#pragma once

#include <smacc2/smacc.hpp>
#include <lifecycle_msgs/msg/transition.hpp>

#include "../client_behaviors/cb_change_lifecycle.hpp"
#include <amp_sm/clients/cl_lifecycle_pipeline.hpp>
#include <amp_sm/clients/cl_topic_listener.hpp>

namespace amp_sm
{

struct st_AsEmergency;

struct st_AsFinished : smacc2::SmaccState<st_AsFinished, Amp_sm>
{
    using SmaccState::SmaccState;

    typedef boost::mpl::list<
    smacc2::Transition<amp_sm::EvCalibrationListener, amp_sm::st_AsReady>,
    smacc2::Transition<amp_sm::EvStopListener, amp_sm::st_AsEmergency>

    > reactions;

    static void staticConfigure()
    {
        // ativar todos os nós de sensoriamento e percepção.
    }

    void onEntry()
    {
        RCLCPP_INFO(getLogger(), "Estado StAsCalibration: Disparando comandos de configuração...");
        
    }

    void onExit()
    {
        RCLCPP_INFO(getLogger(), "Estado StAsCalibration: Saltando automaticamente para st_AsReady!");
    }
};
} // namespace amp_sm