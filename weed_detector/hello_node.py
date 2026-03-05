import rclpy
from rclpy.node import Node

class HelloNode(Node):
	def __init__(self):
		super().__init__('hello_node')
		self.get_logger().info('AgriBot is alive!')
		self.create_timer(1.0, self.tick)
	def tick(self):
		self.get_logger().info('Scanning for weeds...')
def main(args=None):
	rclpy.init(args=args)
	rclpy.spin(HelloNode())
	rclpy.shutdown()
