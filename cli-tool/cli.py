import requests

BASE = "http://localhost:5000"

def add_node():
    cpu = int(input("Enter CPU cores for new node: "))
    res = requests.post(f"{BASE}/add_node", json={'cpu_cores': cpu})
    node_id = res.json().get('node_id')
    print("Node added:", node_id)
    return node_id

def launch_node_container(node_id):
    import os
    os.system(f"docker run -d node_sim python node.py {node_id}")

def list_nodes():
    res = requests.get(f"{BASE}/nodes")
    print("Nodes:", res.json())

def add_pod():
    cpu = int(input("CPU required for Pod: "))
    res = requests.post(f"{BASE}/add_pod", json={'cpu_required': cpu})
    print(res.json())

while True:
    print("\n1. Add Node\n2. Add Pod\n3. List Nodes\n4. Exit")
    choice = input("Choice: ")
    if choice == "1":
        node_id = add_node()
        launch_node_container(node_id)
    elif choice == "2":
        add_pod()
    elif choice == "3":
        list_nodes()
    elif choice == "4":
        break
