#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool
from fs_msgs.msg import GoSignal

import sys
import select
import tty
import termios

class TecladoCanNode(Node):
    def __init__(self):
        super().__init__('teclado_can_node')
        
        # Publishers para Mission Select
        self.pub_mission_select = self.create_publisher(String, '/as_amp/mission_select', 10)
        
        # Publishers para Sinais de Estado (Usando std_msgs/Bool)
        self.pub_go = self.create_publisher(Bool, '/as_amp/res/go', 10)
        self.pub_as_ready = self.create_publisher(Bool, '/as_amp/res/as_ready', 10)
        self.pub_as_emergency = self.create_publisher(Bool, '/as_amp/res/as_emergency', 10)

        # Instruções no terminal
        self.get_logger().info('--- Nó de Teste de Teclado (CAN Simulator) Iniciado ---')
        self.get_logger().info('--- MISSIONS ---')
        self.get_logger().info(' [q] -> Publicar "CHECK" em /as_amp/mission_select')
        self.get_logger().info(' [w] -> Publicar "CALIBRATION" em /as_amp/mission_select')
        self.get_logger().info(' [e] -> Publicar "TRACKDRIVE" em /as_amp/mission_select')
        self.get_logger().info('--- SIGNALS ---')
        self.get_logger().info(' [c] -> Publicar True(1) em /as_amp/go')
        self.get_logger().info(' [v] -> Publicar True(1) em /as_amp/as_ready')
        self.get_logger().info(' [b] -> Publicar True(1) em /as_amp/as_emergency')
        self.get_logger().info('Aperte "Ctrl+C" para sair.')

    def disparar_mission_select(self, comando):
        # Publica String
        msg_str = String()
        msg_str.data = comando
        self.pub_mission_select.publish(msg_str)
        
        self.get_logger().info(f'🚀 Mission: "{comando}" enviada!')

    def disparar_booleano(self, publisher, topic_name):
        msg = Bool()
        msg.data = True
        publisher.publish(msg)
        self.get_logger().info(f'✅ Sinal True (1) enviado no tópico {topic_name}!')


# Função para ler uma única tecla do terminal sem precisar dar Enter
def capturar_tecla(settings):
    tty.setraw(sys.stdin.fileno())
    select.select([sys.stdin], [], [], 0)
    key = sys.stdin.read(1)
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key


def main(args=None):
    rclpy.init(args=args)
    node = TecladoCanNode()
    
    # Salva as configurações originais do terminal
    settings = termios.tcgetattr(sys.stdin)

    try:
        while rclpy.ok():
            # Captura a tecla e converte para minúscula para facilitar a comparação
            tecla = capturar_tecla(settings).lower()
            
            if tecla == 'q':
                node.disparar_mission_select("CHECK")
            elif tecla == 'w':
                node.disparar_mission_select("CALIBRATION")
            elif tecla == 'e':
                node.disparar_mission_select("TRACKDRIVE")
            elif tecla == 'c':
                node.disparar_booleano(node.pub_go, "/as_amp/go")
            elif tecla == 'v':
                node.disparar_booleano(node.pub_as_ready, "/as_amp/as_ready")
            elif tecla == 'b':
                node.disparar_booleano(node.pub_as_emergency, "/as_amp/as_emergency")
            elif tecla == '\x03': # Código hexadecimal para Ctrl+C
                break
                
    except Exception as e:
        print(e)
    finally:
        # Restaura o terminal para o normal antes de fechar
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()