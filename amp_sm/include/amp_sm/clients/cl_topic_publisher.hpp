#pragma once

#include <string>
#include <smacc2/smacc.hpp>
#include <rclcpp/rclcpp.hpp>

namespace amp_sm
{
template <typename MsgT>
class ClTopicPublisher : public smacc2::ISmaccClient
{
public:
    explicit ClTopicPublisher(const std::string & topic_name, size_t qos_depth = 10)
    : topic_name_(topic_name), qos_depth_(qos_depth)
    {
    }

    void onInitialize() override
    {
        publisher_ = getNode()->create_publisher<MsgT>(topic_name_, qos_depth_);
    }

    void publish(const MsgT & msg)
    {
        if (publisher_)
        {
            publisher_->publish(msg);
        }
        else
        {
            RCLCPP_ERROR(getLogger(), "[ClTopicPublisher] Publisher nao inicializado para %s", topic_name_.c_str());
        }
    }

private:
    std::string topic_name_;
    size_t qos_depth_;
    typename rclcpp::Publisher<MsgT>::SharedPtr publisher_;
};
} // namespace amp_sm