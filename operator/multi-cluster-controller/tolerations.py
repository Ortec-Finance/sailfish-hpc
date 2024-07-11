from prometheus import PrometheusEvaluator


class Tolerations:
    def __init__(self):
        self.evaluator = PrometheusEvaluator()

    def evaluate_tolerations(self, cluster_name, tolerations, logger):
        logger.info(f"Evaluating tolerations for cluster {cluster_name}")

        for toleration in tolerations:
            if toleration["clusterRef"] == cluster_name:
                if not self.evaluator.evaluate_expression(toleration["expr"]):
                    logger.info(
                        f"The {toleration['name']} for cluster {cluster_name} is not met"
                    )
                    return False
        logger.info(
            f"Toleration with the Expression: {toleration['expr']} for cluster {cluster_name} is met"
        )
        return True
