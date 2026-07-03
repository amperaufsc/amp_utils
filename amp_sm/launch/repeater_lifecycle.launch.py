from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument as LaunchArg
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():

    return LaunchDescription([
        # --- Configurações Gerais ---
        LaunchArg('namespace', default_value='', description='Namespace for the node'),
        
        # --- Tópicos de Entrada (Subscribers) ---
        LaunchArg('mission_select_in', default_value='/as_amp/mission_select', description='Mission select input topic'),
        LaunchArg('go_in', default_value='/as_amp/res/go', description='GO signal input topic'),
        LaunchArg('ready_in', default_value='/as_amp/res/as_ready', description='AS READY signal input topic'),
        LaunchArg('emergency_in', default_value='/as_amp/res/as_emergency', description='EMERGENCY signal input topic'),

        # --- Tópicos de Saída (Publishers) ---
        LaunchArg('mission_go_out', default_value='/as_amp/mission_selected/go', description='Mission Go_Signal output topic'),
        LaunchArg('go_out', default_value='/as_amp/res/go_out', description='GO signal repeated output topic'),
        LaunchArg('ready_out', default_value='/as_amp/res/as_ready_out', description='AS READY repeated output topic'),
        LaunchArg('emergency_out', default_value='/as_amp/res/as_emergency_out', description='EMERGENCY repeated output topic'),

        # --- Definição do Nó Lifecycle ---
        Node(
            package='amp_sm',
            executable='repeater_lifecycle_node.py',
            name='repeater_node',
            namespace=LaunchConfiguration('namespace'),
            output='screen',
            remappings=[
                ('/as_amp/mission_select', LaunchConfiguration('mission_select_in')),
                ('/as_amp/res/go', LaunchConfiguration('go_in')),
                ('/as_amp/res/as_ready', LaunchConfiguration('ready_in')),
                ('/as_amp/res/as_emergency', LaunchConfiguration('emergency_in')),
                
                ('/as_amp/mission_selected/go', LaunchConfiguration('mission_go_out')),
                ('/as_amp/res/go_out', LaunchConfiguration('go_out')),
                ('/as_amp/res/as_ready_out', LaunchConfiguration('ready_out')),
                ('/as_amp/res/as_emergency_out', LaunchConfiguration('emergency_out'))
            ]
        )
    ])