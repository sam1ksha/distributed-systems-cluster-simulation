# Distributed Systems Cluster Simulation Framework

This project implements a lightweight simulation of a Kubernetes-like cluster management system. It demonstrates key distributed computing concepts such as node management, pod scheduling, and fault tolerance.

## Architecture

The system consists of three main components:

1. **API Server (Central Control Unit)**: Manages the overall cluster operations including node registration, pod scheduling, and health monitoring.
2. **Nodes**: Simulated as Docker containers, each node hosts pods and periodically sends heartbeat signals to the API server.
3. **Pods**: The smallest deployable units that are scheduled on nodes and require specific CPU resources.

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

## Setup

1. Clone the repository:
   ```
   git clone <repository-url>
   cd distributed-systems-cluster-simulator
   ```

2. Run the setup script:
   ```
   chmod +x setup_and_run.sh
   ./setup_and_run.sh
   ```

3. The API server and Redis database will start in Docker containers.

## Using the CLI

The command-line interface provides several commands for interacting with the cluster:

### Add a node to the cluster

```
python cli_client.py add-node <cpu_cores>
```

Example:
```
python cli_client.py add-node 4
```

### List all nodes in the cluster

```
python cli_client.py list-nodes
```

### Create a pod

```
python cli_client.py create-pod <name> <cpu_required> [--algorithm <algorithm>]
```

Example:
```
python cli_client.py create-pod web-server 2 --algorithm best-fit
```

Available algorithms: first-fit (default), best-fit, worst-fit

### List all pods in the cluster

```
python cli_client.py list-pods
```

### Simulate a node failure

```
python cli_client.py fail-node <node_id>
```

## Using the Web Interface

Start the web interface:

```
python web_interface.py
```

Then open your browser and navigate to http://localhost:8080

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
