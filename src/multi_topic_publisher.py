import os

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class MultiTopicPublisher(Node):
    def __init__(self):
        super().__init__("multi_topic_publisher")

        # Read environment variables
        topics_env = os.getenv("TOPICS", "/chatter")
        payload = os.getenv("PAYLOAD", "hello from ROS2 in k8s")
        freq_hz_str = os.getenv("FREQUENCY_HZ", "1.0")

        try:
            freq_hz = float(freq_hz_str)
            if freq_hz <= 0:
                raise ValueError("Frequency must be > 0")
        except Exception as e:
            self.get_logger().warn(
                f"Invalid FREQUENCY_HZ='{freq_hz_str}', "
                f"defaulting to 1.0 Hz. Error: {e}"
            )
            freq_hz = 1.0

        self.topics = [t.strip() for t in topics_env.split(",") if t.strip()]
        if not self.topics:
            self.get_logger().warn(
                "No valid topics in TOPICS env; defaulting to ['/chatter']"
            )
            self.topics = ["/chatter"]

        self.payload = payload
        self.period = 1.0 / freq_hz

        # Create publishers for each topic
        self.publishers = []
        for t in self.topics:
            pub = self.create_publisher(String, t, 10)
            self.publishers.append(pub)
            self.get_logger().info(f"Created publisher on topic: {t}")

        # Timer for periodic publishing
        self.timer = self.create_timer(self.period, self.timer_callback)

        self.get_logger().info(
            f"MultiTopicPublisher node started.\n"
            f"  Topics   : {self.topics}\n"
            f"  Payload  : '{self.payload}'\n"
            f"  Frequency: {freq_hz} Hz (period={self.period}s)"
        )

    def timer_callback(self):
        msg = String()
        msg.data = self.payload
        for pub, topic in zip(self.publishers, self.topics):
            pub.publish(msg)
            # debug log (can be noisy at high frequency)
            self.get_logger().debug(f"Published to {topic}: {msg.data}")


def main(args=None):
    rclpy.init(args=args)
    node = MultiTopicPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Shutting down MultiTopicPublisher (KeyboardInterrupt).")
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
