import kopf


class Score:
    def apply_scaler(self, value, scaler):
        return float(value) * float(scaler)

    def sum_trigger_values(self, trigger_statuses):
        result = 0
        for trigger in trigger_statuses:
            result += trigger["value"]
        return result

    def cost_function(self, logger, cluster_results, operator=min):
        try:
            winner = operator(cluster_results, key=lambda x: x["score"])
        except Exception as e:
            logger.error("Operator not supported")
            raise kopf.PermanentError("Operator not supported")
        logger.info(
            f"The cost function declared the winner to be with reward {winner['name']} with a value of {winner['score']}"
        )
        return winner
