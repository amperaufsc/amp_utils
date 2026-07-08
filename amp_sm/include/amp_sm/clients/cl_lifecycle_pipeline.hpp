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
        : ClLifecycleInterface("/check_lifecycle_node/change_state")
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

