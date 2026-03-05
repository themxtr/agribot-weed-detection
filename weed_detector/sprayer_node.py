import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool, String
class SprayerNode(Node):
	def __init__(self):
		super().__init__('sprayer_node')
		self.spraying    = False
		self.spray_timer = None
		self.weed_sub    = self.create_subscription(
			Bool, '/weed_detected', self.on_weed, 10)
		self.status_pub  = self.create_publisher(String, '/sprayer_status', 10)
		self.get_logger().info('Sprayer Node ready.')
	def on_weed(self, msg):
		if msg.data and not self.spraying:
			self.activate()
	def activate(self):
		self.spraying = True
		self.publish_status('SPRAYING: Pesticide dispensed!')
		self.get_logger().info('SPRAYER ACTIVATED')
		self.spray_timer = self.create_timer(3.0, self.deactivate)
	def deactivate(self):
		self.spraying = False
		self.publish_status('IDLE')
		self.get_logger().info('Sprayer off.')
		if self.spray_timer:
			self.destroy_timer(self.spray_timer)
			self.spray_timer = None
	def publish_status(self, text):
		msg = String(); msg.data = text
		self.status_pub.publish(msg)
def main(args=None):
	rclpy.init(args=args)
	rclpy.spin(SprayerNode())
	rclpy.shutdown()
