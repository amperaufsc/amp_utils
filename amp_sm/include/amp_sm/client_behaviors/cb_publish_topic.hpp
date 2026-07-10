#pragma once

#include <smacc2/smacc_client_behavior.hpp>
#include "std_msgs/msg/u_int8.hpp"
#include <amp_sm/clients/cl_topic_publisher.hpp> 

namespace amp_sm
{
class CbPublishEvent : public smacc2::SmaccClientBehavior
{
public:
    void onEntry() override
    {
        // 1. Pede ao SMACC2 para alocar o Client AQUI, antes de fazer qualquer coisa
        this->requiresClient(publisher_client_);

        // 2. Agora o ponteiro é seguro para ser utilizado
        if (publisher_client_) {
            std_msgs::msg::UInt8 msg;
            msg.data = 1; // Sinal de finish = 1
            
            publisher_client_->publish(msg);
            RCLCPP_INFO(getLogger(), "[CbPublishEvent] Sinal UInt8 (1) publicado em /as_amp/go/finish!");
        } else {
            RCLCPP_ERROR(getLogger(), "[CbPublishEvent] ❌ ERRO FATAL: publisher_client_ nao foi encontrado no Orthogonal!");
        }
    }

private:
    amp_sm::ClTopicPublisher<std_msgs::msg::UInt8>* publisher_client_{nullptr};
};
} // namespace amp_sm