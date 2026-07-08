#!/usr/bin/env python3

import rclpy
from rclpy.lifecycle import Node, State, TransitionCallbackReturn
from std_msgs.msg import String, Bool
from fs_msgs.msg import GoSignal

class RosMsgRepeater(Node):
    def __init__(self):
        super().__init__('repeater_node')
        
        # --- MÁQUINA DE ESTADOS ---
        # WAIT_MISSION: Ignora RES e aguarda missão
        # WAIT_RES: Missão recebida, 60s para receber GO e READY
        # PUBLISHING: Condições atendidas, publicando missão a 10Hz
        self.sm_state = "WAIT_MISSION"
        
        self.current_mission_translated = "NONE"
        self.timer_10hz = None
        self.timeout_timer = None # Timer para a janela de 1 minuto
        
        # Variáveis de memória do RES
        self.res_go_state = False
        self.as_ready_state = False
        
        self.subs = {}
        self.pubs = {}

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
            
            self.pubs['mission_go'] = self.create_lifecycle_publisher(GoSignal, '/as_amp/mission_selected/go', 10)
            self.pubs['go'] = self.create_lifecycle_publisher(Bool, '/as_amp/res/go_out', 10)
            self.pubs['ready'] = self.create_lifecycle_publisher(Bool, '/as_amp/res/as_ready_out', 10)
            self.pubs['emergency'] = self.create_lifecycle_publisher(Bool, '/as_amp/res/as_emergency_out', 10)

            self.subs['mission_select'] = self.create_subscription(String, '/as_amp/mission_select', self.mission_command_callback, 10)
            self.subs['go'] = self.create_subscription(Bool, '/as_amp/res/go', lambda msg: self.bool_repeater_callback(msg, 'go'), 10)
            self.subs['ready'] = self.create_subscription(Bool, '/as_amp/res/as_ready', lambda msg: self.bool_repeater_callback(msg, 'ready'), 10)
            self.subs['emergency'] = self.create_subscription(Bool, '/as_amp/res/as_emergency', lambda msg: self.bool_repeater_callback(msg, 'emergency'), 10)

            return TransitionCallbackReturn.SUCCESS
            
        except Exception as e:
            self.get_logger().error(f'❌ Erro ao configurar o nó: {e}')
            return TransitionCallbackReturn.ERROR

    def on_activate(self, state: State) -> TransitionCallbackReturn:
        try:
            self.get_logger().info('Ativando repeater node...')
            super().on_activate(state)
            
            # Loop de publicação a 10 Hz
            self.timer_10hz = self.create_timer(0.1, self.timer_10hz_callback)

            return TransitionCallbackReturn.SUCCESS
            
        except Exception as e:
            self.get_logger().error(f'❌ Erro ao ativar o nó: {e}')
            return TransitionCallbackReturn.ERROR

    def on_deactivate(self, state: State) -> TransitionCallbackReturn:
        try:
            self.get_logger().info('Desativando repeater node...')
            super().on_deactivate(state)
            
            if self.timer_10hz is not None:
                self.timer_10hz.cancel()
                self.destroy_timer(self.timer_10hz)
                self.timer_10hz = None
                
            if self.timeout_timer is not None:
                self.timeout_timer.cancel()
                self.destroy_timer(self.timeout_timer)
                self.timeout_timer = None
                
            return TransitionCallbackReturn.SUCCESS
            
        except Exception as e:
            self.get_logger().error(f'❌ Erro ao desativar o nó: {e}')
            return TransitionCallbackReturn.ERROR

    def on_cleanup(self, state: State) -> TransitionCallbackReturn:
        try:
            self.get_logger().info('Desconfigurando repeater node...')
            
            for sub in self.subs.values():
                self.destroy_subscription(sub)
            self.subs.clear()
                
            for pub in self.pubs.values():
                self.destroy_publisher(pub)
            self.pubs.clear()
                
            # Reseta estado
            self.sm_state = "WAIT_MISSION"
            self.current_mission_translated = "NONE"
            self.res_go_state = False
            self.as_ready_state = False
            
            return TransitionCallbackReturn.SUCCESS

        except Exception as e:
            self.get_logger().error(f'❌ Erro no cleanup: {e}')
            return TransitionCallbackReturn.ERROR
        
    def on_shutdown(self, state: State) -> TransitionCallbackReturn:
        try:
            self.get_logger().info('Shutdown repeater node...')
            
            for timer in [self.timer_10hz, self.timeout_timer]:
                if timer is not None:
                    timer.cancel()
                    self.destroy_timer(timer)
                
            for sub in self.subs.values():
                self.destroy_subscription(sub)
            for pub in self.pubs.values():
                self.destroy_publisher(pub)
                
            return TransitionCallbackReturn.SUCCESS
            
        except Exception as e:
            self.get_logger().error(f'❌ Erro no shutdown: {e}')
            return TransitionCallbackReturn.ERROR

    # ========================================================================
    # LÓGICA DO NÓ
    # ========================================================================

    def mission_timeout_callback(self):
        """Disparado se passar 1 minuto sem receber o GO e READY."""
        self.get_logger().warn('⏱️ Timeout de 1 minuto expirado! Retornando ao estado inicial.')
        
        self.sm_state = "WAIT_MISSION"
        self.current_mission_translated = "NONE"
        self.res_go_state = False
        self.as_ready_state = False
        
        # Destrói o timer de timeout pois ele já cumpriu seu papel
        if self.timeout_timer is not None:
            self.timeout_timer.cancel()
            self.destroy_timer(self.timeout_timer)
            self.timeout_timer = None

    def mission_command_callback(self, msg):
        mission_input = msg.data.upper()
        
        if mission_input in self.mission_map:
            translated_mission = self.mission_map[mission_input]
            
            self.current_mission_translated = translated_mission
            self.sm_state = "WAIT_RES"
            self.res_go_state = False
            self.as_ready_state = False
            
            self.get_logger().info(f'🔄 Missão [{self.current_mission_translated}] selecionada! Janela de 60s iniciada para receber GO e READY.')
            
            # Gerencia a janela de tempo de 60 segundos
            if self.timeout_timer is not None:
                self.timeout_timer.cancel()
                self.destroy_timer(self.timeout_timer)
            
            self.timeout_timer = self.create_timer(60.0, self.mission_timeout_callback)
            
        else:
            self.get_logger().warn(f'⚠️ Missão desconhecida: {mission_input}')

    def bool_repeater_callback(self, msg, pub_key):
        # A mensagem de emergência passa direto, independentemente do estado.
        # Mas GO e READY dependem do estado da máquina.
        if pub_key in ['go', 'ready']:
            
            # Se não recebemos missão ainda, ignoramos os botões completamente
            if self.sm_state == "WAIT_MISSION":
                return 

            # Atualiza a memória de estado
            if pub_key == 'go':
                self.res_go_state = msg.data
            elif pub_key == 'ready':
                self.as_ready_state = msg.data

            # Se estávamos esperando e ambos ficaram verdadeiros, passamos para PUBLISHING
            if self.sm_state == "WAIT_RES" and self.res_go_state and self.as_ready_state:
                self.sm_state = "PUBLISHING"
                
                # Sucesso! Cancela a janela de tempo de 1 minuto
                if self.timeout_timer is not None:
                    self.timeout_timer.cancel()
                    self.destroy_timer(self.timeout_timer)
                    self.timeout_timer = None
                    
                self.get_logger().info('✅ AS_READY e GO recebidos a tempo! Publicando missão a 10Hz.')

            # Regra de Segurança Extra: Se cair qualquer um dos sinais DURANTE a execução, aborta tudo.
            elif self.sm_state == "PUBLISHING" and (not self.res_go_state or not self.as_ready_state):
                self.get_logger().warn('🚨 Sinal de GO ou READY caiu! Abortando a publicação e voltando ao início.')
                self.sm_state = "WAIT_MISSION"
                self.current_mission_translated = "NONE"

        # Repassa o booleano APENAS se o publisher específico estiver ativo e o estado permitiu chegar aqui
        if pub_key in self.pubs and self.pubs[pub_key].is_activated:
            self.pubs[pub_key].publish(msg)

    def timer_10hz_callback(self):
        pub_mission = self.pubs.get('mission_go')
        
        # O Timer apenas publica se estivermos no estado final (PUBLISHING)
        if pub_mission and pub_mission.is_activated and self.sm_state == "PUBLISHING":
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