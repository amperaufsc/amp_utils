#pragma once

#include <smacc2/smacc.hpp>
#include <lifecycle_msgs/msg/transition.hpp>

#include "../client_behaviors/cb_change_lifecycle.hpp"
#include "../client_behaviors/cb_publish_topic.hpp"
#include <amp_sm/clients/cl_lifecycle_pipeline.hpp>
#include <amp_sm/clients/cl_topic_listener.hpp>

namespace amp_sm
{

struct st_AsEmergency : smacc2::SmaccState<st_AsEmergency, Amp_sm>
{
    using SmaccState::SmaccState;

    static void staticConfigure()
    {
        std::vector<std::string> nodes_to_shutdown = {
            "/check_lifecycle_node",
            "/repeater_node",
            "/perception_lifecycle_node",
            "/disparity_pub_life",
            "/path_node",
            "/yolo_node",
            "/control_node",
            "/mapper_node"
        };

        configure_orthogonal<or_utils, CbChangeLifecycleGroup>(nodes_to_shutdown, 99);
        configure_orthogonal<or_utils, CbPublishEvent>();
    }

    void onEntry()
    {
        RCLCPP_INFO(getLogger(), "Estado Emergency: Disparando comandos de configuração...");
    }

    void onExit()
    {
        RCLCPP_INFO(getLogger(), "Estado Emergency: Saindo do estado...");
    }
};
} // namespace amp_sm