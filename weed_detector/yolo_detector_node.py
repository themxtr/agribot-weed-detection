import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String, Bool
import numpy as np


class YoloDetectorNode(Node):
    def __init__(self):
        super().__init__('yolo_detector_node')
        self.image_sub = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10
        )
        self.detection_pub = self.create_publisher(Bool, '/weed_detected', 10)
        self.status_pub = self.create_publisher(String, '/detection_status', 10)
        self.get_logger().info('Weed Detector ready!')

    def image_callback(self, msg):
        frame = np.frombuffer(msg.data, dtype=np.uint8).reshape(
            (msg.height, msg.width, 3))

        b = frame[:, :, 0].astype(int)
        g = frame[:, :, 1].astype(int)
        r = frame[:, :, 2].astype(int)

        green_mask = (g > 150) & (b < 50) & (r < 50)
        count = int(np.sum(green_mask))

        detected = count > 100
        status = 'WEED:' + str(count) + 'px' if detected else 'clear'

        det_msg = Bool()
        det_msg.data = detected
        self.detection_pub.publish(det_msg)

        sta_msg = String()
        sta_msg.data = status
        self.status_pub.publish(sta_msg)

        self.get_logger().info('green=' + str(count) + ' detected=' + str(detected))


def main(args=None):
    rclpy.init(args=args)
    rclpy.spin(YoloDetectorNode())
    rclpy.shutdown()
