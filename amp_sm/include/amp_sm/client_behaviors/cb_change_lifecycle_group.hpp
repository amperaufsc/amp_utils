#pragma once
#include <smacc2/smacc_client_behavior.hpp>
#include <lifecycle_msgs/srv/change_state.hpp>
#include <thread>
#include <chrono>
#include <future>

namespace amp_sm
{
class CbChangeLifecycleGroup : public smacc2::SmaccClientBehavior
{
public:
    CbChangeLifecycleGroup(const std::vector<std::string> & target_nodes, uint8_t transition_id)
    : target_nodes_(target_nodes), transition_id_(transition_id)
    {
    }

    void onEntry() override
    {
        RCLCPP_INFO(getLogger(), "[CbGroup] Iniciando transicao %d em CASCATA para %zu nos...", 
                    transition_id_, target_nodes_.size());

        // Usamos std::async para não travar a Máquina de Estados
        // std::launch::async força a criação de uma thread no background
        execution_future_ = std::async(std::launch::async, [this]() {
            this->executeSequence();
        });
    }

private:
    std::vector<std::string> target_nodes_;
    uint8_t transition_id_;
    
    // Mantemos o future para a thread não morrer prematuramente
    std::future<void> execution_future_;

    void executeSequence()
    {
        auto node = getNode();
        
        for (const auto & target : target_nodes_)
        {
            auto client = node->create_client<lifecycle_msgs::srv::ChangeState>(target + "/change_state");
            
            // Damos até 1.5 segundos para o serviço responder (sem pressa)
            if (client->wait_for_service(std::chrono::milliseconds(1500)))
            {
                auto request = std::make_shared<lifecycle_msgs::srv::ChangeState::Request>();
                request->transition.id = transition_id_;
                
                client->async_send_request(request);
                RCLCPP_INFO(getLogger(), "[CbGroup] Comando enviado para: %s", target.c_str());
            }
            else
            {
                RCLCPP_WARN(getLogger(), "[CbGroup] ❌ SERVICO INACESSIVEL: %s", target.c_str());
            }

            // O SEGREDINHO: Espera 150ms antes de pedir ao próximo nó!
            // Isso evita o pico no FastDDS e no processador.
            std::this_thread::sleep_for(std::chrono::milliseconds(150));
        }
        
        RCLCPP_INFO(getLogger(), "[CbGroup] Fim da cascata de transicao.");
    }
};
} // namespace amp_sm