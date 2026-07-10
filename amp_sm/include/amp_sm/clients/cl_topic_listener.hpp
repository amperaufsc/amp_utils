#pragma once

#include <string>
#include <smacc2/client_bases/smacc_subscriber_client.hpp>
#include <std_msgs/msg/string.hpp>
#include <smacc2/smacc_client.hpp>
#include <std_msgs/msg/bool.hpp>
#include <rclcpp/rclcpp.hpp>
#include <fs_msgs/msg/go_signal.hpp>
#include "std_msgs/msg/u_int8.hpp"


namespace amp_sm
{

    struct EvReadyToDrive : boost::statechart::event<EvReadyToDrive>{};
    struct EvCheckListener : boost::statechart::event<EvCheckListener>{};
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
            : smacc2::client_bases::SmaccSubscriberClient<std_msgs::msg::String>("/as_amp/mission_select")
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
            if (msg.data == "CALIBRATION")
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

    class ClReadyToDrive : public smacc2::ISmaccClient
    {
    public:
        ClReadyToDrive()
        : event_triggered_(false)
        {
        }

        void onInitialize() override
        {
            // Subscreve apenas ao tópico unificado que vem do nó Repeater
            sub_go_signal_ = getNode()->create_subscription<fs_msgs::msg::GoSignal>(
                "/as_amp/mission_selected/go", 
                10, 
                std::bind(&ClReadyToDrive::onGoSignalCallback, this, std::placeholders::_1)
            );

            RCLCPP_INFO(getLogger(), "[ClReadyToDrive] Inicializado. Aguardando GoSignal em /as_amp/mission_selected/go");
        }

    private:
        // O Subscriber agora usa o tipo GoSignal
        rclcpp::Subscription<fs_msgs::msg::GoSignal>::SharedPtr sub_go_signal_;

        // Flag de segurança para não disparar o evento múltiplas vezes
        bool event_triggered_;

        // Callback simplificado: Se a mensagem chegou, é porque o nó Repeater já validou tudo!
        void onGoSignalCallback(const fs_msgs::msg::GoSignal::SharedPtr msg)
        {
            if (!event_triggered_)
            {
                RCLCPP_INFO(getLogger(), "✅ [ClReadyToDrive] GoSignal recebido para a missao: [%s]!", msg->mission.c_str());
                
                // Lança o evento para a Máquina de Estados transicionar
                this->postEvent<EvReadyToDrive>();
                
                // Tranca o gatilho
                event_triggered_ = true; 
            }
        }
    };

    class ClStopListener : public smacc2::client_bases::SmaccSubscriberClient<std_msgs::msg::UInt8>
    {
    public:
        ClStopListener()
            : smacc2::client_bases::SmaccSubscriberClient<std_msgs::msg::UInt8>("/as_amp/res/as_emergency")
        {
        }

        void onInitialize() override
        {
            // 1. Atualiza a chamada do método da classe base para usar UInt8
            smacc2::client_bases::SmaccSubscriberClient<std_msgs::msg::UInt8>::onInitialize();

            // Faz o bind do callback
            this->onMessageReceived(&ClStopListener::messageCallback, this);
        }

    private:
        // 2. Altera o tipo do parâmetro que a função recebe
        void messageCallback(const std_msgs::msg::UInt8 &msg)
        {
            // 3. Verifica se o valor numérico é 1
            if (msg.data == 1)
            {
                RCLCPP_INFO(
                    getLogger(),
                    "[ClStopListener] Comando Stop recebido (UInt8 = 1)! Disparando evento...");

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