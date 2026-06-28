#pragma once

#include <smacc2/smacc.hpp>
#include <lifecycle_msgs/srv/change_state.hpp>

namespace amp_sm
{
template <typename TClient>
class CbChangeLifecycle : public smacc2::SmaccClientBehavior
{
private:
    TClient* lifecycle_client_;
    uint8_t entry_transition_;
    uint8_t exit_transition_;
    bool has_exit_transition_;

public:
    // Aceita apenas 1 comando (só executa ao entrar no estado)
    CbChangeLifecycle(uint8_t entry_transition) 
    {
        entry_transition_ = entry_transition;
        has_exit_transition_ = false;
    }

    // Aceita 2 comandos (executa um ao entrar, e outro ao sair)
    CbChangeLifecycle(uint8_t entry_transition, uint8_t exit_transition) 
    {
        entry_transition_ = entry_transition;
        exit_transition_ = exit_transition;
        has_exit_transition_ = true;
    }

    void onEntry() override
    {
        this->requiresClient(lifecycle_client_);

        if (lifecycle_client_ != nullptr)
        {
            RCLCPP_INFO(getLogger(), "[CbChangeLifecycle] ENTRADA: Comando ID %d (Assíncrono)", entry_transition_);
            auto request = std::make_shared<lifecycle_msgs::srv::ChangeState::Request>();
            request->transition.id = entry_transition_;
            
            // ATENÇÃO AQUI: Usa a porta assíncrona, não trava o carro!
            lifecycle_client_->async_change_state(request);
        }
    }

    void onExit() override 
    {
        if (has_exit_transition_ && lifecycle_client_ != nullptr)
        {
            RCLCPP_INFO(getLogger(), "[CbChangeLifecycle] SAÍDA: Comando ID %d (Assíncrono)", exit_transition_);
            auto request = std::make_shared<lifecycle_msgs::srv::ChangeState::Request>();
            request->transition.id = exit_transition_;
            
            // ATENÇÃO AQUI: Manda desligar e não espera resposta! Evita Deadlock!
            lifecycle_client_->async_change_state(request);
        }
    }
};
} // namespace amp_sm