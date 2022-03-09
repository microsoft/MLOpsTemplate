from azureml.core.compute import ComputeTarget, AmlCompute
from azureml.core.compute_target import ComputeTargetException
import logging
import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '../..')))
from scripts.authentication.service_principal import ws
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

def create_compute_cluster(workspace=None, compute_name=None):
    """Create AML compute cluster"""
    try:
        cpu_cluster = ComputeTarget(workspace=workspace, name=compute_name)
        logging.info('Found existing cluster, use it.')
    except ComputeTargetException:
        # To use a different region for the compute, add a location='<region>' parameter
        compute_config = AmlCompute.provisioning_configuration(
                vm_size='STANDARD_DS3_v2',
                min_nodes=1,
                max_nodes=4)
        cpu_cluster = ComputeTarget.create(workspace, compute_name, compute_config)
        logging.info(f'Triggered the creation of {compute_name} cluster')
        cpu_cluster.wait_for_completion(show_output=True)

def main():
    """Main operational flow"""
    cluster_name='cpu-cluster'
    create_compute_cluster(
            workspace=ws, 
            compute_name=cluster_name
            )

if __name__ == "__main__":
    main()
