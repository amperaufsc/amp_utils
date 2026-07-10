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

        execution_future_ = std::async(std::launch::async, [this]() {
            this->executeSequence();
        });
    }

private:
    enum class NodeCheckResult { SKIP, TRANSITION, ERROR };

    std::vector<std::string> target_nodes_;
    uint8_t transition_id_;
    std::future<void> execution_future_;

    void executeSequence()
    {
        auto node = getNode();

        for (const auto & target : target_nodes_)
        {
            NodeCheckResult check = checkNodeState(node, target);

            if (check == NodeCheckResult::ERROR)
            {
                RCLCPP_ERROR(getLogger(), "[CbGroup] ❌ Nao foi possivel verificar %s. Abortando cascata.", target.c_str());
                this->postEvent<amp_sm::EvNodeCrashed>();
                return;
            }

            if (check == NodeCheckResult::SKIP)
            {
                RCLCPP_INFO(getLogger(), "[CbGroup] ⏭️ %s ja esta no estado desejado.", target.c_str());
                continue;
            }

            // TRANSITION: envia o comando e ESPERA a confirmação antes de seguir
            bool ok = sendAndConfirmTransition(node, target);
            if (!ok)
            {
                RCLCPP_ERROR(getLogger(), "[CbGroup] ❌ Falha na transicao de %s. Abortando cascata.", target.c_str());
                this->postEvent<amp_sm::EvNodeCrashed>();
                return;
            }

            RCLCPP_INFO(getLogger(), "[CbGroup] ✅ %s confirmado no novo estado. Prosseguindo...", target.c_str());
        }

        RCLCPP_INFO(getLogger(), "[CbGroup] Cascata concluida com sucesso.");
        this->postEvent<amp_sm::EvAllNodesConfigured>();
    }

    // Retorna se precisa transicionar, se já está no estado certo (skip), ou erro de comunicação
    NodeCheckResult checkNodeState(rclcpp::Node::SharedPtr node, const std::string & target)
    {
        auto client_get = node->create_client<lifecycle_msgs::srv::GetState>(target + "/get_state");

        const int max_retries = 40;
        for (int attempt = 1; attempt <= max_retries; ++attempt)
        {
            if (!client_get->wait_for_service(std::chrono::milliseconds(150)))
            {
                std::this_thread::sleep_for(std::chrono::milliseconds(50));
                continue;
            }

            auto request = std::make_shared<lifecycle_msgs::srv::GetState::Request>();
            auto future_result = client_get->async_send_request(request);

            if (future_result.wait_for(std::chrono::milliseconds(500)) == std::future_status::ready)
            {
                auto response = future_result.get();
                std::string current_state = response->current_state.label;

                RCLCPP_INFO(getLogger(), "[CbGroup] %s -> estado atual: [%s]", target.c_str(), current_state.c_str());

                if (transition_id_ == lifecycle_msgs::msg::Transition::TRANSITION_CONFIGURE &&
                    (current_state == "inactive" || current_state == "active"))
                    return NodeCheckResult::SKIP;

                if (transition_id_ == lifecycle_msgs::msg::Transition::TRANSITION_ACTIVATE &&
                    current_state == "active")
                    return NodeCheckResult::SKIP;

                if (transition_id_ == lifecycle_msgs::msg::Transition::TRANSITION_DEACTIVATE &&
                    (current_state == "inactive" || current_state == "unconfigured"))
                    return NodeCheckResult::SKIP;

                if (transition_id_ == lifecycle_msgs::msg::Transition::TRANSITION_CLEANUP &&
                    current_state == "unconfigured")
                    return NodeCheckResult::SKIP;

                return NodeCheckResult::TRANSITION;
            }

            std::this_thread::sleep_for(std::chrono::milliseconds(50));
        }

        // Aqui SIM é um erro real: não conseguimos nem saber o estado do nó
        return NodeCheckResult::ERROR;
    }

    // Envia o change_state e só retorna quando tiver a confirmação (ou falha/timeout)
    bool sendAndConfirmTransition(rclcpp::Node::SharedPtr node, const std::string & target)
    {
        auto client_change = node->create_client<lifecycle_msgs::srv::ChangeState>(target + "/change_state");

        if (!client_change->wait_for_service(std::chrono::seconds(3)))
        {
            RCLCPP_ERROR(getLogger(), "[CbGroup] Servico change_state inacessivel: %s", target.c_str());
            return false;
        }

        auto request = std::make_shared<lifecycle_msgs::srv::ChangeState::Request>();
        request->transition.id = transition_id_;

        auto future = client_change->async_send_request(request);

        // Configure/Activate podem demorar (carregar modelo do YOLO, por ex) - timeout generoso
        auto status = future.wait_for(std::chrono::seconds(10));
        if (status != std::future_status::ready)
        {
            RCLCPP_ERROR(getLogger(), "[CbGroup] Timeout esperando resposta de change_state: %s", target.c_str());
            return false;
        }

        auto response = future.get();
        if (!response->success)
        {
            RCLCPP_ERROR(getLogger(), "[CbGroup] %s recusou a transicao (callback retornou failure/error).", target.c_str());
            return false;
        }

        return true; // sucesso confirmado pelo próprio nó via response->success
    }
};
} // namespace amp_sm