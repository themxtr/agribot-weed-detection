import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
import numpy as np


class FakeCameraNode(Node):
    def __init__(self):
        super().__init__('fake_camera_node')
        self.publisher = self.create_publisher(Image, '/camera/image_raw', 10)
        self.timer = self.create_timer(1.0, self.publish_frame)
        self.frame_count = 0
        self.get_logger().info('Fake camera started!')

    def publish_frame(self):
        height, width = 480, 640
        frame = np.zeros((height, width, 3), dtype=np.uint8)

        # BGR background (dark blue-grey)
        frame[:, :, 0] = 110  # B
        frame[:, :, 1] = 82   # G
        frame[:, :, 2] = 42   # R

        # Show weed every other second
        show_weed = (self.frame_count % 2 == 0)

        if show_weed:
            # Draw bright green circle in BGR: G=220, B=0, R=0
            cy, cx, r = 250, 320, 60
            y_idx, x_idx = np.ogrid[0:height, 0:width]
            circle_mask = ((x_idx - cx)**2 + (y_idx - cy)**2) <= r**2
            frame[circle_mask, 0] = 0    # B
            frame[circle_mask, 1] = 220  # G
            frame[circle_mask, 2] = 0    # R
            self.get_logger().info('WEED IN FRAME (frame ' + str(self.frame_count) + ')')
        else:
            self.get_logger().info('clear field (frame ' + str(self.frame_count) + ')')

        self.frame_count += 1

        msg = Image()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.height = height
        msg.width = width
        msg.encoding = 'bgr8'
        msg.step = width * 3
        msg.data = frame.tobytes()
        self.publisher.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    rclpy.spin(FakeCameraNode())
    rclpy.shutdown()
