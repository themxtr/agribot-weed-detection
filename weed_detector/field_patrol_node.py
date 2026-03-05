import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool
from visualization_msgs.msg import Marker, MarkerArray
from geometry_msgs.msg import Point
import math


# Define the field layout
PLANTS = [
    (2.0, 0.0), (2.0, 1.5), (2.0, -1.5),
    (4.0, 0.0), (4.0, 1.5), (4.0, -1.5),
    (6.0, 0.0), (6.0, 1.5), (6.0, -1.5),
]

WEEDS = [
    (2.0, 1.5),
    (4.0, 0.0),
    (6.0, -1.5),
]

# Patrol waypoints (robot follows this path)
WAYPOINTS = [
    (0.0,  0.0),   # Start
    (2.0,  2.0),   # Row 1 top
    (2.0,  0.0),   # Row 1 mid
    (2.0, -2.0),   # Row 1 bot
    (4.0, -2.0),   # Row 2 bot
    (4.0,  0.0),   # Row 2 mid
    (4.0,  2.0),   # Row 2 top
    (6.0,  2.0),   # Row 3 top
    (6.0,  0.0),   # Row 3 mid
    (6.0, -2.0),   # Row 3 bot
    (0.0,  0.0),   # Return to start
]

ROBOT_SPEED = 0.03   # units per tick
SPRAY_RADIUS = 0.8   # how close to weed to trigger spray
SPRAY_TICKS = 30     # how long spraying lasts


