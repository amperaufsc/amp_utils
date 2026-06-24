#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from can_bus.can_reader import StateCanReader
from fs_msgs.msg import ControlCommand, GoSignal
from std_msgs.msg import Float32, UInt8, UInt16

class CanPublisherNode(Node):
    def __init__(self):
        super().__init__('can_publisher_node')
        self.can_reader = StateCanReader()

        self.go_publisher = self.create_publisher(GoSignal, "/signal/go", 10)

        self.timer = self.create_timer(0.01, self.can_publish)

        self.uint8_publishers = {
            #Painel
            "/can/ready_to_drive": self.create_publisher(UInt8, "/can/ready_to_drive", 10),
            "/can/autonomous_mode": self.create_publisher(UInt8, "/can/autonomous_mode", 10),
            "/can/page_id": self.create_publisher(UInt8, "/can/page_id", 10),

            #RES
            "/can/AS_status": self.create_publisher(UInt8, "/can/AS_status", 10),
            "/can/go_signal": self.create_publisher(UInt8, "/can/go_signal", 10),
            "/can/emergency": self.create_publisher(UInt8, "/can/emergency", 10),

            #ECU
            "/can/inverter_status": self.create_publisher(UInt8, "/can/inverter_status", 10),
            "/can/current_state": self.create_publisher(UInt8, "/can/current_state", 10),
            "/can/tms_error_code": self.create_publisher(UInt8, "/can/tms_error_code", 10),
            "/can/inverter_error_code": self.create_publisher(UInt8, "/can/inverter_error_code", 10),

            "/can/max_temperature": self.create_publisher(UInt8, "/can/max_temperature", 10),
            "/can/brake_switch": self.create_publisher(UInt8, "/can/brake_switch", 10),
            "/can/brake_pedal": self.create_publisher(UInt8, "/can/brake_pedal", 10),
            "/can/accelerator_pedal": self.create_publisher(UInt8, "/can/accelerator_pedal", 10),
            "/can/state_of_charge": self.create_publisher(UInt8, "/can/state_of_charge", 10),
            "/can/max_cell_voltage": self.create_publisher(UInt8, "/can/max_cell_voltage", 10),
            "/can/avg_cell_voltage": self.create_publisher(UInt8, "/can/avg_cell_voltage", 10),
            "/can/min_cell_voltage": self.create_publisher(UInt8, "/can/min_cell_voltage", 10),
        }

        self.uint16_publishers = {
            #ECU
            "/can/control_word": self.create_publisher(UInt16, "/can/control_word", 10),
            "/can/ecu_error_code": self.create_publisher(UInt16, "/can/ecu_error_code", 10),

            "/can/inverter_temperature": self.create_publisher(UInt16, "/can/inverter_temperature", 10),
            "/can/motor_torque": self.create_publisher(UInt16, "/can/motor_torque", 10),
            "/can/motor_temperature": self.create_publisher(UInt16, "/can/motor_temperature", 10),
            "/can/motor_rpm": self.create_publisher(UInt16, "/can/motor_rpm", 10),
        }

        self.float_publishers = {
            #DataLogger
            "/can/steering_angle": self.create_publisher(Float32, "/can/steering_angle", 10),

            "/can/encoder_rear_left": self.create_publisher(Float32, "/can/encoder_rear_left", 10),
            "/can/encoder_rear_right": self.create_publisher(Float32, "/can/encoder_rear_right", 10),

            "/can/encoder_front_left": self.create_publisher(Float32, "/can/encoder_front_left", 10),
            "/can/encoder_front_right": self.create_publisher(Float32, "/can/encoder_front_right", 10),

            "/can/accel_x": self.create_publisher(Float32, "/can/accel_x", 10),
            "/can/accel_y": self.create_publisher(Float32, "/can/accel_y", 10),
            "/can/accel_z": self.create_publisher(Float32, "/can/accel_z", 10),

            #ECU
            "/can/battery_current": self.create_publisher(Float32, "/can/battery_current", 10),
            "/can/battery_voltage": self.create_publisher(Float32, "/can/battery_voltage", 10),
            "/can/inverter_current": self.create_publisher(Float32, "/can/inverter_current", 10),
            "/can/inverter_voltage": self.create_publisher(Float32, "/can/inverter_voltage", 10),
        }
    def can_publish(self):
        try:
            message = self.can_reader.receive_message()
        
            if message == None:
                self.get_logger().info(f'Nenhuma Mensagem Recebida')
                return
            
            can_data = self.can_reader.can_reader(message)
            self.get_logger().debug(f'{can_data}')

            self.uint8_publish(can_data)
            self.uint16_publish(can_data)
            self.float_publish(can_data)

            mode = can_data.get("AutonomousMode")
            self.get_logger().debug(f'{mode}')  
            if mode is not None:
                go_message = GoSignal() 
                go_message.mission = mode
                self.go_publisher.publish(go_message)
        except Exception as e:
            self.get_logger().debug(f'{e}')

    def uint8_publish(self, can_data):
        uint8_signals = {
            #painel
            "ReadyToDrive": "/can/ready_to_drive",
            "AutonomousMode": "/can/autonomous_mode",
            "PageID":"/can/page_id",

            #RES
            "ASStatus": "/can/AS_status",
            "GOSignal": "/can/go_signal",
            "ASEmergency": "/can/emergency",

            #ECU
            "InverterStatus": "/can/inverter_status",
            "CurrentState": "/can/current_state",
            "TMSErrorCode": "/can/tms_error_code",
            "InverterErrorCode": "/can/inverter_error_code",

            "MaxTemperature": "/can/max_temperature",
            "BrakeSwitch": "/can/brake_switch",
            "BrakePedal": "/can/brake_pedal",
            "AcceleratorPedal": "/can/accelerator_pedal",
            "StateOfCharge": "/can/state_of_charge",
            "MaxCellVoltage": "/can/max_cell_voltage",
            "AvgCellVoltage": "/can/avg_cell_voltage",
            "MinCellVoltage": "/can/min_cell_voltage",
        }

        for signal, topic in uint8_signals.items():
            try:
                if signal in can_data and can_data[signal] is not None:
                    msg = UInt8()
                    msg.data = int(can_data[signal])
                    self.uint8_publishers[topic].publish(msg)
                    self.get_logger().debug(f'Mensagem {msg.data} publicada para {topic}')
            except  Exception as e:
                self.get_logger().warn(f'Erro {e} ao publicar {signal}')

    def uint16_publish(self, can_data):
        uint16_signals = {
            #ECU
            "ControlWord": "/can/control_word",
            "ECUErrorCode": "/can/ecu_error_code",

            "InverterTemperature": "/can/inverter_temperature",
            "MotorTorque": "/can/motor_torque",
            "MotorTemperature": "/can/motor_temperature",
            "MotorRPM": "/can/motor_rpm",
        }
        for signal, topic in uint16_signals.items():
            try:
                if signal in can_data and can_data[signal] is not None:
                    msg = UInt16()
                    msg.data = int(can_data[signal])
                    self.uint16_publishers[topic].publish(msg)
                    self.get_logger().debug(f'Mensagem {msg.data} publicada para {topic}')
            except  Exception as e:
                self.get_logger().warn(f'Erro {e} ao publicar {signal}')


    def float_publish(self, can_data):
        float_signals = {
            # DataLogger
            "SteeringAngle": "/can/steering_angle",

            "EncoderRearLeft": "/can/encoder_rear_left",
            "EncoderRearRight": "/can/encoder_rear_right",

            "EncoderFrontLeft": "/can/encoder_front_left",
            "EncoderFrontRight": "/can/encoder_front_right",

            "AccelX": "/can/accel_x",
            "AccelY": "/can/accel_y",
            "AccelZ": "/can/accel_z",

            # ECU
            "BatteryCurrent": "/can/battery_current",
            "BatteryVoltage": "/can/battery_voltage",

            "InverterCurrent": "/can/inverter_current",
            "InverterVoltage": "/can/inverter_voltage",
        }
        for signal, topic in float_signals.items():
            try:
                if signal in can_data and can_data[signal] is not None:
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
