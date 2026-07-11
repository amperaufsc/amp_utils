#pragma once

#include <smacc2/smacc.hpp>
#include <smacc2/client_bases/smacc_service_client.hpp>

#include <lifecycle_msgs/srv/change_state.hpp>

#include <amp_sm/clients/cl_topic_listener.hpp>
#include <amp_sm/clients/cl_lifecycle_monitor.hpp>
#include <amp_sm/clients/cl_lifecycle_pipeline.hpp>

#include "std_msgs/msg/u_int8.hpp"
#include <amp_sm/clients/cl_topic_publisher.hpp>


namespace amp_sm
{
class or_utils : public smacc2::Orthogonal<or_utils>
{
public:
    void onInitialize() override
    {   
        // cliente que assina no serviço de cada nó. Dessa maneira ele consegue controlar o lifecycle.
        this->createClient<amp_sm::ClRepeaterLifecycle>();
        this->createClient<amp_sm::ClTopicPublisher<std_msgs::msg::UInt8>>("/as_amp/go/finish");
    
        
        // lista de nós que fazem parte do subsistema
        std::vector<std::string> nodes = {
            "/check_lifecycle_node",
            "/repeater_node"
        };

        // lista de nós que precisam estar ativos ao sair de st_Off.
        std::vector<std::string> on_startup_nodes = {
            "/repeater_node",
            "/perception_lifecycle_node",
            "/control_node",
            "/path_node",
            "/yolo_node",
            "/check_lifecycle_node",
            "/mapper_node",
            "/disparity_pub_life"

            //...
        };

        // cliente que verifica a integridade de todos os nós. Caso algum va para Error ou Desconfigurado ele disparará um evento.
        this->createClient<amp_sm::ClLifecycleMonitor>(nodes);

        // cliente que dispara um Evento (ver quais dentro do cliente) assim que todos os nós estao configurados ou ativados.
        this->createClient<amp_sm::ClLifecycleConsensusMonitor>(on_startup_nodes);

        // listeners
        this->createClient<amp_sm::ClMissionSelectListener>(); // cliente que dispara um Evento quando recebe um "Go".
        this->createClient<amp_sm::ClReadyToDrive>(); // cliente que dispara um Evento quando recebe alguma missao valida & mensagem go do res & mensagem ready do res.
        this->createClient<amp_sm::ClFinishedListener>(); // cliente que dispara um Evento quando recebe a missao foi concluida (mensagem publicada pelo Path Planning).
        this->createClient<amp_sm::ClStopListener>();
    }
};
} // namespace amp_sm