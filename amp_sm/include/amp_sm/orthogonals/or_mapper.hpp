#pragma once

#include <smacc2/smacc.hpp>
#include <smacc2/client_bases/smacc_service_client.hpp>

#include <lifecycle_msgs/srv/change_state.hpp>

#include <amp_sm/clients/cl_topic_listener.hpp>
#include <amp_sm/clients/cl_lifecycle_monitor.hpp>
#include <amp_sm/clients/cl_lifecycle_pipeline.hpp>

namespace amp_sm
{
class or_mapper : public smacc2::Orthogonal<or_mapper>
{
public:
    void onInitialize() override
    {   
        
        // cliente que assina no serviço de cada nó. Dessa maneira ele consegue controlar o lifecycle.
        this->createClient<amp_sm::ClMapperLifecycle>();        
        
        // lista de nós que fazem parte do subsistema
        std::vector<std::string> nodes = {
            "/mapper_node"
        };

        // cliente que verifica a integridade de todos os nós. Caso algum va para Error ou Desconfigurado ele disparará um evento.
        this->createClient<amp_sm::ClLifecycleMonitor>(nodes);

    }
};
} // namespace amp_sm