class FieldPatrolNode(Node):
    def __init__(self):
        super().__init__('field_patrol_node')

        self.marker_pub = self.create_publisher(
            MarkerArray, '/visualization_markers', 10)
        self.status_pub = self.create_publisher(
            String, '/sprayer_status', 10)
        self.weed_pub = self.create_publisher(
            Bool, '/weed_detected', 10)

        # Robot state
        self.robot_x = 0.0
        self.robot_y = 0.0
        self.waypoint_idx = 0
        self.mission_done = False
        self.returned_home = False

        # Sprayer state
        self.spraying = False
        self.spray_ticks = 0

        # Weed state — track which are alive
        self.weed_alive = {i: True for i in range(len(WEEDS))}

        self.timer = self.create_timer(0.05, self.tick)
        self.get_logger().info('Field patrol started! Robot beginning patrol...')

    def tick(self):
        if self.returned_home:
            self.publish_markers()
            return

        # Move robot toward current waypoint
        if self.waypoint_idx < len(WAYPOINTS):
            tx, ty = WAYPOINTS[self.waypoint_idx]
            dx = tx - self.robot_x
            dy = ty - self.robot_y
            dist = math.sqrt(dx**2 + dy**2)

            if dist < 0.05:
                # Reached waypoint
                self.waypoint_idx += 1
                if self.waypoint_idx >= len(WAYPOINTS):
                    self.returned_home = True
                    self.mission_done = True
                    self.get_logger().info('Mission complete! Robot returned to start.')
                    self.publish_status('MISSION COMPLETE')
            else:
                # Move toward waypoint
                self.robot_x += (dx / dist) * ROBOT_SPEED
                self.robot_y += (dy / dist) * ROBOT_SPEED

        # Check proximity to weeds
        for i, (wx, wy) in enumerate(WEEDS):
            if not self.weed_alive[i]:
                continue
            dist = math.sqrt(
                (self.robot_x - wx)**2 + (self.robot_y - wy)**2)
            if dist < SPRAY_RADIUS and not self.spraying:
                self.start_spraying(i)

        # Handle spraying countdown
        if self.spraying:
            self.spray_ticks -= 1
            if self.spray_ticks <= 0:
                self.stop_spraying()

        self.publish_markers()

    def start_spraying(self, weed_idx):
        self.spraying = True
        self.spray_ticks = SPRAY_TICKS
        self.current_weed = weed_idx
        self.weed_alive[weed_idx] = False  # Kill weed immediately
        self.get_logger().info(
            f'SPRAYING weed {weed_idx} at {WEEDS[weed_idx]}!')
        self.publish_status('SPRAYING: Pesticide dispensed!')
        weed_msg = Bool()
        weed_msg.data = True
        self.weed_pub.publish(weed_msg)

    def stop_spraying(self):
        self.spraying = False
        self.get_logger().info('Spraying complete. Resuming patrol.')
        self.publish_status('IDLE')
        weed_msg = Bool()
        weed_msg.data = False
        self.weed_pub.publish(weed_msg)

    def publish_status(self, text):
        msg = String()
        msg.data = text
        self.status_pub.publish(msg)

    def publish_markers(self):
        markers = MarkerArray()
        now = self.get_clock().now().to_msg()

        # ── Ground plane ──
        ground = Marker()
        ground.header.frame_id = 'map'
        ground.header.stamp = now
        ground.ns = 'ground'
        ground.id = 0
        ground.type = Marker.CUBE
        ground.action = Marker.ADD
        ground.pose.position.x = 4.0
        ground.pose.position.y = 0.0
        ground.pose.position.z = -0.05
        ground.pose.orientation.w = 1.0
        ground.scale.x = 10.0
        ground.scale.y = 6.0
        ground.scale.z = 0.05
        ground.color.r = 0.4
        ground.color.g = 0.3
        ground.color.b = 0.1
        ground.color.a = 1.0
        markers.markers.append(ground)

        # ── Plants ──
        for i, (px, py) in enumerate(PLANTS):
            m = Marker()
            m.header.frame_id = 'map'
            m.header.stamp = now
            m.ns = 'plants'
            m.id = i
            m.type = Marker.CYLINDER
            m.action = Marker.ADD
            m.pose.position.x = px
            m.pose.position.y = py
            m.pose.position.z = 0.2
            m.pose.orientation.w = 1.0
            m.scale.x = 0.2
            m.scale.y = 0.2
            m.scale.z = 0.4
            m.color.r = 0.0
            m.color.g = 0.7
            m.color.b = 0.0
            m.color.a = 1.0
            markers.markers.append(m)

        # ── Weeds ──
        for i, (wx, wy) in enumerate(WEEDS):
            m = Marker()
            m.header.frame_id = 'map'
            m.header.stamp = now
            m.ns = 'weeds'
            m.id = i
            m.type = Marker.CYLINDER
            m.action = Marker.ADD
            m.pose.position.x = wx
            m.pose.position.y = wy
            m.pose.position.z = 0.15

            if not self.weed_alive[i]:
                # Weed is dead — make it flat and brown
                m.pose.position.z = 0.01
                m.scale.x = 0.25
                m.scale.y = 0.25
                m.scale.z = 0.02
                m.color.r = 0.3
                m.color.g = 0.2
                m.color.b = 0.0
                m.color.a = 0.5
            elif self.spraying and hasattr(self, 'current_weed') \
                    and self.current_weed == i:
                # Currently being sprayed — flash red
                m.scale.x = 0.25
                m.scale.y = 0.25
                m.scale.z = 0.3
                m.color.r = 1.0
                m.color.g = 0.0
                m.color.b = 0.0
                m.color.a = 1.0
            else:
                # Alive weed — bright yellow-green
                m.scale.x = 0.25
                m.scale.y = 0.25
                m.scale.z = 0.3
                m.color.r = 0.8
                m.color.g = 0.8
                m.color.b = 0.0
                m.color.a = 1.0
            m.pose.orientation.w = 1.0
            markers.markers.append(m)

        # ── Patrol path line ──
        path = Marker()
        path.header.frame_id = 'map'
        path.header.stamp = now
        path.ns = 'path'
        path.id = 0
        path.type = Marker.LINE_STRIP
        path.action = Marker.ADD
        path.pose.orientation.w = 1.0
        path.scale.x = 0.03
        path.color.r = 0.5
        path.color.g = 0.5
        path.color.b = 1.0
        path.color.a = 0.5
        for wx, wy in WAYPOINTS:
            pt = Point()
            pt.x = wx
            pt.y = wy
            pt.z = 0.01
            path.points.append(pt)
        markers.markers.append(path)

        # ── Robot body ──
        robot = Marker()
        robot.header.frame_id = 'map'
        robot.header.stamp = now
        robot.ns = 'robot'
        robot.id = 0
        robot.type = Marker.CUBE
        robot.action = Marker.ADD
        robot.pose.position.x = self.robot_x
        robot.pose.position.y = self.robot_y
        robot.pose.position.z = 0.1
        robot.pose.orientation.w = 1.0
        robot.scale.x = 0.4
        robot.scale.y = 0.3
        robot.scale.z = 0.15
        robot.color.r = 0.1
        robot.color.g = 0.4
        robot.color.b = 0.9
        robot.color.a = 1.0
        markers.markers.append(robot)

        # ── Spray effect ──
        if self.spraying:
            spray = Marker()
            spray.header.frame_id = 'map'
            spray.header.stamp = now
            spray.ns = 'spray_effect'
            spray.id = 0
            spray.type = Marker.SPHERE
            spray.action = Marker.ADD
            spray.pose.position.x = self.robot_x
            spray.pose.position.y = self.robot_y
            spray.pose.position.z = 0.2
            spray.pose.orientation.w = 1.0
            spray.scale.x = 1.5
            spray.scale.y = 1.5
            spray.scale.z = 0.3
            spray.color.r = 0.0
            spray.color.g = 0.7
            spray.color.b = 1.0
            spray.color.a = 0.4
            markers.markers.append(spray)

        # ── Status text ──
        text = Marker()
        text.header.frame_id = 'map'
        text.header.stamp = now
        text.ns = 'status'
        text.id = 0
        text.type = Marker.TEXT_VIEW_FACING
        text.action = Marker.ADD
        text.pose.position.x = 3.0
        text.pose.position.y = 3.5
        text.pose.position.z = 1.5
        text.pose.orientation.w = 1.0
        text.scale.z = 0.4

        weeds_left = sum(self.weed_alive.values())
        if self.returned_home:
            text.text = 'MISSION COMPLETE! All weeds sprayed.'
            text.color.r = 0.0
            text.color.g = 1.0
            text.color.b = 0.0
        elif self.spraying:
            text.text = 'SPRAYING WEED!'
            text.color.r = 0.0
            text.color.g = 0.5
            text.color.b = 1.0
        else:
            text.text = f'Patrolling... Weeds left: {weeds_left}'
            text.color.r = 1.0
            text.color.g = 1.0
            text.color.b = 1.0
        text.color.a = 1.0
        markers.markers.append(text)

        self.marker_pub.publish(markers)


def main(args=None):
    rclpy.init(args=args)
    rclpy.spin(FieldPatrolNode())
    rclpy.shutdown()
