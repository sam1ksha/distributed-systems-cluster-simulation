import requests
import time
import sys

node_id = sys.argv[1]

while True:
    try:
        r = requests.post("http://host.docker.internal:5000/heartbeat", json={"node_id": node_id})
        print(f"[{node_id}] Sent heartbeat. Status:", r.status_code)
    except Exception as e:
        print(f"[{node_id}] Error:", e)
    time.sleep(5)
