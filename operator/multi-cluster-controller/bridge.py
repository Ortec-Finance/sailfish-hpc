import kubernetes
import kubernetes.client
from kubernetes.client.rest import ApiException


class Bridge:
    def __init__(self, SAILFISH_BROKER_NAME):
        self.SAILFISH_BROKER_NAME = SAILFISH_BROKER_NAME

    def fetch_activemq_artemis(self, name, namespace, logger):
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
            logger.error(
                f"A ActiveMQArtemis broker is not deployed in this namespace: {e}"
            )
            return None

    def update_activemq_artemis(self, name, namespace, patch, logger):
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
        self, name, namespace, cluster_name, owner_reference, logger
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
                "applyToCrNames": [self.SAILFISH_BROKER_NAME],
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
