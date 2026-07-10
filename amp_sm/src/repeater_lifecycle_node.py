#!/usr/bin/env python3

import rclpy
from rclpy.lifecycle import Node, State, TransitionCallbackReturn
# Importando o UInt8
from std_msgs.msg import String, UInt8 
from fs_msgs.msg import GoSignal

class RosMsgRepeater(Node):
    def __init__(self):
        super().__init__('repeater_node')
        
        # --- MÁQUINA DE ESTADOS ---
        # WAIT_MISSION: Ignora RES e aguarda missão
        # WAIT_RES: Missão recebida, 60s para receber GO e READY
        # WAIT_FINISH: Primeiro GoSignal enviado, aguardando /as_amp/go/finish
        # COMPLETED: Segundo GoSignal enviado, aguarda queda de sinal ou nova missão
        self.sm_state = "WAIT_MISSION"
        
        self.current_mission_translated = "NONE"
        self.timeout_timer = None # Timer para a janela de 1 minuto
        
        # Variáveis de memória do RES (Mantidas como booleanos para a lógica interna)
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
            
            # Publishers alterados para UInt8 para poderem repassar a mensagem recebida
            self.pubs['go'] = self.create_lifecycle_publisher(UInt8, '/as_amp/res/go_out', 10)
            self.pubs['ready'] = self.create_lifecycle_publisher(UInt8, '/as_amp/res/as_ready_out', 10)
            self.pubs['emergency'] = self.create_lifecycle_publisher(UInt8, '/as_amp/res/as_emergency_out', 10)

            self.subs['mission_select'] = self.create_subscription(String, '/as_amp/mission_select', self.mission_command_callback, 10)
            
            # Subscribers alterados para UInt8
            self.subs['go'] = self.create_subscription(UInt8, '/as_amp/res/go', lambda msg: self.uint8_repeater_callback(msg, 'go'), 10)
            self.subs['ready'] = self.create_subscription(UInt8, '/as_amp/res/as_ready', lambda msg: self.uint8_repeater_callback(msg, 'ready'), 10)
            self.subs['emergency'] = self.create_subscription(UInt8, '/as_amp/res/as_emergency', lambda msg: self.uint8_repeater_callback(msg, 'emergency'), 10)
            self.subs['go_finish'] = self.create_subscription(UInt8, '/as_amp/go/finish', self.go_finish_callback, 10)

            return TransitionCallbackReturn.SUCCESS
            
        except Exception as e:
            self.get_logger().error(f'❌ Erro ao configurar o nó: {e}')
            return TransitionCallbackReturn.ERROR

    def on_activate(self, state: State) -> TransitionCallbackReturn:
        try:
            self.get_logger().info('Ativando repeater node...')
            super().on_activate(state)
            return TransitionCallbackReturn.SUCCESS
            
        except Exception as e:
            self.get_logger().error(f'❌ Erro ao ativar o nó: {e}')
            return TransitionCallbackReturn.ERROR

    def on_deactivate(self, state: State) -> TransitionCallbackReturn:
        try:
            self.get_logger().info('Desativando repeater node...')
            super().on_deactivate(state)
            
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
            
            if self.timeout_timer is not None:
                self.timeout_timer.cancel()
                self.destroy_timer(self.timeout_timer)
                
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
            
            if self.timeout_timer is not None:
                self.timeout_timer.cancel()
                self.destroy_timer(self.timeout_timer)
            
            self.timeout_timer = self.create_timer(60.0, self.mission_timeout_callback)
            
        else:
            self.get_logger().warn(f'⚠️ Missão desconhecida: {mission_input}')

    def go_finish_callback(self, msg):
        """Recebe o sinal de término (UInt8) e dispara o segundo GoSignal."""
        # Avalia como verdadeiro se msg.data for 1 (ou > 0)
        if msg.data == 1 and self.sm_state == "WAIT_FINISH":
            pub_mission = self.pubs.get('mission_go')
            if pub_mission and pub_mission.is_activated:
                mission_msg = GoSignal()
                mission_msg.mission = self.current_mission_translated
                pub_mission.publish(mission_msg)
                self.get_logger().info('🏁 Sinal FINISH recebido (UInt8=1)! Segundo GoSignal publicado.')
                
                # Avança para COMPLETED para não repetir a publicação se receber outro 1
                self.sm_state = "COMPLETED"

    def uint8_repeater_callback(self, msg, pub_key):
        if pub_key in ['go', 'ready']:
            
            if self.sm_state == "WAIT_MISSION":
                return 

            # Traduz o UInt8 (0 ou 1) para o booleano da memória interna da State Machine
            if pub_key == 'go':
                self.res_go_state = (msg.data == 1)
            elif pub_key == 'ready':
                self.as_ready_state = (msg.data == 1)

            # 1º DISPARO: Quando recebe GO e READY dentro do tempo
            if self.sm_state == "WAIT_RES" and self.res_go_state and self.as_ready_state:
                self.sm_state = "WAIT_FINISH" 
                
                if self.timeout_timer is not None:
                    self.timeout_timer.cancel()
                    self.destroy_timer(self.timeout_timer)
                    self.timeout_timer = None
                
                pub_mission = self.pubs.get('mission_go')
                if pub_mission and pub_mission.is_activated:
                    mission_msg = GoSignal()
                    mission_msg.mission = self.current_mission_translated
                    pub_mission.publish(mission_msg)
                    self.get_logger().info('✅ AS_READY e GO recebidos! PRIMEIRO GoSignal publicado. Aguardando finish...')

            # Regra de Segurança: Aborta se cair o sinal (voltar para 0) em qualquer estado após o início
            elif self.sm_state in ["WAIT_FINISH", "COMPLETED"] and (not self.res_go_state or not self.as_ready_state):
                self.get_logger().warn('🚨 Sinal de GO ou READY caiu para 0! Voltando ao estado inicial.')
                self.sm_state = "WAIT_MISSION"
                self.current_mission_translated = "NONE"

        # Repassa a mensagem UInt8 para a saída, se o publisher estiver ativado
        if pub_key in self.pubs and self.pubs[pub_key].is_activated:
            self.pubs[pub_key].publish(msg)

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