from kubernetes import client, config

class KubernetesHelper:
    def __init__(self):
        config.load_kube_config()  # Load kubeconfig from local system
        self.v1 = client.CoreV1Api()

    def create_nginx_pod(self):
        pod = client.V1Pod(
            metadata=client.V1ObjectMeta(name="nginx-pod"),
            spec=client.V1PodSpec(containers=[
                client.V1Container(
                    name="nginx",
                    image="nginx",  # Use the nginx image from Docker Hub
                    ports=[client.V1ContainerPort(container_port=80)]
                )
            ])
        )
        self.v1.create_namespaced_pod(namespace="default", body=pod)
        return "Nginx pod created successfully!"

    def list_pods(self):
        pods = self.v1.list_namespaced_pod(namespace="default")
        return [pod.metadata.name for pod in pods.items]
