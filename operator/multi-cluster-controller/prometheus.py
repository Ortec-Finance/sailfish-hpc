import os
from prometheus_api_client import PrometheusConnect

class PrometheusClient:
    def __init__(self):
        url = os.getenv('PROMETHEUS_URL', "https://localhost:10912")
        if os.path.isfile("/var/run/secrets/kubernetes.io/serviceaccount/token"):
            with open("/var/run/secrets/kubernetes.io/serviceaccount/token", "r") as file:
                TOKEN = file.read().strip()
                self.prom = PrometheusConnect(url=url, headers={"Authorization": f"Bearer {TOKEN}"}, disable_ssl=True)
            with open("/var/run/secrets/kubernetes.io/serviceaccount/namespace", "r") as file:
                self.namespace = file.read().strip()
        else:
            TOKEN = "eyJhbGciOiJSUzI1NiIsImtpZCI6ImgxNWNwY2MyTWtISDZWSkdRRkdYT2hpV2tZb3JqZU52TlZfN2p1N3NOdHMifQ.eyJhdWQiOlsiaHR0cHM6Ly9rdWJlcm5ldGVzLmRlZmF1bHQuc3ZjIl0sImV4cCI6MTc1MTQ1MzQ5NCwiaWF0IjoxNzE5OTE3NDk0LCJpc3MiOiJodHRwczovL2t1YmVybmV0ZXMuZGVmYXVsdC5zdmMiLCJrdWJlcm5ldGVzLmlvIjp7Im5hbWVzcGFjZSI6InJkbGFicy1leHBlcmltZW50LWNhcy1ldS13ZXN0IiwicG9kIjp7Im5hbWUiOiJzYWlsZmlzaC1tdWx0aS1jbHVzdGVyLWNvbnRyb2xsZXItNmY2NTVmNTY4OC02eHhycSIsInVpZCI6IjI4NzRkMWYxLWNmNTktNGU2Mi04OWRmLTFlZTk4ZWQ1Y2Q4OSJ9LCJzZXJ2aWNlYWNjb3VudCI6eyJuYW1lIjoic2FpbGZpc2gtb3BlcmF0b3IiLCJ1aWQiOiJiNmQzZDdhZC1lMDFlLTRlMjMtYThiOS1iOWIzMzVmM2EyZTUifSwid2FybmFmdGVyIjoxNzE5OTIxMTAxfSwibmJmIjoxNzE5OTE3NDk0LCJzdWIiOiJzeXN0ZW06c2VydmljZWFjY291bnQ6cmRsYWJzLWV4cGVyaW1lbnQtY2FzLWV1LXdlc3Q6c2FpbGZpc2gtb3BlcmF0b3IifQ.XR995Py7vaFOrVp4nXyAJvNMi8kv_a5AhSRKNSQIIuPQ87Hu3NOOuDxFttcQVJTbNsjNgqlqosqV9rr901fh1iiEGWpHiyVPV5NGc3lYFkTny6QP5afB-atV0n_ZkVD5c4nkXNQe8aq49qBeJElIQsulOTWSEt5eliNLNnzi9ZfdXHhJTpUCE5CSrBDG9xSydTWTOVql0P936880KfqUxbLWNNSoWxFqhMdI9L-9vjYi7KUvBYpm4jrmhbfZX9kBJ-v1utah61_uDu6KvxTQoby3Nsl2HLCGflXN0QRKzsc2a5tvDp7Lu5djE4VQmyhOE95GM8TW-OBnlP7K8VslMS6zijEnWYS6MRC-a1OqxIvdtnhkK98A3xaEN8hQABbKeseyrGbSvj7tAanWt7CprkYpfddWstbF3vwmFAtkrFtzQITyf7Eq-iALRczwY9M5wz1osKiQytgYi3pmI9f6MjNW_KxXD7DJHQUOa7s7Ahrp4F5WZ5FxDHGBT17VeTd5OFRBHZ5EYqZ2lWsFEB3UdBzX2HYctSd43u5UZEw0xVFrfmwACWlRJeZuyb0oOLgPRpevic8VuI6TuyXUoNX-F78eY5LRDiox0PrecP-SaxkyY3nA5_K3nKN2Pm8UeuzGX2flJj-ougX6VL9LuAXO1JBHuOgvvuK-sRlYdB16arE"    
            
            self.prom = PrometheusConnect(url=url, headers={"Authorization": f"Bearer {TOKEN}"}, disable_ssl=True)
            self.namespace = "rdlabs-experiment-cas-eu-west" # Fallback value for local execution
    
    def query_value(self, query):
        """Executes a single point query."""
        try:
            metric_data = self.prom.custom_query(query=query, params={'namespace': self.namespace})
            return float(metric_data[0]['value'][1])
        except Exception as e:
            print(f"Failed to execute query {query}: {str(e)}")
            return None
        
        
class PrometheusEvaluator:
    def __init__(self):
        self.prom = PrometheusClient()
    
    def evaluateQuery(self,query):
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
        import re
        """Parse the expression into a query, operator, and threshold."""
        # This regex allows spaces around the operator and handles complex queries
        match = re.search(r"^(.+?)\s*(>=|<=|>|<|==|!=)\s*(\d+\.?\d*)$", expression.strip())
        if not match:
            raise ValueError("Invalid expression format.")
        return match.groups()
    
    def compare(self, value, operator, threshold):
        """Perform a comparison based on the operator."""
        operations = {
            '>': lambda x, y: x > y,
            '<': lambda x, y: x < y,
            '>=': lambda x, y: x >= y,
            '<=': lambda x, y: x <= y,
            '==': lambda x, y: x == y,
            '!=': lambda x, y: x != y,
        }
        return operations[operator](value, threshold)
