import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool
from visualization_msgs.msg import Marker, MarkerArray
from geometry_msgs.msg import Point
import math


class VisualizerNode(Node):
    def __init__(self):
        super().__init__('visualizer_node')

        # Subscribe to system status
        self.weed_sub = self.create_subscription(
            Bool, '/weed_detected', self.weed_callback, 10)
        self.spray_sub = self.create_subscription(
            String, '/sprayer_status', self.spray_callback, 10)

        # Publish markers for RViz
        self.marker_pub = self.create_publisher(
            MarkerArray, '/visualization_markers', 10)

        self.weed_detected = False
        self.spraying = False
        self.timer = self.create_timer(0.1, self.publish_markers)
        self.get_logger().info('Visualizer node started!')

    def weed_callback(self, msg):
        self.weed_detected = msg.data

    def spray_callback(self, msg):
        self.spraying = 'SPRAYING' in msg.data

    def publish_markers(self):
        markers = MarkerArray()

        # Robot body marker
        robot = Marker()
        robot.header.frame_id = 'map'
        robot.header.stamp = self.get_clock().now().to_msg()
        robot.ns = 'robot'
        robot.id = 0
        robot.type = Marker.CUBE
        robot.action = Marker.ADD
        robot.pose.position.x = 0.0
        robot.pose.position.y = 0.0
        robot.pose.position.z = 0.1
        robot.pose.orientation.w = 1.0
        robot.scale.x = 0.6
        robot.scale.y = 0.4
        robot.scale.z = 0.15
        robot.color.r = 0.1
        robot.color.g = 0.6
        robot.color.b = 0.1
        robot.color.a = 1.0
        markers.markers.append(robot)

        # Weed marker — red when detected
        weed = Marker()
        weed.header.frame_id = 'map'
        weed.header.stamp = self.get_clock().now().to_msg()
        weed.ns = 'weed'
        weed.id = 1
        weed.type = Marker.CYLINDER
        weed.action = Marker.ADD
        weed.pose.position.x = 2.0
        weed.pose.position.y = 0.0
        weed.pose.position.z = 0.25
        weed.pose.orientation.w = 1.0
        weed.scale.x = 0.16
        weed.scale.y = 0.16
        weed.scale.z = 0.5
        if self.weed_detected:
            # Flash red when detected
            weed.color.r = 1.0
            weed.color.g = 0.0
            weed.color.b = 0.0
        else:
            # Green when not detected
            weed.color.r = 0.0
            weed.color.g = 0.8
            weed.color.b = 0.0
        weed.color.a = 1.0
        markers.markers.append(weed)

        # Spray marker — blue cylinder when spraying
        spray = Marker()
        spray.header.frame_id = 'map'
        spray.header.stamp = self.get_clock().now().to_msg()
        spray.ns = 'spray'
        spray.id = 2
        spray.type = Marker.CYLINDER
        spray.action = Marker.ADD
        spray.pose.position.x = 0.0
        spray.pose.position.y = 0.0
        spray.pose.position.z = -0.1
        spray.pose.orientation.w = 1.0
        spray.scale.x = 0.1
        spray.scale.y = 0.1
        spray.scale.z = 0.2
        if self.spraying:
            spray.color.r = 0.0
            spray.color.g = 0.5
            spray.color.b = 1.0
            spray.color.a = 1.0
        else:
            spray.color.a = 0.1
            spray.color.b = 1.0
        markers.markers.append(spray)

        # Status text
        text = Marker()
        text.header.frame_id = 'map'
        text.header.stamp = self.get_clock().now().to_msg()
        text.ns = 'status'
        text.id = 3
        text.type = Marker.TEXT_VIEW_FACING
        text.action = Marker.ADD
        text.pose.position.x = 0.0
        text.pose.position.y = 0.0
        text.pose.position.z = 1.0
        text.pose.orientation.w = 1.0
        text.scale.z = 0.3
        if self.spraying:
            text.text = 'SPRAYING!'
            text.color.r = 0.0
            text.color.g = 0.5
            text.color.b = 1.0
        elif self.weed_detected:
            text.text = 'WEED DETECTED!'
            text.color.r = 1.0
            text.color.g = 0.0
            text.color.b = 0.0
        else:
            text.text = 'Scanning...'
            text.color.r = 1.0
            text.color.g = 1.0
            text.color.b = 1.0
        text.color.a = 1.0
        markers.markers.append(text)

        self.marker_pub.publish(markers)


def main(args=None):
    rclpy.init(args=args)
    rclpy.spin(VisualizerNode())
    rclpy.shutdown()
