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

// Certifique-se de que esses eventos estão declarados no seu arquivo de eventos principal
struct EvAllNodesConfigured;
struct EvNodeCrashed;

class CbChangeLifecycleGroup : public smacc2::SmaccClientBehavior
{
public:
    CbChangeLifecycleGroup(const std::vector<std::string> & target_nodes, uint8_t transition_id)
    : target_nodes_(target_nodes), transition_id_(transition_id)
    {
    }

    void onEntry() override
    {
        RCLCPP_INFO(getLogger(), "[CbGroup] Iniciando transicao (ID: %d) em CASCATA para %zu nos...",
                    transition_id_, target_nodes_.size());

        // Lança a execução assíncrona para não travar a SMACC2
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
        
        // Define se estamos no modo rigoroso (configuração) ou trator (shutdown)
        bool is_force_shutdown = (transition_id_ == 99); 

        for (const auto & target : target_nodes_)
        {
            uint8_t actual_id_to_send = transition_id_;

            // 1. Verifica o estado atual do nó
            NodeCheckResult check = checkNodeState(node, target, actual_id_to_send);

            if (check == NodeCheckResult::ERROR)
            {
                if (is_force_shutdown) {
                    RCLCPP_WARN(getLogger(), "[CbGroup] ⚠️ %s morto ou inalcancavel. Pulando para o proximo.", target.c_str());
                    continue; // Shutdown trator: ignora e avança
                } else {
                    RCLCPP_ERROR(getLogger(), "[CbGroup] ❌ Nao foi possivel verificar %s. Abortando cascata.", target.c_str());
                    this->postEvent<amp_sm::EvNodeCrashed>();
                    return; // Configuração estrita: aborta tudo
                }
            }

            if (check == NodeCheckResult::SKIP)
            {
                RCLCPP_INFO(getLogger(), "[CbGroup] ⏭️ %s ja esta no estado desejado.", target.c_str());
                continue;
            }

            // 2. Envia o comando de transição
            bool ok = sendAndConfirmTransition(node, target, actual_id_to_send);
            if (!ok)
            {
                if (is_force_shutdown) {
                    RCLCPP_WARN(getLogger(), "[CbGroup] ⚠️ %s falhou ao transicionar. Pulando para o proximo.", target.c_str());
                    continue; // Shutdown trator: ignora e avança
                } else {
                    RCLCPP_ERROR(getLogger(), "[CbGroup] ❌ Falha na transicao de %s. Abortando cascata.", target.c_str());
                    this->postEvent<amp_sm::EvNodeCrashed>();
                    return; // Configuração estrita: aborta tudo
                }
            }

            RCLCPP_INFO(getLogger(), "[CbGroup] ✅ %s confirmado no novo estado.", target.c_str());
        }

        RCLCPP_INFO(getLogger(), "[CbGroup] Cascata concluida com sucesso.");
        this->postEvent<amp_sm::EvAllNodesConfigured>();
    }

    NodeCheckResult checkNodeState(rclcpp::Node::SharedPtr node, const std::string & target, uint8_t & actual_id)
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

                // --- MODO SHUTDOWN INTELIGENTE ---
                if (actual_id == 99)
                {
                    if (current_state == "finalized") return NodeCheckResult::SKIP;

                    // Ajusta o ID de acordo com a posição do nó no lifecycle
                    if (current_state == "active") actual_id = lifecycle_msgs::msg::Transition::TRANSITION_ACTIVE_SHUTDOWN;
                    else if (current_state == "inactive") actual_id = lifecycle_msgs::msg::Transition::TRANSITION_INACTIVE_SHUTDOWN;
                    else if (current_state == "unconfigured") actual_id = lifecycle_msgs::msg::Transition::TRANSITION_UNCONFIGURED_SHUTDOWN;

                    return NodeCheckResult::TRANSITION;
                }

                // --- MODO CONFIGURAÇÃO ESTREITA (IDs 1, 2, 3, 4) ---
                if (actual_id == lifecycle_msgs::msg::Transition::TRANSITION_CONFIGURE &&
                    (current_state == "inactive" || current_state == "active"))
                    return NodeCheckResult::SKIP;

                if (actual_id == lifecycle_msgs::msg::Transition::TRANSITION_ACTIVATE &&
                    current_state == "active")
                    return NodeCheckResult::SKIP;

                if (actual_id == lifecycle_msgs::msg::Transition::TRANSITION_DEACTIVATE &&
                    (current_state == "inactive" || current_state == "unconfigured"))
                    return NodeCheckResult::SKIP;

                if (actual_id == lifecycle_msgs::msg::Transition::TRANSITION_CLEANUP &&
                    current_state == "unconfigured")
                    return NodeCheckResult::SKIP;

                return NodeCheckResult::TRANSITION;
            }

            std::this_thread::sleep_for(std::chrono::milliseconds(50));
        }

        return NodeCheckResult::ERROR;
    }

    bool sendAndConfirmTransition(rclcpp::Node::SharedPtr node, const std::string & target, uint8_t actual_id)
    {
        auto client_change = node->create_client<lifecycle_msgs::srv::ChangeState>(target + "/change_state");

        if (!client_change->wait_for_service(std::chrono::seconds(3)))
        {
            RCLCPP_ERROR(getLogger(), "[CbGroup] Servico change_state inacessivel: %s", target.c_str());
            return false;
        }

        auto request = std::make_shared<lifecycle_msgs::srv::ChangeState::Request>();
        request->transition.id = actual_id;

        auto future = client_change->async_send_request(request);

        // Timeout generoso de 10s (caso o YOLO ou os sensores demorem para subir na RAM)
        auto status = future.wait_for(std::chrono::seconds(10));
        if (status != std::future_status::ready)
        {
            RCLCPP_ERROR(getLogger(), "[CbGroup] Timeout esperando resposta de change_state: %s", target.c_str());
            return false;
        }

        auto response = future.get();
        if (!response->success)
        {
            RCLCPP_ERROR(getLogger(), "[CbGroup] %s recusou a transicao (callback do nó retornou false).", target.c_str());
            return false;
        }

        return true;
    }
};
} // namespace amp_sm