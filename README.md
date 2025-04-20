# Distributed Systems Cluster Simulation Framework

This project implements a lightweight simulation of a Kubernetes-like cluster management system. It demonstrates key distributed computing concepts such as node management, pod scheduling, and fault tolerance.

## Features

- **Node Management**: Add nodes to the cluster with specific CPU resources
- **Pod Scheduling**: Launch pods with specific CPU requirements using different scheduling algorithms (first-fit, best-fit, worst-fit)
- **Health Monitoring**: Track node health and detect failures
- **Fault Tolerance**: Automatically reschedule pods from failed nodes
- **User Interface**: Both CLI and web interface options for interacting with the cluster

## Prerequisites

- Docker and Docker Compose
- Python 3.6+
- Required Python packages (see requirements.txt)

## Using the CLI

The command-line interface provides several commands for interacting with the cluster:

Available algorithms: first-fit (default), best-fit, worst-fit

Then open your browser and navigate to http://localhost:5000

The web interface allows you to:
- See an overview of cluster status
- Add nodes to the cluster
- Create pods with different scheduling algorithms
- View all nodes and pods in real-time
- Simulate node failures

## Components Explanation

### API Server

The central control unit consists of three key components:

1. **Node Manager**: Tracks registered nodes and their statuses, including resource availability
2. **Pod Scheduler**: Assigns pods to nodes based on scheduling policies and resource requirements
3. **Health Monitor**: Receives heartbeat signals from nodes and detects failures

### Node Simulator

Each node is simulated as a Docker container running a Python script that:
- Registers with the API server
- Sends periodic heartbeat signals
- Maintains an array of pod IDs it hosts

### Pod Scheduler

The pod scheduler implements three algorithms:
- **First-fit**: Assigns the pod to the first node with enough resources
- **Best-fit**: Assigns the pod to the node that has the closest match to the required resources
- **Worst-fit**: Assigns the pod to the node with the most available resources

## Further Enhancements

- Implement auto-scaling for nodes based on cluster load
- Add pod resource usage monitoring
- Implement network policy simulation for pod communication control

## License

[MIT License](LICENSE)
