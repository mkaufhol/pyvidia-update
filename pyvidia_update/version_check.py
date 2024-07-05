import subprocess


def get_current_nvidia_driver_version():
    try:
        out = subprocess.check_output("nvidia-smi")
        nvidia_driver_version = (
            out.decode("utf-8")
            .split("Driver Version: ")[1]
            .split("CUDA Version")[0]
            .replace(" ", "")
        )
        return nvidia_driver_version
    except Exception:  # noqa
        print("No Nvidia GPU in system!")
        return None
