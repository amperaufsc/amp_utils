#pragma once

#include <map>
#include <string>
#include <vector>
#include <std_msgs/msg/string.hpp>
#include <smacc2/smacc_client.hpp>
#include <lifecycle_msgs/msg/transition_event.hpp>
#include <sensor_msgs/msg/image.hpp>

namespace amp_sm
{

struct EvNodeActivated   : boost::statechart::event<EvNodeActivated> {};
struct EvNodeDeactivated : boost::statechart::event<EvNodeDeactivated> {};
struct EvNodeCrashed     : boost::statechart::event<EvNodeCrashed> {};

struct EvAllNodesConfigured : boost::statechart::event<EvAllNodesConfigured> {};
struct EvAllNodesInactive   : boost::statechart::event<EvAllNodesInactive> {};
struct EvAllNodesActivated  : boost::statechart::event<EvAllNodesActivated> {};

class ClLifecycleMonitor : public smacc2::ISmaccClient
{
public:
    ClLifecycleMonitor(const std::vector<std::string> & target_nodes)
    : node_names_(target_nodes)
    {
    }

    void onInitialize() override
    {
        alert_pub_ = getNode()->create_publisher<std_msgs::msg::String>("/as_amp/shutdown", 10);

        for (const std::string & name : node_names_)
        {
            std::string topic_name = name + "/transition_event";

            auto sub = getNode()->create_subscription<lifecycle_msgs::msg::TransitionEvent>(
                topic_name, 10,
                [this, name](const lifecycle_msgs::msg::TransitionEvent::SharedPtr msg) {
                    this->messageCallback(msg, name);
                }
            );
            subs_.push_back(sub);
        }
    }

private:
    std::vector<std::string> node_names_;
    std::vector<rclcpp::Subscription<lifecycle_msgs::msg::TransitionEvent>::SharedPtr> subs_;    
    rclcpp::Publisher<std_msgs::msg::String>::SharedPtr alert_pub_;

    void messageCallback(const lifecycle_msgs::msg::TransitionEvent::SharedPtr msg, const std::string & node_name)
    {
        std::string novo_estado = msg->goal_state.label;
        std::string gatilho = msg->transition.label;

        RCLCPP_INFO(getLogger(), "[Monitor Individual -> %s] mudou para o estado: %s", 
                    node_name.c_str(), novo_estado.c_str());

        if (novo_estado == "active")
        {
            this->postEvent<EvNodeActivated>();
        }
        else if (novo_estado == "inactive")
        {
            this->postEvent<EvNodeDeactivated>();
        }
        else if (novo_estado == "finalized" || novo_estado == "unconfigured" || novo_estado == "errorprocessing")
        {
            RCLCPP_ERROR(getLogger(), "🚨 FALHA CRÍTICA: [%s] derrubado por [%s]", node_name.c_str(), gatilho.c_str());

            std_msgs::msg::String alert_msg;
            alert_msg.data = node_name;
            
            alert_pub_->publish(alert_msg);

            this->postEvent<EvNodeCrashed>(); 
        }
    }
};

class ClLifecycleConsensusMonitor : public smacc2::ISmaccClient
{
public:
    ClLifecycleConsensusMonitor(const std::vector<std::string> & target_nodes)
    : node_names_(target_nodes)
    {
    }

    void onInitialize() override
    {
        shutdown_pub_ = getNode()->create_publisher<std_msgs::msg::String>("/as_amp/shutdown", 10);

        for (const std::string & name : node_names_)
        {
            node_states_[name] = "unknown";

            std::string topic_name = name + "/transition_event";
            auto sub = getNode()->create_subscription<lifecycle_msgs::msg::TransitionEvent>(
                topic_name, 10,
                [this, name](const lifecycle_msgs::msg::TransitionEvent::SharedPtr msg) {
                    this->messageCallback(msg, name);
                }
            );
            subs_.push_back(sub);
        }
    }

private:
    std::vector<std::string> node_names_;
    std::vector<rclcpp::Subscription<lifecycle_msgs::msg::TransitionEvent>::SharedPtr> subs_;
    std::map<std::string, std::string> node_states_;
    rclcpp::Publisher<std_msgs::msg::String>::SharedPtr shutdown_pub_;

