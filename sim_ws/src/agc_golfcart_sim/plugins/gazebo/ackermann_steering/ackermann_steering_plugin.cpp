#include <gz/plugin/Register.hh>
#include <ignition/gazebo6/ignition/gazebo/System.hh>
#include <ignition/gazebo6/ignition/gazebo/Model.hh>
#include <ignition/gazebo6/ignition/gazebo/components/Joint.hh>
#include <ignition/gazebo6/ignition/gazebo/components/JointPosition.hh>
#include <ignition/gazebo6/ignition/gazebo/components/Name.hh>
#include <ignition/gazebo6/ignition/gazebo/Util.hh>
#include <ignition/gazebo6/ignition/gazebo/components/JointPositionReset.hh>
#include <cmath>

namespace ackermann_steering
{
  class AckermannSteeringPlugin :
    public ignition::gazebo::System,
    public ignition::gazebo::ISystemConfigure,
    public ignition::gazebo::ISystemPreUpdate
  {
    private:
      ignition::gazebo::Model model{ignition::gazebo::kNullEntity};
      ignition::gazebo::Entity steeringInputJoint{ignition::gazebo::kNullEntity};
      ignition::gazebo::Entity leftSteeringJoint{ignition::gazebo::kNullEntity};
      ignition::gazebo::Entity rightSteeringJoint{ignition::gazebo::kNullEntity};
      
      double wheelbase{2.030};
      double trackWidth{1.09};
      
      std::string steeringInputName{"steering_input_joint"};
      std::string leftSteeringName{"front_left_steering_joint"};
      std::string rightSteeringName{"front_right_steering_joint"};

    public:
      void Configure(const ignition::gazebo::Entity &_entity,
                     const std::shared_ptr<const sdf::Element> &_sdf,
                     ignition::gazebo::EntityComponentManager &_ecm,
                     ignition::gazebo::EventManager &/*_eventMgr*/) override
      {
        this->model = ignition::gazebo::Model(_entity);
        
        if (!this->model.Valid(_ecm))
        {
          ignerr << "AckermannSteeringPlugin should be attached to a model entity." << std::endl;
          return;
        }
        
        // Get parameters
        if (_sdf->HasElement("wheelbase"))
          this->wheelbase = _sdf->Get<double>("wheelbase");
        
        if (_sdf->HasElement("track_width"))
          this->trackWidth = _sdf->Get<double>("track_width");
        
        if (_sdf->HasElement("steering_input_joint"))
          this->steeringInputName = _sdf->Get<std::string>("steering_input_joint");
        
        if (_sdf->HasElement("left_steering_joint"))
          this->leftSteeringName = _sdf->Get<std::string>("left_steering_joint");
        
        if (_sdf->HasElement("right_steering_joint"))
          this->rightSteeringName = _sdf->Get<std::string>("right_steering_joint");
        
        // Get joint entities
        this->steeringInputJoint = this->model.JointByName(_ecm, this->steeringInputName);
        this->leftSteeringJoint = this->model.JointByName(_ecm, this->leftSteeringName);
        this->rightSteeringJoint = this->model.JointByName(_ecm, this->rightSteeringName);
        
        if (this->steeringInputJoint == ignition::gazebo::kNullEntity ||
            this->leftSteeringJoint == ignition::gazebo::kNullEntity ||
            this->rightSteeringJoint == ignition::gazebo::kNullEntity)
        {
          ignerr << "AckermannSteeringPlugin: Failed to find required joints!" << std::endl;
          return;
        }
        
        // Enable position component for joints
        ignition::gazebo::enableComponent<ignition::gazebo::components::JointPosition>(_ecm, this->steeringInputJoint);
        ignition::gazebo::enableComponent<ignition::gazebo::components::JointPosition>(_ecm, this->leftSteeringJoint);
        ignition::gazebo::enableComponent<ignition::gazebo::components::JointPosition>(_ecm, this->rightSteeringJoint);
        
        ignmsg << "AckermannSteeringPlugin loaded successfully!" << std::endl;
        ignmsg << "  Wheelbase: " << this->wheelbase << " m" << std::endl;
        ignmsg << "  Track Width: " << this->trackWidth << " m" << std::endl;
      }

    void PreUpdate(const ignition::gazebo::UpdateInfo &/*_info*/,
                   ignition::gazebo::EntityComponentManager &_ecm) override
    {
      // Get steering input angle
      auto steeringPos = _ecm.Component<ignition::gazebo::components::JointPosition>(this->steeringInputJoint);
      if (!steeringPos || steeringPos->Data().empty())
        return;
      
      double steeringAngle = steeringPos->Data()[0];
      
      double leftAngle, rightAngle;
      
      if (std::abs(steeringAngle) < 0.001)
      {
        leftAngle = rightAngle = 0.0;
      }
      else
      {
        // Ackermann calculation
        double turnRadius = this->wheelbase / std::tan(std::abs(steeringAngle));
        
        if (steeringAngle > 0)
        {
          // Turning left
          leftAngle = std::atan(this->wheelbase / (turnRadius - this->trackWidth/2.0));
          rightAngle = std::atan(this->wheelbase / (turnRadius + this->trackWidth/2.0));
        }
        else
        {
          // Turning right
          rightAngle = -std::atan(this->wheelbase / (turnRadius - this->trackWidth/2.0));
          leftAngle = -std::atan(this->wheelbase / (turnRadius + this->trackWidth/2.0));
        }
      }
      
      // Use JointPositionReset to force set the joint angles
      std::vector<double> leftPosVec = {leftAngle};
      std::vector<double> rightPosVec = {rightAngle};
      
      _ecm.SetComponentData<ignition::gazebo::components::JointPositionReset>(
          this->leftSteeringJoint, leftPosVec);
      _ecm.SetComponentData<ignition::gazebo::components::JointPositionReset>(
          this->rightSteeringJoint, rightPosVec);
    }
  };
}

IGNITION_ADD_PLUGIN(
    ackermann_steering::AckermannSteeringPlugin,
    ignition::gazebo::System,
    ackermann_steering::AckermannSteeringPlugin::ISystemConfigure,
    ackermann_steering::AckermannSteeringPlugin::ISystemPreUpdate)