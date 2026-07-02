#pragma once

#include <string>
#include <smacc2/client_bases/smacc_subscriber_client.hpp>
#include <std_msgs/msg/string.hpp>
#include <smacc2/smacc_client.hpp>
#include <std_msgs/msg/bool.hpp>
#include <rclcpp/rclcpp.hpp>


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
        : go_out_received_(false), ready_out_received_(false), go_received_(false), event_triggered_(false)
        {
        }

        void onInitialize() override
        {
            // Subscreve ao tópico /as_amp/mission_select
            sub_go_out_ = getNode()->create_subscription<std_msgs::msg::String>(
                "/as_amp/mission_select", 
                10, 
                std::bind(&ClReadyToDrive::onGoOutCallback, this, std::placeholders::_1)
            );

            // Subscreve ao tópico /as_amp/res/as_ready
            sub_ready_out_ = getNode()->create_subscription<std_msgs::msg::Bool>(
                "/as_amp/res/as_ready", 
                10, 
                std::bind(&ClReadyToDrive::onReadyOutCallback, this, std::placeholders::_1)
            );

            // Subscreve ao tópico /go
            sub_go_ = getNode()->create_subscription<std_msgs::msg::Bool>(
                "/as_amp/res/go", 
                10, 
                std::bind(&ClReadyToDrive::onGoCallback, this, std::placeholders::_1)
            );

            RCLCPP_INFO(getLogger(), "[ClReadyToDrive] Cliente inicializado. A aguardar /as_amp/go_out (Missão), /as_amp/res/as_ready e /as_amp/res/go");
        }

    private:
        // Pointers para os Subscribers (Note a alteração no tipo do sub_go_out_)
        rclcpp::Subscription<std_msgs::msg::String>::SharedPtr sub_go_out_;
        rclcpp::Subscription<std_msgs::msg::Bool>::SharedPtr sub_ready_out_;
        rclcpp::Subscription<std_msgs::msg::Bool>::SharedPtr sub_go_;

        // Variáveis de estado interno
        bool go_out_received_;
        bool ready_out_received_;
        bool go_received_;
        
        // Flag de segurança para não disparar o evento múltiplas vezes sem querer
        bool event_triggered_;

        // Callback para /as_amp/go_out (AGORA AVALIA A STRING)
        void onGoOutCallback(const std_msgs::msg::String::SharedPtr msg)
        {
            std::string missao = msg->data;

            // Verifica se a string recebida é uma das missões válidas
            if (missao == "TRACKDRIVE" || missao == "AUTOCROSS" || 
                missao == "SKIDPAD" || missao == "ACCELERATION")
            {
                go_out_received_ = true;
            }
            else
            {
                go_out_received_ = false;
            }

            checkConditionsAndTrigger();
        }

        // Callback para /as_amp/res/as_ready
        void onReadyOutCallback(const std_msgs::msg::Bool::SharedPtr msg)
        {
            ready_out_received_ = msg->data;
            checkConditionsAndTrigger();
        }

        // Callback para /as_amp/res/go
        void onGoCallback(const std_msgs::msg::Bool::SharedPtr msg)
        {
            go_received_ = msg->data;
            checkConditionsAndTrigger();
        }

        // Função que avalia se todas as condições estão cumpridas
        void checkConditionsAndTrigger()
        {
            // Se todos são true e ainda não disparamos o evento
            if (go_out_received_ && ready_out_received_ && go_received_ && !event_triggered_)
            {
                RCLCPP_INFO(getLogger(), "✅ [ClReadyToDrive] CONDIÇÕES ATINGIDAS: Missão válida, READY_OUT e GO confirmados!");

                // Lança o evento para a Máquina de Estados
                this->postEvent<EvReadyToDrive>();
                
                // Tranca o gatilho para não inundar a state machine se os tópicos continuarem a publicar 'true'
                event_triggered_ = true; 
            }
            else if ((!go_out_received_ || !ready_out_received_ || !go_received_) && event_triggered_)
            {
                // Opcional: Se algum dos sinais cair para falso (0) ou a missão mudar para algo inválido, 
                // "rearmamos" a flag permitindo que o evento seja disparado novamente no futuro se necessário.
                event_triggered_ = false;
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