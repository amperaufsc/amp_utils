#pragma once

#include <smacc2/smacc.hpp>

namespace amp_sm
{
    struct st_AsOff;
    struct st_AsReady;
    struct st_AsChecking;
    struct st_AsCalibration;
    struct st_AsDriving;
    struct st_AsEmergency;
    struct st_AsFinished;
}

#include "orthogonals/or_mapper.hpp"
#include "orthogonals/or_motion.hpp"
#include "orthogonals/or_perception.hpp"
#include "orthogonals/or_utils.hpp"

namespace amp_sm
{
struct Amp_sm : public smacc2::SmaccStateMachineBase<Amp_sm, st_AsOff>
{
    // ESTA LINHA É OBRIGATÓRIA: Ela herda os construtores do SMACC2 que o Boost exige
    using SmaccStateMachineBase::SmaccStateMachineBase;

    void onInitialize() override
    {
        RCLCPP_INFO(getLogger(), "[Amp SM] Iniciando a Máquina de Estados...");
        this->createOrthogonal<or_mapper>();
        this->createOrthogonal<or_motion>();
        this->createOrthogonal<or_perception>();
        this->createOrthogonal<or_utils>();
    }
};
} // namespace amp_sm

#include "states/st_AsOff.hpp"
#include "states/st_AsReady.hpp"
#include "states/st_AsDriving.hpp"
#include "states/st_AsChecking.hpp"
#include "states/st_AsCalibration.hpp"
#include "states/st_AsEmergency.hpp"
#include "states/st_AsFinished.hpp"
