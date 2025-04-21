# api_server/api_server.py
from flask import Flask, request, jsonify, render_template
from threading import Thread
import uuid
import time
import subprocess
import os

app = Flask(__name__)

nodes = {}  # {node_id: {cpu_cores, available_cores, pods, last_heartbeat, container_id}}
pods = {}   # {pod_id: {cpu_required, node_id, container_id}}

# Heartbeat timeout (seconds)
HEARTBEAT_TIMEOUT = 10

# Web Interface Route
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_node', methods=['POST'])
def add_node():
    data = request.get_json()
    cpu_cores = data.get('cpu_cores', 2)
    node_id = str(uuid.uuid4())
    
    # Launch Docker container for this node
    try:
        result = subprocess.run(
            ["docker", "run", "-d", "--name", f"node_{node_id[:8]}", "node_sim", "python", "node.py", node_id],
            capture_output=True, text=True, check=True
        )
        container_id = result.stdout.strip()
        print(f"Started node container: {container_id}")
        
        nodes[node_id] = {
            'cpu_cores': cpu_cores,
            'available_cores': cpu_cores,
            'pods': [],
            'last_heartbeat': time.time(),
            'status': 'Healthy',
            'container_id': container_id
        }
        return jsonify({'message': 'Node added', 'node_id': node_id, 'container_id': container_id}), 201
    except subprocess.CalledProcessError as e:
        print(f"Error starting node container: {e}")
        return jsonify({'message': 'Error creating node container', 'error': str(e)}), 500

@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    data = request.get_json()
    node_id = data['node_id']
    if node_id in nodes:
        nodes[node_id]['last_heartbeat'] = time.time()
        nodes[node_id]['status'] = 'Healthy'
    return jsonify({'message': 'Heartbeat received'}), 200

@app.route('/add_pod', methods=['POST'])
def add_pod():
    data = request.get_json()
    cpu_required = data['cpu_required']
    pod_id = str(uuid.uuid4())
    container_id = None

    # First-fit scheduling
    for node_id, node in nodes.items():
        if node['available_cores'] >= cpu_required and node['status'] == 'Healthy':
            # Create a pod container - this is optional as pods could be simulated
            try:
                # Example pod - in reality this would be your application container
                # We're just creating a simple container that does nothing but stay alive
                result = subprocess.run(
                    ["docker", "run", "-d", "--name", f"pod_{pod_id[:8]}", 
                     "--label", f"node_id={node_id}", 
                     "alpine", "sleep", "infinity"],
                    capture_output=True, text=True, check=True
                )
                container_id = result.stdout.strip()
                print(f"Started pod container: {container_id}")
                
                # Update resources and assignments
                node['available_cores'] -= cpu_required
                node['pods'].append(pod_id)
                pods[pod_id] = {
                    'cpu_required': cpu_required, 
                    'node_id': node_id,
                    'container_id': container_id
                }
                return jsonify({
                    'message': 'Pod scheduled', 
                    'pod_id': pod_id, 
                    'node_id': node_id,
                    'container_id': container_id
                }), 201
            except subprocess.CalledProcessError as e:
                print(f"Error starting pod container: {e}")
                return jsonify({'message': 'Error creating pod container', 'error': str(e)}), 500

    return jsonify({'message': 'No suitable node available'}), 503

@app.route('/nodes', methods=['GET'])
def list_nodes():
    return jsonify(nodes), 200

# New routes for web interface
@app.route('/pods', methods=['GET'])
def list_pods():
    return jsonify(pods), 200

@app.route('/remove_pod/<pod_id>', methods=['DELETE'])
def remove_pod(pod_id):
    if pod_id in pods:
        node_id = pods[pod_id]['node_id']
        cpu_required = pods[pod_id]['cpu_required']
        container_id = pods[pod_id].get('container_id')
        
        # Return resources to node
        if node_id in nodes:
            nodes[node_id]['available_cores'] += cpu_required
            if pod_id in nodes[node_id]['pods']:
                nodes[node_id]['pods'].remove(pod_id)
        
        # Remove the Docker container
        if container_id:
            try:
                subprocess.run(["docker", "rm", "-f", container_id], check=True)
                print(f"Removed pod container: {container_id}")
            except subprocess.CalledProcessError as e:
                print(f"Error removing pod container: {e}")
        
        # Remove pod
        del pods[pod_id]
        return jsonify({'message': 'Pod removed'}), 200
    
    return jsonify({'message': 'Pod not found'}), 404

