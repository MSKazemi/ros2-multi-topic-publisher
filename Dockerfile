# Base ROS 2 image (Humble + Ubuntu 22.04)
FROM ros:humble-ros-core

# Working directory inside the container
WORKDIR /app

# Install ROS 2 Python client libs and std messages + python3-pip
RUN apt-get update && apt-get install -y \
    ros-humble-rclpy \
    ros-humble-std-msgs \
    python3-pip \
 && rm -rf /var/lib/apt/lists/*

# Copy application code
COPY src/multi_topic_publisher.py /app/multi_topic_publisher.py
COPY requirements.txt /app/requirements.txt

# Install extra Python deps if any (ignore if file empty)
RUN pip3 install --no-cache-dir -r /app/requirements.txt || true

# Default environment values (can be overridden in Kubernetes)
ENV FREQUENCY_HZ=1.0
ENV TOPICS=/chatter
ENV PAYLOAD="hello from ROS2 in k8s"

# Entry point: source ROS 2 and run the script
CMD ["/bin/bash", "-c", "source /opt/ros/humble/setup.bash && python3 /app/multi_topic_publisher.py"]
