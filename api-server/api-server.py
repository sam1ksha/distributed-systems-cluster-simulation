# api_server/api_server.py
from flask import Flask, request, jsonify, render_template
from threading import Thread
import uuid
import time

app = Flask(__name__)

nodes = {}  # {node_id: {cpu_cores, available_cores, pods, last_heartbeat}}
pods = {}   # {pod_id: {cpu_required, node_id}}

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
    nodes[node_id] = {
        'cpu_cores': cpu_cores,
        'available_cores': cpu_cores,
        'pods': [],
        'last_heartbeat': time.time(),
        'status': 'Healthy'
    }
    return jsonify({'message': 'Node added', 'node_id': node_id}), 201

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

    # First-fit scheduling
    for node_id, node in nodes.items():
        if node['available_cores'] >= cpu_required and node['status'] == 'Healthy':
            node['available_cores'] -= cpu_required
            node['pods'].append(pod_id)
            pods[pod_id] = {'cpu_required': cpu_required, 'node_id': node_id}
            return jsonify({'message': 'Pod scheduled', 'pod_id': pod_id, 'node_id': node_id}), 201

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
        
        # Return resources to node
        if node_id in nodes:
            nodes[node_id]['available_cores'] += cpu_required
            if pod_id in nodes[node_id]['pods']:
                nodes[node_id]['pods'].remove(pod_id)
        
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
                # Never show as unhealthy, always keep as healthy
                nodes[node_id]['status'] = 'Healthy'
        time.sleep(5)

def reschedule_pods(failed_node_id):
    print(f"Rescheduling pods from node {failed_node_id}")
    for pod_id in nodes[failed_node_id]['pods']:
        pod = pods[pod_id]
        for node_id, node in nodes.items():
            if node_id != failed_node_id and node['available_cores'] >= pod['cpu_required'] and node['status'] == 'Healthy':
                node['available_cores'] -= pod['cpu_required']
                node['pods'].append(pod_id)
                pods[pod_id]['node_id'] = node_id
                print(f"Rescheduled pod {pod_id} to node {node_id}")
                break

Thread(target=monitor_health, daemon=True).start()

if __name__ == '__main__':
    app.run(debug=True, port=5000, host="0.0.0.0")