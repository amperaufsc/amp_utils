#!/usr/bin/env python3

import rclpy
from rclpy.lifecycle import Node, State, TransitionCallbackReturn
from std_msgs.msg import String

class RosMsgRepeater(Node):
    def __init__(self):
        # Inicializa a classe base de Lifecycle em vez do Node normal
        super().__init__('repeater_node')
        
        # Variáveis locais iniciadas no construtor (sem alocar ROS 2 ainda)
        self.current_mission = "NONE"
        self.subscription = None
        self.publisher_ = None
        self.timer = None
        
        self.get_logger().info('Inicializando repeater node...')

    # ========================================================================
    # TRANSIÇÕES DO LIFECYCLE
    # ========================================================================

    def on_configure(self, state: State) -> TransitionCallbackReturn:
        try:
            self.get_logger().info('Configurando repeater node...')
            
            # 1. Cria o Lifecycle Publisher (nasce desativado)
            self.publisher_ = self.create_lifecycle_publisher(
                String, 
                '/as_amp/mission_selected', 
                10
            )

            # 2. Cria o Subscriber (já pode ouvir, mas não publicamos nada ainda)
            self.subscription = self.create_subscription(
                String,
                '/as_amp/mission_select',
                self.mission_command_callback,
                10
            )

            return TransitionCallbackReturn.SUCCESS
        
        except Exception as e:
            self.get_logger().error(f'❌ Erro ao ativar o nó: {e}')
            
            return TransitionCallbackReturn.ERROR

    def on_activate(self, state: State) -> TransitionCallbackReturn:
        try:
            self.get_logger().info('Ativando repeater node...')
            super().on_activate(state)
            timer_period = 0.1  # 10 Hz
            self.timer = self.create_timer(timer_period, self.timer_callback)

            return TransitionCallbackReturn.SUCCESS

        
        except Exception as e:
            self.get_logger().error(f'❌ Erro ao ativar o nó: {e}')
            return TransitionCallbackReturn.ERROR

    def on_deactivate(self, state: State) -> TransitionCallbackReturn:
        try:
            self.get_logger().info('Desativando repeater node...')
            
            super().on_deactivate(state)
            
            # Destrói o timer para parar o processamento imediatamente
            if self.timer is not None:
                self.timer.cancel()
                self.destroy_timer(self.timer)
                self.timer = None
                
            return TransitionCallbackReturn.SUCCESS
        except Exception as e:
            self.get_logger().error(f'❌ Erro ao ativar o nó: {e}')
            return TransitionCallbackReturn.ERROR

    def on_cleanup(self, state: State) -> TransitionCallbackReturn:
        try:
            self.get_logger().info('Desconfigurando repeater node...')
            
            if self.subscription is not None:
                self.destroy_subscription(self.subscription)
                self.subscription = None
                
            if self.publisher_ is not None:
                self.destroy_publisher(self.publisher_)
                self.publisher_ = None
                
            # Apaga a missão da memória
            self.current_mission = "NONE"
            
            return TransitionCallbackReturn.SUCCESS

        except Exception as e:
            self.get_logger().error(f'❌ Erro ao ativar o nó: {e}')
            return TransitionCallbackReturn.ERROR
        
    def on_shutdown(self, state: State) -> TransitionCallbackReturn:
        self.get_logger().info('Shutdown repeater node...')
        
        if self.timer is not None:
            self.timer.cancel()
            self.destroy_timer(self.timer)
        if self.subscription is not None:
            self.destroy_subscription(self.subscription)
        if self.publisher_ is not None:
            self.destroy_publisher(self.publisher_)
            
        return TransitionCallbackReturn.SUCCESS

    # ========================================================================
    # LÓGICA DO NÓ (CALLBACKS)
    # ========================================================================

    def mission_command_callback(self, msg):
        nova_missao = msg.data
        
        if self.current_mission != nova_missao:
            self.current_mission = nova_missao
            self.get_logger().info(f'🔄 Missão atualizada na memória: {self.current_mission}')

    def timer_callback(self):
        # A publicação só ocorre se o nó estiver "Active" e tivermos uma missão
        if self.current_mission != "NONE" and self.publisher_.is_activated:
            msg = String()
            msg.data = self.current_mission
            self.publisher_.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = RosMsgRepeater()
    
    try:
        # Apenas fica a rodar (spin). As mudanças de estado virão do SMACC2
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()