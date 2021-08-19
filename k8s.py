import logging

from kubernetes import client, config

logging.getLogger().setLevel(logging.INFO)


class Kubernetes:

    _namespace = "trading"

    def __init__(self):
        self.load_k8s_config()
        self.core_api = client.CoreV1Api()
        self.batch_api = client.BatchV1Api()

    @staticmethod
    def make_container(image, name, pull_policy, args):

        container = client.V1Container(
            image=image,
            name=name,
            image_pull_policy=pull_policy,
            env=[],
            args=args,
            command=["python3", "-u", "/monte_carlo_simulator.py"],
        )

        logging.info(
            f"Created container with name: {container.name}, "
            f"image: {container.image} and args: {container.args}"
        )

        return container

    @staticmethod
    def make_pod_template(pod_id, container):
        pod_template = client.V1PodTemplateSpec(
            spec=client.V1PodSpec(restart_policy="Never", containers=[container]),
            metadata=client.V1ObjectMeta(name=pod_id, labels={"name": pod_id}),
        )

        return pod_template

    @staticmethod
    def make_job(job_id, pod_template):
        # metadata
        metadata = client.V1ObjectMeta(name=job_id, labels={"job_name": job_id})

        job = client.V1Job(
            api_version="batch/v1",
            kind="Job",
            metadata=metadata,
            spec=client.V1JobSpec(backoff_limit=0, template=pod_template),
        )

        return job

    def delete_job(self, job):
        logging.info(f"Deleting job {job.metadata.name}.")
        self.batch_api.delete_namespaced_job(
            name=job.metadata.name, namespace=self._namespace
        )

    def delete_pod(self, job):
        job_pods = self.core_api.list_namespaced_pod(
            namespace=self._namespace, label_selector=f"job_name={job.metadata.name}"
        )

        for job_pod in job_pods.items:
            logging.info(f"Deleting pod {job_pod.metadata.name}.")

            self.core_api.delete_namespaced_pod(
                name=job_pod.metadata.name, namespace=self._namespace
            )

    @staticmethod
    def load_k8s_config():

        """ Load the correct configuration """
        try:
            # Cluster config
            config.load_incluster_config()
        except config.config_exception.ConfigException:

            try:
                # Local config
                config.load_kube_config()
            except config.config_exception.ConfigException:

                logging.exception("Could not configure kubernetes python client.")
                raise
