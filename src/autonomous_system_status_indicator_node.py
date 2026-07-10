#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
from smacc2_msgs.msg import SmaccStatus
from assi_control.assi_control import Control


class AutonomousSystemStatusIndicator(Node):
    def __init__(self):
        super().__init__('autonomous_system_status_indicator')
        self.states = {
            "st_AsOff": [[0, 0, 0], 0],
            "st_AsDriving": [[1, 0, 0,], 0],
            "st_AsReady": [[1, 0, 0], 1],
            "st_AsEmergency": [[0, 0, 1], 1],
            "st_AsFinished": [[0, 0, 1], 0]
        }

        self.yellowPin = 35
        self.greenPin = 37
        self.bluePin = 39
        self.command = [0, 0, 0, 0]
        self.blink = 0
        self.count = 1

        self.control = Control(self.yellowPin, self.greenPin, self.bluePin)

        self.subscription = self.create_subscription(SmaccStatus, '/Amp_sm/smacc/status', self.sm_callback, 10)

        self.pub_sensor = self.create_publisher(Float32, 'sensor/value', 10)

        self.timer = self.create_timer(1/2, self.timer_callback)

    def timer_callback(self):
        try:
            self.count = (self.count + 1)%2
            if self.count == 1 and self.blink == 1:
                self.control.update_leds([0, 0, 0])
                return
            self.control.update_leds(self.command)
        except Exception as e:
            self.get_logger().error(f"{e}")

    def sm_callback(self, message):
        self.command, self.blink = self.states[message.state_name]
        self.count = 1

def main(args=None):
    rclpy.init()
    autonomous_system_status_indicator = AutonomousSystemStatusIndicator()
    try:
        rclpy.spin(autonomous_system_status_indicator)
    except:
        autonomous_system_status_indicator.control.shutdown()

    finally:
        autonomous_system_status_indicator.destroy_node()
        rclpy.shutdown()
        autonomous_system_status_indicator.can.can_listener.bus.shutdown()


if __name__ == '__main__':
    main()