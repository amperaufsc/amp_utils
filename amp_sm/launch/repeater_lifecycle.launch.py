from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration
from launch.actions import DeclareLaunchArgument

def generate_launch_description():
    
    # Tópicos de Entrada (Subscribers)
    mission_select_in_arg = DeclareLaunchArgument(
        'mission_select_in', default_value='/as_amp/mission_select',
        description='Tópico de entrada para seleção de missão (String)'
    )
    go_in_arg = DeclareLaunchArgument(
        'go_in', default_value='/as_amp/go',
        description='Tópico de entrada do sinal GO (Bool)'
    )
    ready_in_arg = DeclareLaunchArgument(
        'ready_in', default_value='/as_amp/as_ready',
        description='Tópico de entrada do sinal AS READY (Bool)'
    )
    emergency_in_arg = DeclareLaunchArgument(
        'emergency_in', default_value='/as_amp/as_emergency',
        description='Tópico de entrada do sinal EMERGENCY (Bool)'
    )

    # Tópicos de Saída (Publishers)
    mission_go_out_arg = DeclareLaunchArgument(
        'mission_go_out', default_value='/go',
        description='Tópico de saída da missão traduzida (GoSignal)'
    )
    go_out_arg = DeclareLaunchArgument(
        'go_out', default_value='/as_amp/go_out',
        description='Tópico de saída do sinal GO repetido (Bool)'
    )
    ready_out_arg = DeclareLaunchArgument(
        'ready_out', default_value='/as_amp/as_ready_out',
        description='Tópico de saída do sinal AS READY repetido (Bool)'
    )
    emergency_out_arg = DeclareLaunchArgument(
        'emergency_out', default_value='/as_amp/as_emergency_out',
        description='Tópico de saída do sinal EMERGENCY repetido (Bool)'
    )
    
    repeater_node = Node(
        package='amp_sm',
        executable='repeater_lifecycle_node.py',
        name='repeater_node',
        output='screen',
        remappings=[
            # (Nome original no código Python, Variável do Launch)
            ('/as_amp/mission_select', LaunchConfiguration('mission_select_in')),
            ('/as_amp/res/go', LaunchConfiguration('go_in')),
            ('/as_amp/res/as_ready', LaunchConfiguration('ready_in')),
            ('/as_amp/res/as_emergency', LaunchConfiguration('emergency_in')),
            
            ('/as_amp/mission_selected/go', LaunchConfiguration('mission_go_out')),
            ('/as_amp/res/go_out', LaunchConfiguration('go_out')),
            ('/as_amp/res/as_ready_out', LaunchConfiguration('ready_out')),
            ('/as_amp/res/as_emergency_out', LaunchConfiguration('emergency_out')),
        ]
    )

    return LaunchDescription([
        mission_select_in_arg,
        go_in_arg,
        ready_in_arg,
        emergency_in_arg,
        mission_go_out_arg,
        go_out_arg,
        ready_out_arg,
        emergency_out_arg,
        repeater_node
    ])