@app.route('/remove_node/<node_id>', methods=['DELETE'])
def remove_node(node_id):
    if node_id in nodes:
        # Check if node has pods
        if nodes[node_id]['pods']:
            return jsonify({'message': 'Cannot remove node with active pods'}), 400
        
        # Remove the Docker container
        container_id = nodes[node_id].get('container_id')
        if container_id:
            try:
                subprocess.run(["docker", "rm", "-f", container_id], check=True)
                print(f"Removed node container: {container_id}")
            except subprocess.CalledProcessError as e:
                print(f"Error removing node container: {e}")
        
        # Remove node
        del nodes[node_id]
        return jsonify({'message': 'Node removed'}), 200
    
    return jsonify({'message': 'Node not found'}), 404


def monitor_health():
    while True:
        now = time.time()
        for node_id in list(nodes.keys()):
            last = nodes[node_id]['last_heartbeat']
            if now - last > HEARTBEAT_TIMEOUT:
                # Always keep as healthy
                nodes[node_id]['status'] = 'Healthy'
        time.sleep(5)

def reschedule_pods(failed_node_id):
    print(f"Rescheduling pods from node {failed_node_id}")
    for pod_id in nodes[failed_node_id]['pods']:
        pod = pods[pod_id]
        
        # Remove the old pod container if it exists
        container_id = pod.get('container_id')
        if container_id:
            try:
                subprocess.run(["docker", "rm", "-f", container_id], check=True)
                print(f"Removed pod container for rescheduling: {container_id}")
            except subprocess.CalledProcessError as e:
                print(f"Error removing pod container: {e}")
        
        # Try to find a new node
        for node_id, node in nodes.items():
            if node_id != failed_node_id and node['available_cores'] >= pod['cpu_required'] and node['status'] == 'Healthy':
                # Create a new pod container on the new node
                try:
                    result = subprocess.run(
                        ["docker", "run", "-d", "--name", f"pod_{pod_id[:8]}_rescheduled", 
                         "--label", f"node_id={node_id}", 
                         "alpine", "sleep", "infinity"],
                        capture_output=True, text=True, check=True
                    )
                    new_container_id = result.stdout.strip()
                    print(f"Rescheduled pod container: {new_container_id}")
                    
                    # Update resources and assignments
                    node['available_cores'] -= pod['cpu_required']
                    node['pods'].append(pod_id)
                    pods[pod_id]['node_id'] = node_id
                    pods[pod_id]['container_id'] = new_container_id
                    print(f"Rescheduled pod {pod_id} to node {node_id}")
                    break
                except subprocess.CalledProcessError as e:
                    print(f"Error rescheduling pod container: {e}")

# Clean up any existing containers on startup
def cleanup_containers():
    try:
        subprocess.run(["docker", "ps", "-q", "--filter", "ancestor=node_sim", "--format", "{{.ID}}"], 
                      capture_output=True, check=True)
        subprocess.run(["docker", "rm", "-f", "$(docker ps -q --filter ancestor=node_sim)"], 
                      shell=True, check=False)
        print("Cleaned up existing node containers")
        
        subprocess.run(["docker", "ps", "-q", "--filter", "name=pod_", "--format", "{{.ID}}"], 
                      capture_output=True, check=True)
        subprocess.run(["docker", "rm", "-f", "$(docker ps -q --filter name=pod_)"], 
                      shell=True, check=False)
        print("Cleaned up existing pod containers")
    except subprocess.CalledProcessError as e:
        print(f"Error during container cleanup: {e}")

# Start background threads
Thread(target=monitor_health, daemon=True).start()

if __name__ == '__main__':
    # Clean up any existing containers before starting
    cleanup_containers()
    
    # Start the Flask app
    app.run(debug=True, port=5000, host="0.0.0.0")
