import os
import re

from prometheus_api_client import PrometheusConnect


class PrometheusClient:
    def __init__(self):
        url = os.getenv("PROMETHEUS_URL", "https://localhost:10912")
        if os.path.isfile("/var/run/secrets/kubernetes.io/serviceaccount/token"):
            with open(
                "/var/run/secrets/kubernetes.io/serviceaccount/token", "r"
            ) as file:
                TOKEN = file.read().strip()
                self.prom = PrometheusConnect(
                    url=url,
                    headers={"Authorization": f"Bearer {TOKEN}"},
                    disable_ssl=True,
                )
            with open(
                "/var/run/secrets/kubernetes.io/serviceaccount/namespace", "r"
            ) as file:
                self.namespace = file.read().strip()
        else:
            TOKEN = os.getenv("PROMETHEUS_TOKEN")

            self.prom = PrometheusConnect(
                url=url, headers={"Authorization": f"Bearer {TOKEN}"}, disable_ssl=True
            )
            self.namespace = (
                "rdlabs-experiment-cas-eu-west"  # Fallback value for local execution
            )

    def query_value(self, query):
        """Executes a single point query."""
        try:
            metric_data = self.prom.custom_query(
                query=query, params={"namespace": self.namespace}
            )
            return float(metric_data[0]["value"][1])
        except Exception as e:
            print(f"Failed to execute query {query}: {str(e)}")
            return None


class PrometheusEvaluator:
    def __init__(self):
        self.prom = PrometheusClient()

    def evaluate_query(self, query):
        return self.prom.query_value(query)

    def evaluate_expression(self, expression):
        """Evaluates a PromQL expression with a comparison, e.g., 'metric{label="value"} > 10'."""
        # Extract the parts of the expression
        query, operator, threshold = self.parse_expression(expression)
        result_value = self.prom.query_value(query)
        if result_value is None:
            return False

        # Compare the result based on the operator
        return self.compare(result_value, operator, float(threshold))

    def parse_expression(self, expression):
        """Parse the expression into a query, operator, and threshold."""
        # This regex allows spaces around the operator and handles complex queries
        match = re.search(
            r"^(.+?)\s*(>=|<=|>|<|==|!=)\s*(\d+\.?\d*)$", expression.strip()
        )
        if not match:
            raise ValueError("Invalid expression format.")
        return match.groups()

    def compare(self, value, operator, threshold):
        """Perform a comparison based on the operator."""
        operations = {
            ">": lambda x, y: x > y,
            "<": lambda x, y: x < y,
            ">=": lambda x, y: x >= y,
            "<=": lambda x, y: x <= y,
            "==": lambda x, y: x == y,
            "!=": lambda x, y: x != y,
        }
        return operations[operator](value, threshold)
