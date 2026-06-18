import rclpy
from rclpy.node import Node
from src.can_reader import StateCanReader
from fs_msgs.msg import ControlCommand, GoSignal
from std_msgs.msg import Float32, UInt8, UInt16

class CanPublisherNode(Node):
    def __init__(self):
        super().__init__('CanPublisherNode')

        self.can_reader = StateCanReader()

        self.go_publisher = self.create_publisher(GoSignal, "/signal/go", 10)

        self.timer = self.create_timer(0.01, self.can_publish)

        self.uint8_publishers = {
            "/can/ready_to_drive": self.create_publisher(UInt8, "/can/ready_to_drive", 10),
            "/can/task_mode": self.create_publisher(UInt8, "/can/task_mode", 10),
            "/can/AS_status": self.create_publisher(UInt8, "/can/AS_status", 10),
            "/can/go_signal": self.create_publisher(UInt8, "/can/go_signal", 10)
        }

        self.float_publishers = {
            "/can/steering_angle": self.create_publisher(UInt16, "/can/steering_angle", 10)
        }

    def can_publish(self):
        message = self.can_reader.receive_message()
    
        if message == None:
            self.get_logger().debug(f'Nenhuma Mensagem Recebida')
            return
        
        can_data = self.can_reader.can_reader(message)

        self.publish_uint8_data(can_data)
        self.publish_float_data(can_data)

        go_data = can_data.get("go_state")
        self.get_logger().debug(f'{go_data}')  
        if go_data == 1:
            go_message = GoSignal()
            go_message.mission = "test"
            self.go_publisher.publish(go_message)

    def uint8_publish(self, can_data):
        uint8_signals = {
            "ready_to_drive": "/can/ready_to_drive",
            "task_mode": "/can/task_mode",
            "AS_status": "/can/AS_status",
            "go_signal": "/can/go_signal",
        }

        for signal, topic in uint8_signals:
            try:
                if can_data.get(signal):
                    msg = UInt8()
                    msg.data = int(can_data[signal])
                    self.uint8_publishers[topic].publish(msg)
                    self.get_logger().debug(f'Mensagem {msg.data} publicada para {topic}')
            except  Exception as e:
                self.get_logger().warn(f'Erro {e} ao publicar {signal}')


    def float_publish(self, can_data):
        float_signals = {
            "steering_angle": "/can/steering_angle",
        }
        for signal, topic in float_signals:
            try:
                if can_data.get(signal):
                    msg = Float32()
                    msg.data = float(can_data[signal])
                    self.float_publishers[topic].publish(msg)
                    self.get_logger().debug(f'Mensagem {msg.data} publicada para {topic}')
            except  Exception as e:
                self.get_logger().warn(f'Erro {e} ao publicar {signal}')


def main(args=None):
    rclpy.init(args=args)
    node = CanPublisherNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
