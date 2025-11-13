# Use ROS 2 Humble base (Ubuntu 22.04)
FROM ros:humble-ros-core

# Set a working directory
WORKDIR /app

# Install Python dependencies for ROS 2 rclpy/std_msgs
RUN apt-get update && apt-get install -y \
    ros-humble-rclpy \
    ros-humble-std-msgs \
    python3-pip \
 && rm -rf /var/lib/apt/lists/*

# (Optional) If you have extra Python deps
# COPY requirements.txt .
# RUN pip3 install --no-cache-dir -r requirements.txt

# Copy your ROS2 publisher script
COPY multi_topic_publisher.py /app/multi_topic_publisher.py

# Environment (optional defaults)
ENV FREQUENCY_HZ=1.0
ENV TOPICS=/chatter
ENV PAYLOAD="hello from ROS2 in k8s"

# Entry command: source ROS 2 setup and run the script
CMD ["/bin/bash", "-c", "source /opt/ros/humble/setup.bash && python3 /app/multi_topic_publisher.py"]
