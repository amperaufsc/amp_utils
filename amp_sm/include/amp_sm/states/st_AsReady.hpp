#pragma once

#include <smacc2/smacc.hpp>
#include <lifecycle_msgs/msg/transition.hpp>

#include "../client_behaviors/cb_change_lifecycle.hpp"
#include <amp_sm/clients/cl_lifecycle_pipeline.hpp>
#include <amp_sm/clients/cl_topic_listener.hpp>
#include <amp_sm/clients/cl_lifecycle_monitor.hpp>

namespace amp_sm
{
struct st_AsDriving;
struct st_AsChecking;
struct st_AsCalibration;
struct st_AsEmergency;

struct st_AsReady : smacc2::SmaccState<st_AsReady, Amp_sm>
{
    using SmaccState::SmaccState;

    typedef boost::mpl::list<
    smacc2::Transition<amp_sm::EvCheckListener, amp_sm::st_AsChecking>,
    smacc2::Transition<amp_sm::EvReadyToDrive, amp_sm::st_AsDriving>,
    smacc2::Transition<amp_sm::EvCalibrationListener, amp_sm::st_AsCalibration>,
    smacc2::Transition<amp_sm::EvNodeCrashed, amp_sm::st_AsEmergency>,
    smacc2::Transition<amp_sm::EvStopListener, amp_sm::st_AsEmergency>
    > reactions;

    static void staticConfigure()
    {   
        
        //
        // Mapper
        //
        
            //...

        //
        //

        //
        // Utils
        //
        
            //...

        //
        //

        //
        //  Control
        //

            //...

        //
        //

        std::vector<std::string> nodes_to_activate = {
            "/repeater_node",
            "/perception_lifecycle_node",
            "/disparity_pub_life",
            "/path_node",
            "/yolo_node",
            "/control_node"
        };

        configure_orthogonal<or_utils, CbChangeLifecycleGroup>(nodes_to_activate, 3);
        
    }

    void onEntry()
    {
        RCLCPP_INFO(getLogger(), "Estado StAsReady: Disparando comandos de configuração...");
        
    }

    void onExit()
    {
        RCLCPP_INFO(getLogger(), "Estado StAsReady: Saltando!");
    }
};
} // namespace amp_sm