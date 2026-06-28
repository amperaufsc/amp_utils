#pragma once

#include <smacc2/smacc_client.hpp>
#include <lifecycle_msgs/srv/change_state.hpp>
#include <sensor_msgs/msg/image.hpp>
#include <map>
#include <string>
#include <vector>
#include <memory>
#include <smacc2/client_bases/smacc_service_client.hpp>


namespace amp_sm
{

//
// Utils
//
class ClLifecycleInterface : public smacc2::client_bases::SmaccServiceClient<lifecycle_msgs::srv::ChangeState>
{
public:
    // O construtor recebe o nome do serviço do nó e repassa para o SMACC2
    ClLifecycleInterface(std::string service_name) 
        : smacc2::client_bases::SmaccServiceClient<lifecycle_msgs::srv::ChangeState>(service_name)
    {
    }

    // A PORTA PÚBLICA: Pega o pedido do Behavior e envia para a rede ROS 2 de forma assíncrona
    void async_change_state(std::shared_ptr<lifecycle_msgs::srv::ChangeState::Request> request)
    {
        if (this->client_ != nullptr)
        {
            // async_send_request não trava a Thread, resolvendo o problema do Deadlock!
            this->client_->async_send_request(request);
        }
        else
        {
            RCLCPP_ERROR(getLogger(), "[ClLifecycleInterface] Falha Crítica: client_ ROS 2 não inicializado!");
        }
    }
};

class ClCheckLifecycle : public ClLifecycleInterface
{
public:
    // 2. Fica minúsculo: apenas repassa a string de destino para a classe mãe
    ClCheckLifecycle() 
        : ClLifecycleInterface("/check_node_lifecycle/change_state")
    {
    }
};
class ClRepeaterLifecycle : public ClLifecycleInterface
{
public:
    // 2. Fica minúsculo: apenas repassa a string de destino para a classe mãe
    ClRepeaterLifecycle() 
        : ClLifecycleInterface("/repeater_node/change_state")
    {
    }
};
//
//

//
// Perception
//
class ClPerceptionLifecycle : public ClLifecycleInterface
{
public:
    // 2. Fica minúsculo: apenas repassa a string de destino para a classe mãe
    ClPerceptionLifecycle() 
        : ClLifecycleInterface("/perception_lifecycle_node/change_state")
    {
    }
};

class ClCameraWatchdog : public smacc2::ISmaccClient
{
public:
    // O construtor recebe a lista de tópicos e o tempo máximo tolerado sem sinal (ex: 2.0 segundos)
    ClCameraWatchdog(const std::vector<std::string> & target_topics, double timeout_sec = 3.0)
    : target_topics_(target_topics), timeout_sec_(timeout_sec)
    {
    }

    void onInitialize() override
    {
        // Tempo inicial (dá uma folga durante o boot do sistema)
        rclcpp::Time now = getNode()->now();

        // 1. QoS de Sensor: Vital para não encher a RAM da Máquina de Estados com imagens!
        auto qos = rclcpp::SensorDataQoS();
        qos.keep_last(1);

        // 2. Cria os subscribers para cada câmara
        for (const std::string & topic : target_topics_)
        {
            last_msg_times_[topic] = now;
            is_crashed_[topic] = false;

            auto sub = getNode()->create_subscription<sensor_msgs::msg::Image>(
                topic, qos,
                [this, topic](const sensor_msgs::msg::Image::SharedPtr /*msg*/) {
                    // Sempre que chega uma imagem, "resetamos" o relógio deste tópico específico
                    this->last_msg_times_[topic] = this->getNode()->now();
                }
            );
            subs_.push_back(sub);
            
            RCLCPP_INFO(getLogger(), "[Watchdog] A vigiar o batimento cardíaco de: %s", topic.c_str());
        }

        // 3. Cria o Timer que atua como o juiz (Roda a cada 500 milissegundos)
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
    std::map<std::string, bool> is_crashed_; // Impede spam infinito de erros
    rclcpp::TimerBase::SharedPtr timer_;

    void checkTimeout()
    {
        rclcpp::Time now = getNode()->now();

        for (const std::string & topic : target_topics_)
        {
            // Se já acusou erro antes, ignora para não floodar a rede com milhares de eventos
            if (is_crashed_[topic]) continue;

            // Calcula quantos segundos se passaram desde a última imagem
            double elapsed_time = (now - last_msg_times_[topic]).seconds();

            if (elapsed_time > timeout_sec_)
            {
                RCLCPP_ERROR(getLogger(), "\n=======================================================");
                RCLCPP_ERROR(getLogger(), "🚨 WATCHDOG DA VISÃO: SINAL PERDIDO! 🚨");
                RCLCPP_ERROR(getLogger(), "O tópico [%s] não envia imagens há %.2f segundos.", topic.c_str(), elapsed_time);
                RCLCPP_ERROR(getLogger(), "Possível falha de cabo ou travagem da OAK-D. Disparando EvNodeCrashed!");
                RCLCPP_ERROR(getLogger(), "=======================================================\n");

                // Marca como crashado para não repetir
                is_crashed_[topic] = true;
                
                // Dispara o evento de falha para a Máquina de Estados abortar e parar o motor
                this->postEvent<EvNodeCrashed>();
            }
        }
    }
};

class ClYoloLifecycle : public ClLifecycleInterface
{
public:
    // 2. Fica minúsculo: apenas repassa a string de destino para a classe mãe
    ClYoloLifecycle() 
        : ClLifecycleInterface("/yolo_node/change_state")
    {
    }
};
//
//

//
// Control
//
class ClCanNodeLifecycle : public ClLifecycleInterface
{
public:
    // 2. Fica minúsculo: apenas repassa a string de destino para a classe mãe
    ClCanNodeLifecycle() 
        : ClLifecycleInterface("/can_node_lifecycle/change_state")
    {
    }
};

class ClControlLifecycle : public ClLifecycleInterface
{
public:
    // 2. Fica minúsculo: apenas repassa a string de destino para a classe mãe
    ClControlLifecycle() 
        : ClLifecycleInterface("/control_node/change_state")
    {
    }
};

class ClPathLifecycle : public ClLifecycleInterface
{
public:
    // 2. Fica minúsculo: apenas repassa a string de destino para a classe mãe
    ClPathLifecycle() 
        : ClLifecycleInterface("/path_node/change_state")
    {
    }
};

//
// Mapper
//

class ClMapperLifecycle : public ClLifecycleInterface
{
public:
    // 2. Fica minúsculo: apenas repassa a string de destino para a classe mãe
    ClMapperLifecycle() 
        : ClLifecycleInterface("/mapper_node/change_state")
    {
    }
};
//
//

} // namespace amp_sm

