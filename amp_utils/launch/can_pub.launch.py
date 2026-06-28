from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument as LaunchArg
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    return LaunchDescription([
        # Namespace global do nó
        LaunchArg('namespace', default_value=[''], description='Namespace for the CAN Node'),

        # ==========================================
        # 1. DECLARAÇÃO DOS ARGUMENTOS DOS TÓPICOS
        # ==========================================
        
        # STRING
        LaunchArg('autonomous_mode_topic', default_value=['/can/autonomous_mode'], description='Topic for autonomous mode'),

        # UINT8 (Painel & RES & ECU)
        LaunchArg('ready_to_drive_topic', default_value=['/can/ready_to_drive'], description='Topic for ready to drive'),
        LaunchArg('page_id_topic', default_value=['/can/page_id'], description='Topic for page id'),
        LaunchArg('as_status_topic', default_value=['/can/as_status'], description='Topic for AS status'),
        LaunchArg('go_signal_topic', default_value=['/can/go_signal'], description='Topic for go signal'),
        LaunchArg('emergency_topic', default_value=['/can/emergency'], description='Topic for emergency'),
        LaunchArg('inverter_status_topic', default_value=['/can/inverter_status'], description='Topic for inverter status'),
        LaunchArg('current_state_topic', default_value=['/can/current_state'], description='Topic for current state'),
        LaunchArg('tms_error_code_topic', default_value=['/can/tms_error_code'], description='Topic for TMS error code'),
        LaunchArg('inverter_error_code_topic', default_value=['/can/inverter_error_code'], description='Topic for inverter error code'),
        LaunchArg('max_temperature_topic', default_value=['/can/max_temperature'], description='Topic for max temperature'),
        LaunchArg('brake_switch_topic', default_value=['/can/brake_switch'], description='Topic for brake switch'),
        LaunchArg('brake_pedal_topic', default_value=['/can/brake_pedal'], description='Topic for brake pedal'),
        LaunchArg('accelerator_pedal_topic', default_value=['/can/accelerator_pedal'], description='Topic for accelerator pedal'),
        LaunchArg('state_of_charge_topic', default_value=['/can/state_of_charge'], description='Topic for state of charge'),
        LaunchArg('max_cell_voltage_topic', default_value=['/can/max_cell_voltage'], description='Topic for max cell voltage'),
        LaunchArg('avg_cell_voltage_topic', default_value=['/can/avg_cell_voltage'], description='Topic for avg cell voltage'),
        LaunchArg('min_cell_voltage_topic', default_value=['/can/min_cell_voltage'], description='Topic for min cell voltage'),

        # UINT16 (ECU)
        LaunchArg('control_word_topic', default_value=['/can/control_word'], description='Topic for control word'),
        LaunchArg('ecu_error_code_topic', default_value=['/can/ecu_error_code'], description='Topic for ECU error code'),
        LaunchArg('inverter_temperature_topic', default_value=['/can/inverter_temperature'], description='Topic for inverter temperature'),
        LaunchArg('motor_torque_topic', default_value=['/can/motor_torque'], description='Topic for motor torque'),
        LaunchArg('motor_temperature_topic', default_value=['/can/motor_temperature'], description='Topic for motor temperature'),
        LaunchArg('motor_rpm_topic', default_value=['/can/motor_rpm'], description='Topic for motor rpm'),

        # FLOAT32 (DataLogger & ECU)
        LaunchArg('encoder_rear_left_topic', default_value=['/can/encoder_rear_left'], description='Topic for rear left encoder'),
        LaunchArg('encoder_rear_right_topic', default_value=['/can/encoder_rear_right'], description='Topic for rear right encoder'),
        LaunchArg('encoder_front_left_topic', default_value=['/can/encoder_front_left'], description='Topic for front left encoder'),
        LaunchArg('encoder_front_right_topic', default_value=['/can/encoder_front_right'], description='Topic for front right encoder'),
        LaunchArg('accel_x_topic', default_value=['/can/accel_x'], description='Topic for accel x'),
        LaunchArg('accel_y_topic', default_value=['/can/accel_y'], description='Topic for accel y'),
        LaunchArg('accel_z_topic', default_value=['/can/accel_z'], description='Topic for accel z'),
        LaunchArg('battery_current_topic', default_value=['/can/battery_current'], description='Topic for battery current'),
        LaunchArg('battery_voltage_topic', default_value=['/can/battery_voltage'], description='Topic for battery voltage'),
        LaunchArg('inverter_current_topic', default_value=['/can/inverter_current'], description='Topic for inverter current'),
        LaunchArg('inverter_voltage_topic', default_value=['/can/inverter_voltage'], description='Topic for inverter voltage'),

        # ==========================================
        # 2. CONFIGURAÇÃO DO NÓ E REMAPPINGS
        # ==========================================
        Node(
            package='amp_utils',
            executable='can_publisher_node.py', # Lembre-se de usar o nome configurado no setup.py (sem .py)
            name='can_publisher_node',
            namespace=LaunchConfiguration('namespace'),
            output='screen',
            remappings=[
                # STRING
                ('/can/autonomous_mode', LaunchConfiguration('autonomous_mode_topic')),

                # UINT8
                ('/can/ready_to_drive', LaunchConfiguration('ready_to_drive_topic')),
                ('/can/page_id', LaunchConfiguration('page_id_topic')),
                ('/can/as_status', LaunchConfiguration('as_status_topic')),
                ('/can/go_signal', LaunchConfiguration('go_signal_topic')),
                ('/can/emergency', LaunchConfiguration('emergency_topic')),
                ('/can/inverter_status', LaunchConfiguration('inverter_status_topic')),
                ('/can/current_state', LaunchConfiguration('current_state_topic')),
                ('/can/tms_error_code', LaunchConfiguration('tms_error_code_topic')),
                ('/can/inverter_error_code', LaunchConfiguration('inverter_error_code_topic')),
                ('/can/max_temperature', LaunchConfiguration('max_temperature_topic')),
                ('/can/brake_switch', LaunchConfiguration('brake_switch_topic')),
                ('/can/brake_pedal', LaunchConfiguration('brake_pedal_topic')),
                ('/can/accelerator_pedal', LaunchConfiguration('accelerator_pedal_topic')),
                ('/can/state_of_charge', LaunchConfiguration('state_of_charge_topic')),
                ('/can/max_cell_voltage', LaunchConfiguration('max_cell_voltage_topic')),
                ('/can/avg_cell_voltage', LaunchConfiguration('avg_cell_voltage_topic')),
                ('/can/min_cell_voltage', LaunchConfiguration('min_cell_voltage_topic')),

                # UINT16
                ('/can/control_word', LaunchConfiguration('control_word_topic')),
                ('/can/ecu_error_code', LaunchConfiguration('ecu_error_code_topic')),
                ('/can/inverter_temperature', LaunchConfiguration('inverter_temperature_topic')),
                ('/can/motor_torque', LaunchConfiguration('motor_torque_topic')),
                ('/can/motor_temperature', LaunchConfiguration('motor_temperature_topic')),
                ('/can/motor_rpm', LaunchConfiguration('motor_rpm_topic')),

                # FLOAT32
                ('/can/encoder_rear_left', LaunchConfiguration('encoder_rear_left_topic')),
                ('/can/encoder_rear_right', LaunchConfiguration('encoder_rear_right_topic')),
                ('/can/encoder_front_left', LaunchConfiguration('encoder_front_left_topic')),
                ('/can/encoder_front_right', LaunchConfiguration('encoder_front_right_topic')),
                ('/can/accel_x', LaunchConfiguration('accel_x_topic')),
                ('/can/accel_y', LaunchConfiguration('accel_y_topic')),
                ('/can/accel_z', LaunchConfiguration('accel_z_topic')),
                ('/can/battery_current', LaunchConfiguration('battery_current_topic')),
                ('/can/battery_voltage', LaunchConfiguration('battery_voltage_topic')),
                ('/can/inverter_current', LaunchConfiguration('inverter_current_topic')),
                ('/can/inverter_voltage', LaunchConfiguration('inverter_voltage_topic')),
            ]
        )
    ])