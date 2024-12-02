import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
import os

class LeaderElectionModel:
    def __init__(self):
        self.model = DecisionTreeClassifier()
        self.model_file = "leader_model.pkl"

        # Load the model if it exists
        if os.path.exists(self.model_file):
            self.model = joblib.load(self.model_file)
        else:
            print("Model file not found. Please train the model before making predictions.")

    def train(self, data, labels):
        """Train the Decision Tree model on the provided data."""
        X_train, X_test, y_train, y_test = train_test_split(data, labels, test_size=0.2, random_state=42)
        self.model.fit(X_train, y_train)

        # Check accuracy
        predictions = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, predictions)
        print(f"Model accuracy: {accuracy * 100:.2f}%")

        # Save the model after training
        joblib.dump(self.model, self.model_file)
        print("Model trained and saved successfully.")

    def predict(self, features):
        """Predict the leader node based on the provided features."""
        if self.model is None:
            raise ValueError("Model is not trained or loaded. Please train the model first.")
        return self.model.predict(features)

    def update_leader(self, node_metrics):
        """Update the leader based on node metrics."""
        features = pd.DataFrame(node_metrics)

        # Make predictions
        predictions = self.predict(features)

        results = []
        for idx, (pred, metrics) in enumerate(zip(predictions, node_metrics.values)):
            if pred == 1:  # If predicted as leader
                results.append(f"Node {idx}: Elected as leader.")
            else:
                reasons = self.get_rejection_reasons(metrics)
                reasons_str = ", ".join(reasons) if reasons else "no specific reasons."
                results.append(f"Node {idx}: Not elected as leader due to metrics: {metrics}. Reasons: {reasons_str}")

        return results

    def get_rejection_reasons(self, metrics):
        """Determine why a node was not elected as a leader based on metrics."""
        reasons = []
        cpu_threshold = 80
        memory_threshold = 80
        latency_threshold = 5
        uptime_threshold = 600  # 10 minutes

        cpu_usage, memory_usage, network_latency, uptime = metrics

        if cpu_usage >= cpu_threshold:
            reasons.append("high CPU usage")
        if memory_usage >= memory_threshold:
            reasons.append("high memory usage")
        if network_latency >= latency_threshold:
            reasons.append("high network latency")
        if uptime <= uptime_threshold:
            reasons.append("low uptime")

        return reasons
