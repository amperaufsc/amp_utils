#pragma once

#include <smacc2/client_bases/smacc_subscriber_client.hpp>
#include <std_msgs/msg/string.hpp>

namespace amp_sm
{

    struct EvGoListener : boost::statechart::event<EvGoListener>{};
    struct EvCheckListener : boost::statechart::event<EvCheckListener>{};
    struct EvMissionSelectListener : boost::statechart::event<EvMissionSelectListener>{};
    struct EvSaltoAutomatico : boost::statechart::event<EvSaltoAutomatico>{};
    struct EvCalibrationListener : boost::statechart::event<EvCalibrationListener>{};
    struct EvStopListener : boost::statechart::event<EvStopListener>{};
    struct EvFinishedListener : boost::statechart::event<EvFinishedListener>{};


    //
    // Utils
    //
    class ClMissionSelectListener : public smacc2::client_bases::SmaccSubscriberClient<std_msgs::msg::String>
    {
    public:
        ClMissionSelectListener()
            : smacc2::client_bases::SmaccSubscriberClient<std_msgs::msg::String>("/can/autonomous_mode")
        {
        }

        void onInitialize() override
        {
            smacc2::client_bases::SmaccSubscriberClient<std_msgs::msg::String>::onInitialize();

            // Atualizado para o novo nome da classe
            this->onMessageReceived(&ClMissionSelectListener::messageCallback, this);
        }

    private:
        void messageCallback(const std_msgs::msg::String &msg)
        {
            if (msg.data == "SKIDPAD" || msg.data == "ACCELERATION" || msg.data == "trackdrive" || msg.data == "AUTOCROSS")
            {
                RCLCPP_INFO(
                    getLogger(), 
                    "[ClTopicListener] Comando MISSION_SELECT recebido! Disparando evento..."
                );
                this->postEvent<EvMissionSelectListener>();
            }
            else if (msg.data == "CALIBRATION")
            {
                RCLCPP_INFO(
                    getLogger(), 
                    "[ClTopicListener] Comando CALIBRATION recebido! Disparando evento..."
                );
                this->postEvent<EvCalibrationListener>();
            }
            else if (msg.data == "CHECK")
            {
                RCLCPP_INFO(
                    getLogger(), 
                    "[ClTopicListener] Comando CHECK recebido! Disparando evento..."
                );
                this->postEvent<EvCheckListener>();
            }
        }
    };

    class ClGoListener : public smacc2::client_bases::SmaccSubscriberClient<std_msgs::msg::String>
    {
    public:
        ClGoListener()
            : smacc2::client_bases::SmaccSubscriberClient<std_msgs::msg::String>("/as_amp/go")
        {
        }

        void onInitialize() override
        {
            smacc2::client_bases::SmaccSubscriberClient<std_msgs::msg::String>::onInitialize();

            // Atualizado para o novo nome da classe
            this->onMessageReceived(&ClGoListener::messageCallback, this);
        }

    private:
        void messageCallback(const std_msgs::msg::String &msg)
        {
            if (msg.data == "GO")
            {
                RCLCPP_INFO(
                    getLogger(),
                    "[ClTopicListener] Comando Go recebido! Disparando evento...");

                this->postEvent<EvGoListener>();
            }
        }
    };
    class ClStopListener : public smacc2::client_bases::SmaccSubscriberClient<std_msgs::msg::String>
    {
    public:
        ClStopListener()
            : smacc2::client_bases::SmaccSubscriberClient<std_msgs::msg::String>("/as_amp/stop")
        {
        }

        void onInitialize() override
        {
            smacc2::client_bases::SmaccSubscriberClient<std_msgs::msg::String>::onInitialize();

            // Atualizado para o novo nome da classe
            this->onMessageReceived(&ClStopListener::messageCallback, this);
        }

    private:
        void messageCallback(const std_msgs::msg::String &msg)
        {
            if (msg.data == "STOP")
            {
                RCLCPP_INFO(
                    getLogger(),
                    "[ClTopicListener] Comando Stop recebido! Disparando evento...");

                this->postEvent<EvStopListener>();
            }
        }
    };
    class ClFinishedListener : public smacc2::client_bases::SmaccSubscriberClient<std_msgs::msg::String>
    {
    public:
        ClFinishedListener()
            : smacc2::client_bases::SmaccSubscriberClient<std_msgs::msg::String>("/as_amp/finished")
        {
        }

        void onInitialize() override
        {
            smacc2::client_bases::SmaccSubscriberClient<std_msgs::msg::String>::onInitialize();

            // Atualizado para o novo nome da classe
            this->onMessageReceived(&ClFinishedListener::messageCallback, this);
        }

    private:
        void messageCallback(const std_msgs::msg::String &msg)
        {
            if (msg.data == "FINISHED")
            {
                RCLCPP_INFO(
                    getLogger(),
                    "[ClTopicListener] Comando Finished recebido! Disparando evento...");

                this->postEvent<EvFinishedListener>();
            }
        }
    };
    //
    //
    
} // namespace amp_sm