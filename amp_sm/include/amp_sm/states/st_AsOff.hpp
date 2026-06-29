#pragma once

#include <smacc2/smacc.hpp>
#include <lifecycle_msgs/msg/transition.hpp>

#include "../client_behaviors/cb_change_lifecycle_group.hpp"
#include "../client_behaviors/cb_change_lifecycle.hpp"
#include <amp_sm/clients/cl_lifecycle_pipeline.hpp>
#include <amp_sm/clients/cl_topic_listener.hpp>
#include <amp_sm/clients/cl_lifecycle_monitor.hpp>

namespace amp_sm
{
struct st_AsReady;    

struct st_AsOff : smacc2::SmaccState<st_AsOff, Amp_sm>
{
    using SmaccState::SmaccState;

    typedef boost::mpl::list<
        smacc2::Transition<amp_sm::EvAllNodesConfigured, amp_sm::st_AsReady>,
        smacc2::Transition<amp_sm::EvNodeCrashed, amp_sm::st_AsEmergency>,
        smacc2::Transition<amp_sm::EvStopListener, amp_sm::st_AsEmergency>
    > reactions;

    static void staticConfigure()
    {   


    configure_orthogonal<or_utils, CbChangeLifecycle<ClCheckLifecycle>>(
            lifecycle_msgs::msg::Transition::TRANSITION_CONFIGURE
        );
    }

    void onEntry()
    {
        RCLCPP_INFO(getLogger(), "Estado off: Disparando comandos de configuração...");
    }

    void onExit()
    {
        RCLCPP_INFO(getLogger(), "Estado off: Saltando automaticamente para st_AsSetup!");
    }
};
} // namespace amp_sm