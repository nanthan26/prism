from kubernetes import client, config
import pandas as pd
from model import LeaderElectionModel

# Load Kubernetes configuration
config.load_kube_config()
v1 = client.CoreV1Api()

# Initialize the AI model
model = LeaderElectionModel()

def update_leader():
    """Elect a leader pod and label it."""
    try:
        # Fetch all pods in the namespace
        pods = v1.list_namespaced_pod(namespace="default").items

        # Check if any pod is already labeled as the leader
        current_leader = None
        for pod in pods:
            if pod.metadata.labels and pod.metadata.labels.get("role") == "leader":
                current_leader = pod.metadata.name
                break

        if current_leader:
            print(f"Current leader: {current_leader}. No need to re-elect.")
            return

        # Load pod metrics from the CSV
        data = pd.read_csv('simulated_pod_metrics.csv').dropna()

        # Ensure required columns are present
        required_columns = ['cpu_usage', 'memory_usage', 'network_latency', 'uptime']
        if not all(col in data.columns for col in required_columns):
            print(f"Error: CSV missing required columns: {required_columns}")
            return

        # Use the model to elect a leader
        leaders = model.update_leader(data[required_columns])

        # Assign the leader label to the elected pod
        for leader in leaders:
            if 'Elected as leader' in leader:
                pod_index = int(leader.split()[1])  # Extract node index from the message
                pod_name = pods[pod_index].metadata.name
                print(f"Electing pod {pod_name} as the new leader.")

                # Update Kubernetes label
                body = {
                    "metadata": {
                        "labels": {"role": "leader"}
                    }
                }
                v1.patch_namespaced_pod(name=pod_name, namespace="default", body=body)
                break
    except Exception as e:
        print(f"Error in updating leader: {e}")

if __name__ == "__main__":
    update_leader()
