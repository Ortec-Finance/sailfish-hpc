import os
import kopf
import kubernetes.client
from kubernetes.client.rest import ApiException
import os
from prometheus import PrometheusEvaluator

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

def fetch_activemq_artemis(name, namespace, logger):
    api = kubernetes.client.CustomObjectsApi()
    try:
        return api.get_namespaced_custom_object(
            group="broker.amq.io",
            version="v1beta1",
            namespace=namespace,
            plural="activemqartemises",
            name=name,
        )
    except ApiException as e:
        logger.error(f"A ActiveMQArtemis broker is not deployed in this namespace: {e}")
        return None


def update_activemq_artemis(name, namespace, patch, logger):
    api = kubernetes.client.CustomObjectsApi()
    try:
        api.patch_namespaced_custom_object(
            group="broker.amq.io",
            version="v1beta1",
            namespace=namespace,
            plural="activemqartemises",
            name=name,
            body=patch,
        )
        logger.info(f"ActiveMQArtemis {name} updated in namespace {namespace}")
    except ApiException as e:
        logger.error(f"Failed to update ActiveMQArtemis: {e}")


def create_or_update_activemq_artemis_address(
    name, namespace, cluster_name, owner_reference, logger
):
    api = kubernetes.client.CustomObjectsApi()

    resource_name = f"sailfish-{cluster_name}-address"
    body = {
        "apiVersion": "broker.amq.io/v1beta1",
        "kind": "ActiveMQArtemisAddress",
        "metadata": {
            "name": resource_name,
            "namespace": namespace,
            "ownerReferences": [owner_reference],
        },
        "spec": {
            "addressName": f"sailfish{cluster_name}",
            "applyToCrNames": [SAILFISH_BROKER_NAME],
            "queueName": f"sailfish{cluster_name}",
            "routingType": "anycast",
            "queueConfiguration": {
                "routingType": "anycast",
                "durable": True,
                "maxConsumers": -1,
                "exclusive": False,
            },
        },
    }

    try:
        # Try to get the resource to determine if it exists
        existing = api.get_namespaced_custom_object(
            group="broker.amq.io",
            version="v1beta1",
            namespace=namespace,
            plural="activemqartemisaddresses",
            name=resource_name,
        )
        # If the resource exists, patch it
        if existing:
            api.patch_namespaced_custom_object(
                group="broker.amq.io",
                version="v1beta1",
                namespace=namespace,
                plural="activemqartemisaddresses",
                name=resource_name,
                body=body,
            )
            logger.info(
                f"ActiveMQArtemisAddress {resource_name} updated in namespace {namespace}"
            )
    except ApiException as e:
        if e.status == 404:
            # Resource does not exist, so create it
            api.create_namespaced_custom_object(
                group="broker.amq.io",
                version="v1beta1",
                namespace=namespace,
                plural="activemqartemisaddresses",
                body=body,
            )
            logger.info(
                f"ActiveMQArtemisAddress {resource_name} created in namespace {namespace}"
            )
        else:
            # Handle other exceptions
            logger.error(f"Failed to create or update ActiveMQArtemisAddress: {e}")

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

    activemq_artemis = fetch_activemq_artemis(SAILFISH_BROKER_NAME, namespace, logger)

    if activemq_artemis:
        # Create the patch based on the Sailfish spec.
        patch = activemq_artemis
        ## CREATING BRIDGES
        bridges = []
        remote_clusters = []
        for cluster in spec.get("clusters", []):
            if "host" in cluster:
                logger.info(f"Creating Broker Configuration for cluster {cluster['name']}")
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
            create_or_update_activemq_artemis_address(
                name, namespace, cluster["name"], owner_reference, logger
            )

        label = [
            f"ortec-finance.com/sailfish-cluster: {name}"
        ]
        
        logger.info(f"Applying BrokerConfiguration to {SAILFISH_BROKER_NAME}")
        update_activemq_artemis(SAILFISH_BROKER_NAME, namespace, patch, logger)

    else:
        logger.warning(f"ActiveMQArtemis {name} not found in namespace {namespace}")

@kopf.on.timer("ortec-finance.com","v1alpha1","sailfishclusters",interval=2)
def poll_sailfish_clusters_status(spec, patch, logger, **kwargs):
    logger.info("Polling Sailfish Clusters Status")
    cluster_statuses = []
    
    ## Append Remote Sailfish Clusters
    for cluster in spec.get("clusters", []):
        queue_name = cluster.get('queue', f"sailfish{cluster['name']}")
        query = next((item for item in spec.get('triggers') if item['clusterRef'] == cluster['name']), None)['query']
        if query:            
            cluster_statuses.append({
                    'name': cluster['name'],
                    'queue': queue_name,
                    'query': query,
                    'status': 'active'
                })
        else:
            cluster_statuses.append({
                    'name': cluster['name'],
                    'queue': queue_name,
                    'status': 'inactive',
                    'reason': 'No trigger query defined for this Cluster'
                })
            
    patch.status['clusters'] = {}
    patch.status['clusters'] = cluster_statuses
    

def get_active_sailfish_clusters(sailfish_cluster):
    clusters = sailfish_cluster['status']['clusters']
    
    activeClusters = []
    for cluster in clusters:
        if cluster['status'] == 'active':
            activeClusters.append(cluster)
        else:
            print(f"Cluster {cluster['name']} is not active.")
            
    return activeClusters
    

@kopf.on.timer("ortec-finance.com","v1alpha1","sailfishclusters",interval=2)
def poll_sailfish_cluster_best_destination(spec, patch, status, logger, **kwargs):
    evaluator = PrometheusEvaluator()
    cluster_statuses = []
    
    for cluster in spec.get("clusters", []):
        trigger_statuses = []
        for trigger in spec.get('triggers'):
            if trigger['clusterRef'] == cluster['name']:
                value = evaluator.evaluateQuery(trigger['query'])
                if value is None:
                    logger.error(f"Was not able to get a value from the query: {trigger['query']}")
                    raise kopf.PermanentError("Value is None. Cannot proceed.")
                scaled_value = apply_scaler(value, trigger['scaler'])
                
                trigger_statuses.append({
                    'name': trigger['name'],
                    'value': scaled_value,
                })
        
        result = sum_trigger_values(trigger_statuses) 
        cluster_statuses.append({
            'name': cluster['name'],
            'result': result,
            'toleration': 'Not Active',
            'triggers': trigger_statuses
        })
        
    reward = cost_function(logger,cluster_statuses)

    scheduler = {
        'clusters': cluster_statuses,
        'activatedTargetCluster': reward['name']
    }
    if 'scheduler' in status and status['scheduler'] == scheduler:
        logger.info("No change in scheduler status")
    else:
        patch.status['scheduler'] = {}
        patch.status['scheduler'] = scheduler
    
def apply_scaler(value, scaler):
    return float(value) * float(scaler) 

def sum_trigger_values(trigger_statuses):
    result = 0
    for trigger in trigger_statuses:
        result += trigger['value']        
    return result

def cost_function(logger, cluster_results,operator = 'MIN'):
    if operator == 'MIN':
        winner = min(cluster_results, key=lambda x: x['result'])
    elif operator == 'MAX':
        winner = max(cluster_results, key=lambda x: x['result'])
    else:
        logger.error("Operator not supported")
        raise kopf.PermanentError("Operator not supported")
    logger.info(f"The cost function declared the winner to be with reward {winner['name']} with a value of {winner['result']}")

    return winner


    
    
if __name__ == "__main__":
    kopf.run()
