#pragma once

#include <vector>
#include <string>
#include <future>
#include <thread>
#include <chrono>

#include "rclcpp/rclcpp.hpp"
#include "smacc2/smacc_client_behavior.hpp"
#include "lifecycle_msgs/srv/change_state.hpp"
#include "lifecycle_msgs/srv/get_state.hpp"

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

        // Usamos std::async para não travar a Máquina de Estados principal
        execution_future_ = std::async(std::launch::async, [this]() {
            this->executeSequence();
        });
    }

private:
    std::vector<std::string> target_nodes_;
    uint8_t transition_id_;
    std::future<void> execution_future_;

    void executeSequence()
    {
        auto node = getNode();
        
        for (const auto & target : target_nodes_)
        {
            // 1. PRIMEIRO PASSO: Consultar o estado atual do nó
            if (isTransitionNecessary(node, target))
            {
                // 2. SE FOR NECESSÁRIO: Enviar o comando de transição
                auto client_change = node->create_client<lifecycle_msgs::srv::ChangeState>(target + "/change_state");
                
                if (client_change->wait_for_service(std::chrono::milliseconds(1500)))
                {
                    auto request = std::make_shared<lifecycle_msgs::srv::ChangeState::Request>();
                    request->transition.id = transition_id_;
                    
                    client_change->async_send_request(request);
                    RCLCPP_INFO(getLogger(), "[CbGroup] Comando [ID: %d] enviado para: %s", transition_id_, target.c_str());
                }
                else
                {
                    RCLCPP_WARN(getLogger(), "[CbGroup] ❌ SERVICO CHANGE_STATE INACESSIVEL: %s", target.c_str());
                }
            }
            
            // Pausa entre os nós para evitar pico no DDS
            std::this_thread::sleep_for(std::chrono::milliseconds(150));
        }
        
        RCLCPP_INFO(getLogger(), "[CbGroup] Fim da cascata de transicao.");
    }

    bool isTransitionNecessary(rclcpp::Node::SharedPtr node, const std::string& target)
    {
        auto client_get = node->create_client<lifecycle_msgs::srv::GetState>(target + "/get_state");
        
        // Verifica se o serviço de consulta de estado está disponível
        if (!client_get->wait_for_service(std::chrono::milliseconds(1000)))
        {
            RCLCPP_WARN(getLogger(), "[CbGroup] ⚠️ Nao consegui consultar o estado de %s. Tentarei transacionar mesmo assim.", target.c_str());
            return true; // Na dúvida, tenta a transição
        }

        auto request = std::make_shared<lifecycle_msgs::srv::GetState::Request>();
        auto future_result = client_get->async_send_request(request);

        // Aguarda a resposta (síncrono na thread de background, seguro aqui)
        if (future_result.wait_for(std::chrono::milliseconds(1000)) == std::future_status::ready)
        {
            auto response = future_result.get();
            std::string current_state = response->current_state.label;
            
            RCLCPP_INFO(getLogger(), "[CbGroup] %s esta no estado: [%s]", target.c_str(), current_state.c_str());

            // --- LÓGICA DE DEFESA ---
            // ID 1: Configure -> Queremos ir para "inactive"
            if (transition_id_ == lifecycle_msgs::msg::Transition::TRANSITION_CONFIGURE) {
                if (current_state == "inactive" || current_state == "active") {
                    RCLCPP_INFO(getLogger(), "[CbGroup] ⏭️ Ignorando CONFIGURE. %s ja esta configurado (%s).", target.c_str(), current_state.c_str());
                    return false;
                }
            }
            // ID 2: Activate -> Queremos ir para "active"
            else if (transition_id_ == lifecycle_msgs::msg::Transition::TRANSITION_ACTIVATE) {
                if (current_state == "active") {
                    RCLCPP_INFO(getLogger(), "[CbGroup] ⏭️ Ignorando ACTIVATE. %s ja esta ativo.", target.c_str());
                    return false;
                }
            }
            // ID 3: Deactivate -> Queremos ir para "inactive"
            else if (transition_id_ == lifecycle_msgs::msg::Transition::TRANSITION_DEACTIVATE) {
                if (current_state == "inactive" || current_state == "unconfigured") {
                    RCLCPP_INFO(getLogger(), "[CbGroup] ⏭️ Ignorando DEACTIVATE. %s ja esta inativo/desconfigurado (%s).", target.c_str(), current_state.c_str());
                    return false;
                }
            }
            // ID 4: Cleanup -> Queremos ir para "unconfigured"
            else if (transition_id_ == lifecycle_msgs::msg::Transition::TRANSITION_CLEANUP) {
                if (current_state == "unconfigured") {
                    RCLCPP_INFO(getLogger(), "[CbGroup] ⏭️ Ignorando CLEANUP. %s ja esta desconfigurado.", target.c_str());
                    return false;
                }
            }
        }
        else
        {
             RCLCPP_WARN(getLogger(), "[CbGroup] Timeout ao ler estado de %s. Tentarei transacionar.", target.c_str());
        }

        // Se o estado for inválido ou não corresponder à verificação de proteção, envia a transição
        return true; 
    }
};
} // namespace amp_sm