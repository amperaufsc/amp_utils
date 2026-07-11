#pragma once

#include <smacc2/smacc.hpp>
#include <lifecycle_msgs/msg/transition.hpp>

#include "../client_behaviors/cb_change_lifecycle.hpp"
#include <amp_sm/clients/cl_lifecycle_pipeline.hpp>
#include <amp_sm/clients/cl_topic_listener.hpp>
#include <amp_sm/clients/cl_lifecycle_monitor.hpp>

// #include "../client_behavior/..." // Substitua pelo cliente real que você quer configurar primeiro

namespace amp_sm
{
struct st_AsFinished;
struct st_AsEmergency;

struct st_AsDriving : smacc2::SmaccState<st_AsDriving, Amp_sm>
{
    using SmaccState::SmaccState;

    typedef boost::mpl::list<
    smacc2::Transition<amp_sm::EvFinishedListener, amp_sm::st_AsFinished>,
    smacc2::Transition<amp_sm::EvNodeCrashed, amp_sm::st_AsEmergency>,
    smacc2::Transition<amp_sm::EvStopListener, amp_sm::st_AsEmergency>
    > reactions;

    static void staticConfigure()
    {
        configure_orthogonal<or_utils, CbChangeLifecycle<ClMapperLifecycle>>(
            lifecycle_msgs::msg::Transition::TRANSITION_ACTIVATE
        );
  }
    
    void onEntry()
    {
        RCLCPP_INFO(getLogger(), "Estado driving: Verificando o sistema...");
    }
};
} // namespace amp_sm