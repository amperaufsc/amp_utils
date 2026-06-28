#pragma once

#include <smacc2/smacc.hpp>
#include <smacc2/client_bases/smacc_service_client.hpp>

#include <lifecycle_msgs/srv/change_state.hpp>

#include <amp_sm/clients/cl_topic_listener.hpp>
#include <amp_sm/clients/cl_lifecycle_monitor.hpp>
#include <amp_sm/clients/cl_lifecycle_pipeline.hpp>

namespace amp_sm
{
class or_utils : public smacc2::Orthogonal<or_utils>
{
public:
    void onInitialize() override
    {   
        // cliente que assina no serviço de cada nó. Dessa maneira ele consegue controlar o lifecycle.
        this->createClient<amp_sm::ClRepeaterLifecycle>();

        
        // lista de nós que fazem parte do subsistema
        std::vector<std::string> nodes = {
            "/check_node_lifecycle"
        };

        // lista de nós que precisam estar ativos ao sair de st_Off.
        std::vector<std::string> on_startup_nodes = {
            "/check_node_lifecycle"
            //...
        };

        // cliente que verifica a integridade de todos os nós. Caso algum va para Error ou Desconfigurado ele disparará um evento.
        this->createClient<amp_sm::ClLifecycleMonitor>(nodes);

        // cliente que dispara um Evento (ver quais dentro do cliente) assim que todos os nós estao configurados ou ativados.
        this->createClient<amp_sm::ClLifecycleConsensusMonitor>(on_startup_nodes);

        // listeners
        this->createClient<amp_sm::ClMissionSelectListener>(); // cliente que dispara um Evento quando recebe um "Go".
        this->createClient<amp_sm::ClGoListener>(); // cliente que dispara um Evento quando recebe alguma missao valida.
        this->createClient<amp_sm::ClFinishedListener>(); // cliente que dispara um Evento quando recebe a missao foi concluida (mensagem publicada pelo Path Planning).
    }
};
} // namespace amp_sm