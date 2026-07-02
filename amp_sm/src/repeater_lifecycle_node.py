#!/usr/bin/env python3

import rclpy
from rclpy.lifecycle import Node, State, TransitionCallbackReturn
from std_msgs.msg import String, Bool
from fs_msgs.msg import GoSignal

class RosMsgRepeater(Node):
    def __init__(self):
        super().__init__('repeater_node')
        
        # Variáveis locais iniciadas no construtor
        self.current_mission_translated = "NONE"
        self.timer = None
        
        # Dicionários para gerir Subscriptions e Publishers
        self.subs = {}
        self.pubs = {}

        # Dicionário de conversão de Missões (simulando um Switch/Case)
        self.mission_map = {
            "TRACKDRIVE": "trackdrive",
            "AUTOCROSS": "auto-cross",
            "ACCELERATION": "acceleration",
            "SKIDPAD": "skidpad"
        }
        
        self.get_logger().info('Inicializando repeater node...')

    # ========================================================================
    # TRANSIÇÕES DO LIFECYCLE
    # ========================================================================

    def on_configure(self, state: State) -> TransitionCallbackReturn:
        try:
            self.get_logger().info('Configurando repeater node...')
            
            # --- PUBLISHERS ---
            self.pubs['mission_go'] = self.create_lifecycle_publisher(
                GoSignal, 
                '/as_amp/mission_selected/go', 
                10
            )
            
            self.pubs['go'] = self.create_lifecycle_publisher(Bool, '/as_amp/res/go_out', 10)
            self.pubs['ready'] = self.create_lifecycle_publisher(Bool, '/as_amp/res/as_ready_out', 10)
            self.pubs['emergency'] = self.create_lifecycle_publisher(Bool, '/as_amp/res/as_emergency_out', 10)

            # --- SUBSCRIBERS ---
            self.subs['mission_select'] = self.create_subscription(
                String,
                '/as_amp/mission_select',
                self.mission_command_callback,
                10
            )
            
            self.subs['go'] = self.create_subscription(
                Bool,
                '/as_amp/res/go',
                lambda msg: self.bool_repeater_callback(msg, 'go'),
                10
            )
            
            self.subs['ready'] = self.create_subscription(
                Bool,
                '/as_amp/res/as_ready',
                lambda msg: self.bool_repeater_callback(msg, 'ready'),
                10
            )
            
            self.subs['emergency'] = self.create_subscription(
                Bool,
                '/as_amp/res/as_emergency',
                lambda msg: self.bool_repeater_callback(msg, 'emergency'),
                10
            )

            return TransitionCallbackReturn.SUCCESS
            
        except Exception as e:
            self.get_logger().error(f'❌ Erro ao configurar o nó: {e}')
            return TransitionCallbackReturn.ERROR

    def on_activate(self, state: State) -> TransitionCallbackReturn:
        try:
            self.get_logger().info('Ativando repeater node...')
            super().on_activate(state)
            
            # Inicia o timer que repetirá a missão selecionada a 10 Hz
            timer_period = 0.1  
            self.timer = self.create_timer(timer_period, self.timer_callback)

            return TransitionCallbackReturn.SUCCESS
            
        except Exception as e:
            self.get_logger().error(f'❌ Erro ao ativar o nó: {e}')
            return TransitionCallbackReturn.ERROR

    def on_deactivate(self, state: State) -> TransitionCallbackReturn:
        try:
            self.get_logger().info('Desativando repeater node...')
            super().on_deactivate(state)
            
            if self.timer is not None:
                self.timer.cancel()
                self.destroy_timer(self.timer)
                self.timer = None
                
            return TransitionCallbackReturn.SUCCESS
            
        except Exception as e:
            self.get_logger().error(f'❌ Erro ao desativar o nó: {e}')
            return TransitionCallbackReturn.ERROR

    def on_cleanup(self, state: State) -> TransitionCallbackReturn:
        try:
            self.get_logger().info('Desconfigurando repeater node...')
            
            # Limpa todos os Subscribers
            for sub in self.subs.values():
                self.destroy_subscription(sub)
            self.subs.clear()
                
            # Limpa todos os Publishers
            for pub in self.pubs.values():
                self.destroy_publisher(pub)
            self.pubs.clear()
                
            self.current_mission_translated = "NONE"
            
            return TransitionCallbackReturn.SUCCESS

        except Exception as e:
            self.get_logger().error(f'❌ Erro ao desconfigurar (cleanup) o nó: {e}')
            return TransitionCallbackReturn.ERROR
        
    def on_shutdown(self, state: State) -> TransitionCallbackReturn:
        try:
            self.get_logger().info('Shutdown repeater node...')
            
            if self.timer is not None:
                self.timer.cancel()
                self.destroy_timer(self.timer)
                
            for sub in self.subs.values():
                self.destroy_subscription(sub)
                
            for pub in self.pubs.values():
                self.destroy_publisher(pub)
                
            return TransitionCallbackReturn.SUCCESS
            
        except Exception as e:
            self.get_logger().error(f'❌ Erro durante o shutdown do nó: {e}')
            return TransitionCallbackReturn.ERROR

    # ========================================================================
    # LÓGICA DO NÓ (CALLBACKS)
    # ========================================================================

    def mission_command_callback(self, msg):
        mission_input = msg.data.upper() # Garante case-insensitivity na entrada
        
        # Verifica se a missão existe no dicionário e faz a tradução
        if mission_input in self.mission_map:
            translated_mission = self.mission_map[mission_input]
            
            if self.current_mission_translated != translated_mission:
                self.current_mission_translated = translated_mission
                self.get_logger().info(f'🔄 Nova missão validada e armazenada: {self.current_mission_translated}')
        else:
            self.get_logger().warn(f'⚠️ Missão desconhecida recebida: {mission_input}')

    def bool_repeater_callback(self, msg, pub_key):
        # Repassa o booleano APENAS se o publisher específico estiver ativo (Lifecycle)
        if pub_key in self.pubs and self.pubs[pub_key].is_activated:
            self.pubs[pub_key].publish(msg)
            # Descomente a linha abaixo para debug, mas pode poluir muito o terminal
            # self.get_logger().info(f'🔁 Repetindo booleano: {msg.data} no canal {pub_key}')

    def timer_callback(self):
        # O Timer apenas lida com a repetição da Missão Atual (GoSignal)
        pub_mission = self.pubs.get('mission_go')
        
        if pub_mission and pub_mission.is_activated and self.current_mission_translated != "NONE":
            msg = GoSignal()
            msg.mission = self.current_mission_translated
            pub_mission.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = RosMsgRepeater()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()