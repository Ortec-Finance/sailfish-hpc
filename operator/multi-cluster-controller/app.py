import os
import kopf

import os
from prometheus import PrometheusEvaluator
from tolerations import Tolerations
from bridge import Bridge
from score import Score
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Dynamically get the namespace the operator is running in
if os.path.isfile("/var/run/secrets/kubernetes.io/serviceaccount/namespace"):
    with open("/var/run/secrets/kubernetes.io/serviceaccount/namespace", "r") as file:
        OPERATOR_NAMESPACE = file.read().strip()
else:
    OPERATOR_NAMESPACE = (
        "rdlabs-experiment-cas-eu-west"  # Fallback value for local execution
    )

SAILFISH_BROKER_NAME = "sailfish-broker"
print("Operator is observing the following namespace: ", OPERATOR_NAMESPACE)
print("Operator is expecting the following broker name: ", SAILFISH_BROKER_NAME)

tolerationUtils = Tolerations()
bridgeConfig = Bridge(SAILFISH_BROKER_NAME)
variableScore = Score()


@kopf.on.create("ortec-finance.com", "v1alpha1", "sailfishclusters")
@kopf.on.update("ortec-finance.com", "v1alpha1", "sailfishclusters")
def modify_activemq_artemis(spec, name, namespace, uid, logger, **kwargs):
    logger.debug(f"Namespace: {namespace}")
    owner_reference = {
        "apiVersion": "ortec-finance.com/v1alpha1",
        "kind": "SailfishCluster",
        "name": name,
        "uid": uid,
        "controller": True,
        "blockOwnerDeletion": True,
    }

    if namespace != OPERATOR_NAMESPACE:
        logger.info(
            f"Skipping event in namespace {namespace}. Operator is monitoring namespace {OPERATOR_NAMESPACE}."
        )
        return

    activemq_artemis = bridgeConfig.fetch_activemq_artemis(
        SAILFISH_BROKER_NAME, namespace, logger
    )

    if activemq_artemis:
        # Create the patch based on the Sailfish spec.
        patch = activemq_artemis
        ## CREATING BRIDGES
        bridges = []
        remote_clusters = []
        for cluster in spec.get("clusters", []):
            if "host" in cluster:
                logger.info(
                    f"Creating Broker Configuration for cluster {cluster['name']}"
                )
                remote_clusters.append(cluster)

        for cluster in remote_clusters:
            # Code to handle clusters with the "host" field
            bridge = [
                f"bridgeConfigurations.{cluster['name']}-bridge.queueName=sailfish{cluster['name']}",
                f"bridgeConfigurations.{cluster['name']}-bridge.forwardingAddress=sailfishJob",
                f"bridgeConfigurations.{cluster['name']}-bridge.retryInterval=500000",
                f"bridgeConfigurations.{cluster['name']}-bridge.reconnectAttempts=-1",
                f"bridgeConfigurations.{cluster['name']}-bridge.staticConnectors={cluster['name']}-connector",
            ]
            bridges.extend(bridge)

        patch["spec"]["brokerProperties"] = bridges

        ## CREATING CONNECTORS
        connectors = []
        for cluster in remote_clusters:
            connector = {
                "name": f"{cluster['name']}-connector",
                "host": cluster["host"],
                "port": 5673,
            }
            connectors.append(connector)

        patch["spec"]["connectors"] = connectors

        ## CREATE cluster QUEUES
        for cluster in remote_clusters:
            logger.info(
                f"Creating Queue: sailfish{cluster['name']} that links to cluster {cluster['name']}"
            )
            bridgeConfig.create_or_update_activemq_artemis_address(
                name, namespace, cluster["name"], owner_reference, logger
            )

        logger.info(f"Applying BrokerConfiguration to {SAILFISH_BROKER_NAME}")
        bridgeConfig.update_activemq_artemis(
            SAILFISH_BROKER_NAME, namespace, patch, logger
        )

    else:
        logger.warning(f"ActiveMQArtemis {name} not found in namespace {namespace}")


