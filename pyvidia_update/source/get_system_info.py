import logging
import subprocess


logger = logging.getLogger(__name__)


def get_current_nvidia_driver_version():
    try:
        output = subprocess.check_output(
            "nvidia-smi --query-gpu=driver_version --format=csv,noheader --id=0"
        )
        version = output.decode("utf-8")
        return version.strip()
    except Exception as e:
        logger.error(e)
        return "Current system driver version not found!"
