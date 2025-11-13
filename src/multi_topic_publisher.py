import os
import sys

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class MultiTopicPublisher(Node):
    def __init__(self):
        try:
            super().__init__("multi_topic_publisher")
            print("Node base class initialized")

            # Read environment variables
            topics_env = os.getenv("TOPICS", "/chatter")
            payload = os.getenv("PAYLOAD", "hello from ROS2 in k8s")
            freq_hz_str = os.getenv("FREQUENCY_HZ", "1.0")
            print(f"Environment variables - TOPICS: {topics_env}, PAYLOAD: {payload}, FREQUENCY_HZ: {freq_hz_str}")

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
            print(f"Creating publishers for topics: {self.topics}")
            self._publishers = []
            for t in self.topics:
                try:
                    pub = self.create_publisher(String, t, 10)
                    self._publishers.append(pub)
                    self.get_logger().info(f"Created publisher on topic: {t}")
                    print(f"Successfully created publisher for topic: {t}")
                except Exception as e:
                    self.get_logger().error(f"Failed to create publisher for topic {t}: {e}")
                    raise

            # Timer for periodic publishing
            print(f"Creating timer with period: {self.period}s")
            self.timer = self.create_timer(self.period, self.timer_callback)
            print("Timer created successfully")

            self.get_logger().info(
                f"MultiTopicPublisher node started.\n"
                f"  Topics   : {self.topics}\n"
                f"  Payload  : '{self.payload}'\n"
                f"  Frequency: {freq_hz} Hz (period={self.period}s)"
            )
            print("MultiTopicPublisher initialization complete")
        except Exception as e:
            print(f"Error during MultiTopicPublisher initialization: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            raise

    def timer_callback(self):
        msg = String()
        msg.data = self.payload
        for pub, topic in zip(self._publishers, self.topics):
            pub.publish(msg)
            # debug log (can be noisy at high frequency)
            self.get_logger().debug(f"Published to {topic}: {msg.data}")


def main(args=None):
    node = None
    ros_initialized = False
    
    # Log ROS_DOMAIN_ID if set
    ros_domain_id = os.getenv("ROS_DOMAIN_ID")
    if ros_domain_id:
        print(f"ROS_DOMAIN_ID is set to: {ros_domain_id}")
    else:
        print("ROS_DOMAIN_ID not set, using default (0)")
    
    try:
        print("Initializing ROS2...")
        rclpy.init(args=args)
        ros_initialized = True
        print("ROS2 initialized successfully")
        
        print("Creating MultiTopicPublisher node...")
        node = MultiTopicPublisher()
        print("Node created successfully, starting to spin...")
        
        try:
            rclpy.spin(node)
        except KeyboardInterrupt:
            if node:
                node.get_logger().info("Shutting down MultiTopicPublisher (KeyboardInterrupt).")
        except Exception as e:
            if node:
                node.get_logger().error(f"Error during spin: {e}")
                import traceback
                node.get_logger().error(f"Traceback: {traceback.format_exc()}")
            print(f"Error during spin: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            raise
    except Exception as e:
        print(f"Fatal error in main: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)
    finally:
        # Cleanup in reverse order
        print("Cleaning up...")
        if node is not None:
            try:
                print("Destroying node...")
                node.destroy_node()
                print("Node destroyed")
            except Exception as e:
                print(f"Error destroying node: {e}")
        
        if ros_initialized:
            try:
                print("Shutting down ROS2...")
                rclpy.shutdown()
                print("ROS2 shutdown complete")
            except Exception as e:
                print(f"Error shutting down ROS2: {e}")


if __name__ == "__main__":
    main()