@kopf.on.update("ortec-finance.com", "v1alpha1", "sailfishclusters")
@kopf.on.timer("ortec-finance.com", "v1alpha1", "sailfishclusters", interval=60)
def poll_sailfish_clusters_status(spec, patch, logger, **kwargs):
    logger.info("Polling Sailfish Clusters Status")
    cluster_statuses = []

    ## Append Remote Sailfish Clusters
    for cluster in spec.get("clusters", []):
        queue_name = cluster.get("queue", f"sailfish{cluster['name']}")
        trigger = None
        if "triggers" in spec:
            trigger = next(
                (
                    item
                    for item in spec.get("triggers")
                    if item["clusterRef"] == cluster["name"]
                ),
                None,
            )
        if trigger and "query" in trigger:
            cluster_statuses.append(
                {
                    "name": cluster["name"],
                    "queue": queue_name,
                    "status": "active",
                }
            )
        else:
            cluster_statuses.append(
                {
                    "name": cluster["name"],
                    "queue": queue_name,
                    "status": "inactive",
                    "reason": "No trigger query defined for this Cluster",
                }
            )

    patch.status["clusters"] = {}
    patch.status["clusters"] = cluster_statuses


def get_active_sailfish_clusters(sailfish_cluster):
    clusters = sailfish_cluster["status"]["clusters"]

    activeClusters = []
    for cluster in clusters:
        if cluster["status"] == "active":
            activeClusters.append(cluster)
        else:
            print(f"Cluster {cluster['name']} is not active.")

    return activeClusters


@kopf.on.update("ortec-finance.com", "v1alpha1", "sailfishclusters")
@kopf.on.timer("ortec-finance.com", "v1alpha1", "sailfishclusters", interval=60)
def poll_sailfish_cluster_best_destination(spec, patch, status, logger, **kwargs):
    evaluator = PrometheusEvaluator()
    cluster_statuses = []

    for cluster in status.get("clusters", []):
        if cluster["status"] == "inactive":
            logger.info(f"Skipping Inactive cluster {cluster['name']}")
            continue
        trigger_statuses = []
        if "triggers" in spec:
            for trigger in spec.get("triggers"):
                if trigger["clusterRef"] == cluster["name"]:
                    value = evaluator.evaluate_query(trigger["query"])
                    if value is None:
                        logger.error(
                            f"Was not able to get a value from the query: {trigger['query']}"
                        )
                        raise kopf.PermanentError("Value is None. Cannot proceed.")
                    scaled_value = variableScore.apply_scaler(value, trigger["scaler"])

                    trigger_statuses.append(
                        {
                            "name": trigger["name"],
                            "value": scaled_value,
                        }
                    )

        score = variableScore.sum_trigger_values(trigger_statuses)

        if spec.get("tolerations") is None:
            toleration = "Accepting"
        else:
            if tolerationUtils.evaluate_tolerations(
                cluster["name"], spec.get("tolerations"), logger
            ):
                toleration = "Accepting"
            else:
                toleration = "Blocking"

        cluster_statuses.append(
            {
                "name": cluster["name"],
                "score": score,
                "toleration": toleration,
                "triggers": trigger_statuses,
            }
        )

    if cluster_statuses:
        reward = variableScore.cost_function(logger, cluster_statuses)
        scheduler = {
            "clusters": cluster_statuses,
            "activatedTargetCluster": reward["name"],
            "status": "Healthy",
        }

    else:  # Fallback to Local cluster if no triggers are set.
        for cluster in spec.get("clusters", []):
            if "queue" in cluster:
                scheduler = {
                    "activatedTargetCluster": cluster["name"],
                    "status": "Unhealthy configuration: No triggers set. Fallback to Local Cluster",
                }

    if "scheduler" in status and status["scheduler"] == scheduler:
        logger.info("No change in scheduler status")
    else:
        patch.status["scheduler"] = {}
        patch.status["scheduler"] = scheduler


if __name__ == "__main__":
    kopf.run()
