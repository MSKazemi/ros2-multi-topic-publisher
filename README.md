# ros2-multi-topic-publisher

A minimal **ROS 2 (Humble) Python node that publishes `std_msgs/String` messages to multiple topics** at a configurable frequency. Everything is driven by environment variables, and the node ships as a Docker image (GitHub Container Registry) with ready-to-use Kubernetes manifests for a publisher/subscriber demo.

- **ros2-multi-topic-publisher** is an open-source ROS 2 example node for publishing to many topics from a single process.
- It helps you generate steady `std_msgs/String` traffic on one or more ROS 2 topics without writing any code.
- Use it when you need a lightweight publisher to test ROS 2 subscribers, DDS discovery, or ROS 2 running inside Docker and Kubernetes.
- It is configured entirely through environment variables (`TOPICS`, `PAYLOAD`, `FREQUENCY_HZ`, `ROS_DOMAIN_ID`).
- It is not a full ROS 2 (ament/colcon) package and is not intended for production robotics workloads.

## Table of contents

- [What is this?](#what-is-this)
- [Who is it for?](#who-is-it-for)
- [How it works](#how-it-works)
- [Configuration](#configuration)
- [Quickstart](#quickstart)
- [Run with Docker](#run-with-docker)
- [Deploy on Kubernetes](#deploy-on-kubernetes)
- [Examples](#examples)
- [Features](#features)
- [Use cases](#use-cases)
- [Limitations / when NOT to use](#limitations--when-not-to-use)
- [FAQ](#faq)
- [License](#license)

## What is this?

`ros2-multi-topic-publisher` is a single ROS 2 node, `multi_topic_publisher`, written in Python with `rclpy`. On a fixed-rate timer it publishes the **same** `std_msgs/String` payload to every topic in a comma-separated list. It targets **ROS 2 Humble** on Ubuntu 22.04 (the `ros:humble-ros-core` base image) and is designed to be run as a container in Docker or Kubernetes.

## Who is it for?

- Robotics and ROS 2 developers who need a quick, configurable message source for testing.
- Platform / DevOps engineers running **ROS 2 on Kubernetes** who want a simple publisher/subscriber smoke test.
- Anyone learning ROS 2 topics, publishers, DDS discovery, and `ROS_DOMAIN_ID`.

## How it works

- Creates one `std_msgs/String` publisher per topic (QoS depth `10`).
- A ROS 2 timer fires every `1 / FREQUENCY_HZ` seconds and publishes the configured payload to all topics.
- Logs an info line every 10 published messages so activity is visible without flooding the logs.
- Reads all settings from environment variables at startup, with safe defaults and validation (invalid frequency falls back to `1.0` Hz; an empty topic list falls back to `/chatter`).

Source: [`src/multi_topic_publisher.py`](src/multi_topic_publisher.py).

## Configuration

| Environment variable | Default | Description |
|---|---|---|
| `TOPICS` | `/chatter` | Comma-separated list of topic names to publish to (e.g. `/topic1,/topic2`). |
| `PAYLOAD` | `hello from ROS2 in k8s` | The string published to every topic. |
| `FREQUENCY_HZ` | `1.0` | Publish rate in Hz. Must be `> 0`; invalid values fall back to `1.0`. |
| `ROS_DOMAIN_ID` | `0` (ROS 2 default) | ROS 2 DDS domain ID; must match any subscribers for them to receive messages. |

## Quickstart

Run the node directly inside a ROS 2 Humble environment (no colcon build required — it is a standalone script):

```bash
source /opt/ros/humble/setup.bash
export TOPICS="/topic1,/topic2"
export PAYLOAD="hello from ROS2"
export FREQUENCY_HZ="2.0"
python3 src/multi_topic_publisher.py
```

Expected log output:

```
[INFO] [multi_topic_publisher]: Created publisher on topic: /topic1
[INFO] [multi_topic_publisher]: Created publisher on topic: /topic2
[INFO] [multi_topic_publisher]: MultiTopicPublisher node started.
  Topics   : ['/topic1', '/topic2']
  Payload  : 'hello from ROS2'
  Frequency: 2.0 Hz (period=0.5s)
[INFO] [multi_topic_publisher]: Published 10 messages to 2 topic(s)
```

Requires the `rclpy` and `std_msgs` packages (`ros-humble-rclpy`, `ros-humble-std-msgs`).

## Run with Docker

Build locally:

```bash
docker build -t ros2-multi-topic-publisher .
docker run --rm \
  -e TOPICS="/topic1,/topic2" \
  -e PAYLOAD="hello from ROS2" \
  -e FREQUENCY_HZ="2.0" \
  ros2-multi-topic-publisher
```

A prebuilt multi-tag image is published to **GitHub Container Registry (GHCR)** by CI on every push to `main`:

```bash
docker pull ghcr.io/mskazemi/ros2-multi-topic-publisher:latest
```

## Deploy on Kubernetes

The [`deploy/`](deploy) directory contains manifests for a full publisher/subscriber demo:

- [`deploy/ros2-publisher-deployment.yaml`](deploy/ros2-publisher-deployment.yaml) — the publisher `Deployment` (publishes to `/topic1,/topic2` at 2 Hz).
- [`deploy/ros2-subscriber-deployment.yaml`](deploy/ros2-subscriber-deployment.yaml) — a subscriber that runs `ros2 topic echo /topic1`.
- [`deploy/ros2-topic-checker-pod.yaml`](deploy/ros2-topic-checker-pod.yaml) — an interactive pod for inspecting topics with the ROS 2 CLI.

```bash
kubectl apply -f deploy/ros2-publisher-deployment.yaml
kubectl apply -f deploy/ros2-subscriber-deployment.yaml
kubectl logs -f deployment/ros2-topic-subscriber
```

All pods must share the same `ROS_DOMAIN_ID` for DDS discovery to work.

## Examples

**Single topic, 1 Hz (defaults):**

```bash
python3 src/multi_topic_publisher.py
# publishes "hello from ROS2 in k8s" to /chatter once per second
```

**Three topics at 5 Hz:**

```bash
TOPICS="/a,/b,/c" FREQUENCY_HZ="5.0" PAYLOAD="ping" python3 src/multi_topic_publisher.py
```

**Verify from another ROS 2 terminal:**

```bash
ros2 topic echo /topic1
ros2 topic hz /topic1
```

## Features

- Publishes to an arbitrary number of topics from one process.
- Configurable payload and publish frequency.
- 100% environment-variable driven — no code changes to reconfigure.
- Input validation with safe fallbacks for frequency and topic list.
- Docker image built and pushed to GHCR via GitHub Actions.
- Kubernetes manifests for publisher, subscriber, and a topic-checker pod.

## Use cases

- Smoke-testing ROS 2 subscribers and message pipelines.
- Validating DDS discovery and `ROS_DOMAIN_ID` configuration across pods/hosts.
- Demonstrating ROS 2 on Docker and Kubernetes.
- Teaching ROS 2 topics and the publisher pattern.

## Limitations / when NOT to use

- Publishes only `std_msgs/String` — no custom or sensor message types.
- Sends the same static payload to every topic; no per-topic content or dynamic data.
- Not an ament/colcon package (no `package.xml` / `setup.py`); it is run as a standalone script or container, not via `ros2 run`.
- Intended for testing, demos, and learning — not for production robotics.

## FAQ

**Which ROS 2 distribution does it target?**
ROS 2 Humble on Ubuntu 22.04 (`ros:humble-ros-core`).

**What message type does it publish?**
`std_msgs/String`.

**How do I change the topics or rate?**
Set the `TOPICS` and `FREQUENCY_HZ` environment variables — no rebuild needed.

**Why does my subscriber see nothing?**
Ensure the publisher and subscriber use the same `ROS_DOMAIN_ID` and are on the same DDS-reachable network.

**Do I need to run `colcon build`?**
No. It is a standalone Python script; run it directly with `python3` after sourcing ROS 2, or use the container image.

## License

Licensed under the [Apache License 2.0](LICENSE).
