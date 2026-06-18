import rclpy
from rclpy.node import Node
from src.can_reader import StateCanReader
from fs_msgs.msg import ControlCommand, GoSignal
from std_msgs.msg import Float32, UInt8, UInt16

class CanPublisherNode(Node):
    def __init__(self):
        super().__init__('can_publisher_node')

        self.can_reader = StateCanReader()

        self.go_publisher = self.create_publisher(GoSignal, "/signal/go", 10)

        self.timer = self.create_timer(0.01, self.can_publish)

    def can_publish(self):
        message = self.can_reader.receive_message()
    
        if message == None:
            self.get_logger().debug(f'Nenhuma Mensagem Recebida')
            return
        
        data = self.can_reader.can_reader(message)

        go_data = data.get("Go_State")
        self.get_logger()_.debug(f'{go_data}')  
        if go_data == 1:
            go_message = GoSignal()
            go_message.mission = "test"
            self.go_publisher.publish(go_message)

def main(args=None):
    rclpy.init(args=args)
    node = CanPublisherNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