    void messageCallback(const lifecycle_msgs::msg::TransitionEvent::SharedPtr msg, const std::string & node_name)
    {
        std::string novo_estado = msg->goal_state.label;
        std_msgs::msg::String alert_msg;
        
        node_states_[node_name] = novo_estado;

        RCLCPP_INFO(getLogger(), "✅ No %s: Novo estado: %s", node_name.c_str(), novo_estado.c_str());

        if (novo_estado == "errorprocessing" || novo_estado == "finalized")
        {   
            RCLCPP_ERROR(getLogger(), "🚨 No %s: Falha ao ir para %s 🚨", node_name.c_str(), novo_estado.c_str());
            alert_msg.data = node_name;
            shutdown_pub_->publish(alert_msg);
            this->postEvent<EvNodeCrashed>();
            return;
        }

        checkConsensus();
    }

    void checkConsensus()
    {
        bool all_configured = true;
        bool all_activated = true;
        bool all_inactive = true;

        for (const auto & pair : node_states_)
        {
            if (pair.second != "inactive") 
            {
                all_configured = false;
                all_inactive = false;
            }
            if (pair.second != "active") 
            {
                all_activated = false;
            }
        }

        if (all_configured)
        {
            RCLCPP_INFO(getLogger(), " [Consenso] SUCESSO! Todos os nos estao CONFIGURADOS na memoria.");
            this->postEvent<EvAllNodesConfigured>();
        }
        
        if (all_activated)
        {
            RCLCPP_INFO(getLogger(), " [Consenso] SUCESSO! Todos os nos estao ATIVADOS a 100%%.");
            this->postEvent<EvAllNodesActivated>();
        }

        if (all_inactive)
        {
            RCLCPP_INFO(getLogger(), " [Consenso] SUCESSO! Todos os nos estao INATIVOS.");
            this->postEvent<EvAllNodesInactive>();
        }
    }
};

class ClCameraWatchdog : public smacc2::ISmaccClient
{
public:
    ClCameraWatchdog(const std::vector<std::string> & target_topics, double timeout_sec = 3.0)
    : target_topics_(target_topics), timeout_sec_(timeout_sec)
    {
    }

    void onInitialize() override
    {   
        shutdown_pub_ = getNode()->create_publisher<std_msgs::msg::String>("/as_amp/shutdown", 10);
        rclcpp::Time now = getNode()->now();

        auto qos = rclcpp::SensorDataQoS();
        qos.keep_last(1);

        for (const std::string & topic : target_topics_)
        {
            last_msg_times_[topic] = now;
            is_crashed_[topic] = false;

            auto sub = getNode()->create_subscription<sensor_msgs::msg::Image>(
                topic, qos,
                [this, topic](const sensor_msgs::msg::Image::SharedPtr) {
                    this->last_msg_times_[topic] = this->getNode()->now();
                }
            );
            subs_.push_back(sub);
            
            RCLCPP_INFO(getLogger(), "[Watchdog] A vigiar %s", topic.c_str());
        }

        timer_ = getNode()->create_wall_timer(
            std::chrono::milliseconds(500),
            std::bind(&ClCameraWatchdog::checkTimeout, this)
        );
    }

private:
    std::vector<std::string> target_topics_;
    double timeout_sec_;
    std::vector<rclcpp::Subscription<sensor_msgs::msg::Image>::SharedPtr> subs_;
    std::map<std::string, rclcpp::Time> last_msg_times_;
    std::map<std::string, bool> is_crashed_;
    rclcpp::TimerBase::SharedPtr timer_;
    rclcpp::Publisher<std_msgs::msg::String>::SharedPtr shutdown_pub_;

    void checkTimeout()
    {
        rclcpp::Time now = getNode()->now();

        for (const std::string & topic : target_topics_)
        {
            if (is_crashed_[topic]) continue;

            double elapsed_time = (now - last_msg_times_[topic]).seconds();

            if (elapsed_time > timeout_sec_)
            {
                std_msgs::msg::String msg;
                msg.data = "Camera Watchdog";

                if (shutdown_pub_) shutdown_pub_->publish(msg);
                
                RCLCPP_ERROR(getLogger(), "🚨 %s WATCHDOG: SINAL PERDIDO!", topic.c_str());

                is_crashed_[topic] = true;
                this->postEvent<EvNodeCrashed>();
            }
        }
    }
};

}