import time
from kubernetes import client, watch
from model import LeaderElectionModel
from update_leader import update_leader

# Initialize Kubernetes API
v1 = client.CoreV1Api()

def monitor_leader_deletion():
    """Monitor pod events for leader deletion and trigger re-election."""
    print("Monitoring pods for leader deletion...")
    w = watch.Watch()
    try:
        for event in w.stream(v1.list_namespaced_pod, namespace="default"):
            pod = event['object']
            if event['type'] == 'DELETED' and pod.metadata.labels.get("role") == "leader":
                print(f"Leader pod {pod.metadata.name} deleted. Re-electing leader...")
                update_leader()
    except Exception as e:
        print(f"Error monitoring leader deletion: {e}")

if __name__ == "__main__":
    # Run the leader election and monitor continuously
    while True:
        update_leader()
        monitor_leader_deletion()
        time.sleep(5)  # Check periodically
