#pragma once

#include <smacc2/smacc.hpp>
#include <lifecycle_msgs/msg/transition.hpp>

#include "../client_behaviors/cb_change_lifecycle.hpp"
#include <amp_sm/clients/cl_lifecycle_pipeline.hpp>
#include <amp_sm/clients/cl_topic_listener.hpp>
#include <amp_sm/clients/cl_lifecycle_monitor.hpp>

namespace amp_sm
{
struct st_AsReady;
struct st_AsEmergency;

struct st_AsChecking : smacc2::SmaccState<st_AsChecking, Amp_sm>
{
    using SmaccState::SmaccState;

    typedef boost::mpl::list<
    smacc2::Transition<amp_sm::EvCheckListener, amp_sm::st_AsReady>,
    smacc2::Transition<amp_sm::EvNodeCrashed, amp_sm::st_AsEmergency>,
    smacc2::Transition<amp_sm::EvStopListener, amp_sm::st_AsEmergency>


    > reactions;

    static void staticConfigure()
    {
        // 1. Envia o sinal Activate para o serviço /.../change_state
        configure_orthogonal<or_utils, CbChangeLifecycle<ClCheckLifecycle>>(
            lifecycle_msgs::msg::Transition::TRANSITION_ACTIVATE,
            lifecycle_msgs::msg::Transition::TRANSITION_DEACTIVATE
        );
  }
    
    void onEntry()
    {
        RCLCPP_INFO(getLogger(), "Estado checking: Inicializando...");
    }
    
    void onExit()
    {   
        RCLCPP_INFO(getLogger(), "Saindo do Estado checking...");
    }
};
} // namespace amp_sm