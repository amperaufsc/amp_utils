#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from fs_msgs.msg import GoSignal

import sys
import select
import tty
import termios

class TecladoCanNode(Node):
    def __init__(self):
        super().__init__('teclado_can_node')
        
        # Cria os publishers para os tópicos específicos
        self.pub_mission_select_go = self.create_publisher(GoSignal, '/as_amp/mission_select/go', 10)
        self.pub_mission_select = self.create_publisher(String, '/can/autonomous_mode', 10)
        self.pub_go = self.create_publisher(String, '/as_amp/go', 10)
        self.pub_finished = self.create_publisher(String, '/as_amp/finished', 10)

        # Instruções no terminal
        self.get_logger().info('--- Nó de Teste de Teclado Iniciado ---')
        self.get_logger().info('Aperte [q] para publicar "CHECK" em /as_amp/mission_select')
        self.get_logger().info('Aperte [w] para publicar "CALIBRATION" em /as_amp/mission_select')
        self.get_logger().info('Aperte [e] para publicar "TRACKDRIVE" em /as_amp/mission_select')
        self.get_logger().info('Aperte [v] para publicar "GO" em /as_amp/go')
        self.get_logger().info('Aperte [c] para publicar "FINISHED" em /as_amp/finished')
        self.get_logger().info('Aperte "Ctrl+C" para sair.')

    def disparar_mission_select(self, comando):
        msg = String()
        msg.data = comando
        self.pub_mission_select.publish(msg)
        go = GoSignal()
        go.mission = comando
        self.pub_mission_select_go.publish(go)
        self.get_logger().info(f'🚀 Mensagem "{comando}" enviada no tópico /as_amp/mission_select!')

    def disparar_go(self, comando):
        msg = String()
        msg.data = comando
        self.pub_go.publish(msg)
        self.get_logger().info(f'🚀 Mensagem "{comando}" enviada no tópico /as_amp/go!')

    def disparar_finished(self, comando):
        msg = String()
        msg.data = comando
        self.pub_finished.publish(msg)
        self.get_logger().info(f'🚀 Mensagem "{comando}" enviada no tópico /as_amp/finished!')


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
                node.disparar_mission_select("trackdrive")
            elif tecla == 'v':
                node.disparar_go("GO")
            elif tecla == 'c':
                node.disparar_finished("FINISHED")
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