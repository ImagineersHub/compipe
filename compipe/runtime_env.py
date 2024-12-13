import logging
import os
import sys
from typing import Any, Dict, Union

from .utils.access import AccessHub
from .utils.logging import logger
from .utils.io_helper import json_loader
from .utils.parameters import (
    ARG_CONSOLE, ARG_DEBUG, ARG_DEV_CHANNEL, ARG_DEV, ARG_PROD,
    ARG_EXECUTABLE_TOOLS, ARG_LOCAL_DRIVE, ARG_OUT_OF_SERVICE,
    ARG_PYTHON_MODULES, ARG_QUEUE_WORKER_NUM, ARG_RESOURCE,
    ARG_SUBPROCESS_NUM, ARG_BASE
)
from .utils.singleton import ThreadSafeSingleton

# Restrict log levels for less relevant modules
logging.getLogger("matplotlib").setLevel(logging.WARNING)  # noqa
logging.getLogger("PIL").setLevel(logging.WARNING)  # noqa
logging.getLogger('trimesh').setLevel(logging.WARNING)  # noqa
logging.getLogger('shapely').setLevel(logging.WARNING)  # noqa


class ClassProperty:
    """
    A descriptor that emulates @property behavior at the class level.
    Allows accessing class-level attributes as if they were properties.
    """
    def __init__(self, getter):
        self.getter = getter

    def __get__(self, instance, owner):
        return self.getter(owner)


class Environment(metaclass=ThreadSafeSingleton):
    """
    A singleton environment class for managing runtime parameters and configurations.
    Provides functionality to:
    - Initialize runtime parameters.
    - Load and merge platform-specific server configurations.
    - Manage runtime snapshots (to revert to previous states).
    - Dynamically update system and Python paths based on configuration.
    """

    def __init__(self, *args, console_mode: bool = False, **kwargs):
        # Holds a copy of runtime parameters for potential restoration
        self.snapshot: Dict[str, Any] = {}

        # Normalize string parameters to lowercase
        self.param: Dict[str, Any] = {
            key: (value.lower() if isinstance(value, str) else value)
            for key, value in kwargs.items()
        }

        # Update parameters with console mode setting
        self.param[ARG_CONSOLE] = console_mode

        # The following line was commented out in original code:
        # self.update(AccessHub().server_configs)

    @classmethod
    def register_credentials(cls, key_dict: Dict[str, Any] = {}):
        """
        Register or update credentials from the given dictionary.
        This typically merges external credentials into the global AccessHub key store.
        """
        AccessHub().keys.update(key_dict)

    @classmethod
    def append_server_config(cls, payload: Dict[str, Any] = {}):
        """
        Add or update server configuration parameters into the Environment.
        
        The payload typically contains platform-specific configuration overrides
        (e.g., number of workers, executable tool paths, etc.).

        Example Payload:
        {
            "win32": {
                "queue_worker_num": 1,
                "subprocess_num": 2,
                "dev_channel": "T015BP2HUU9#G015P1L6L7J",
                "oos": false,
                "debug": true,
                "executable_tools": {
                    "blender": "P:\\Editors\\Blender\\blender-2.93.3-windows-x64",
                    "cyclicgen": "P:\\Editors\\CyclicGen",
                    "unity": "C:\\Dev\\Editors\\Unity\\2020.3.24f1\\Editor"
                },
                "dnn_models": {
                    "swinir_denoising_15": "D:\\Trained_Models\\SwinIR\\Model\\004_grayDN_DFWB_s128w8_SwinIR-M_noise15.pth",
                    "swinir_denoising_25": "D:\\Trained_Models\\SwinIR\\Model\\004_grayDN_DFWB_s128w8_SwinIR-M_noise25.pth",
                    "swinir_denoising_50": "D:\\Trained_Models\\SwinIR\\Model\\004_grayDN_DFWB_s128w8_SwinIR-M_noise50.pth"
                },
                "mars_dicom_data_root": "G:\\Shared drives"
            }
        }
        """
        Environment().param.update(payload)

        # Update system PATH with executable tool paths
        for key, path in Environment().param.get(ARG_EXECUTABLE_TOOLS, {}).items():
            if not path:
                logger.debug(f'Executable Tool [{key}] path is invalid!')
            else:
                logger.debug(
                    f'Executable Tool [{key}]: Adding path [{path}] to system PATH.'
                )
                os.environ["PATH"] += os.pathsep + path

        # Update Python sys.path with external Python module paths
        for key, path in Environment().param.get(ARG_PYTHON_MODULES, {}).items():
            if not path:
                logger.debug(f'Python module [{key}] path is invalid!')
            else:
                logger.debug(
                    f'Python module [{key}]: Adding path [{path}] to sys.path.'
                )
                sys.path.append(path)

    def save_snapshot(self):
        """
        Saves a snapshot of the current environment parameters.
        This can be used later to reset the environment to this exact state.
        """
        self.snapshot = self.param.copy()

    def reset(self):
        """
        Resets the environment parameters to the most recently saved snapshot.
        If no snapshot has been saved, logs a warning and does nothing.
        """
        if not self.snapshot:
            logger.warning('No snapshot of the runtime environment found!')
            return
        self.param = self.snapshot.copy()

    def get(self, key: str, default: Any = None) -> Any:
        """
        Retrieves a parameter by key from the environment parameters.
        Returns the given default if the key is not found.
        """
        return self.param.get(key, default)

    def get_value_by_path(self, keys: list, default: Any = None) -> Any:
        """
        Retrieves a nested configuration value by a chain of keys.

        Example:
        keys = ['executable_tools', 'blender'] 
        returns the value of Environment().param['executable_tools']['blender'] if it exists.

        If any key in the chain is missing, returns the provided default.
        """
        cfg = self.param
        for key in keys:
            cfg = cfg.get(key, None)
            if cfg is None:
                return default
        return cfg or default

    @ClassProperty
    def console_mode(cls) -> bool:
        """Indicates if the environment is running in console mode."""
        return Environment().param.get(ARG_CONSOLE, True)

    @ClassProperty
    def debug_mode(cls) -> bool:
        """Indicates if the environment is running in debug mode."""
        return Environment().param.get(ARG_DEBUG, False)

    @ClassProperty
    def resource(cls) -> Any:
        """Returns the configured resource (e.g., path to resources) if any."""
        return Environment().param.get(ARG_RESOURCE, None)

    @ClassProperty
    def dev_channel(cls) -> str:
        """Returns the Slack/communication channel for development messages."""
        return Environment().param.get(ARG_DEV_CHANNEL, None)

    @ClassProperty
    def out_of_service(cls) -> bool:
        """Indicates if the environment is set to 'out of service' mode."""
        return Environment().param.get(ARG_OUT_OF_SERVICE, False)

    @ClassProperty
    def worker_num(cls) -> int:
        """Returns the number of queue workers configured."""
        return Environment().param.get(ARG_QUEUE_WORKER_NUM, 1)

    @ClassProperty
    def subprocess_num(cls) -> int:
        """Returns the number of subprocesses configured."""
        return Environment().param.get(ARG_SUBPROCESS_NUM, 5)

    @ClassProperty
    def local_drive(cls) -> str:
        """Returns the local drive or filesystem path configured."""
        return Environment().param.get(ARG_LOCAL_DRIVE, None)

    def __str__(self) -> str:
        """
        Returns a human-readable string representation of the environment.
        """
        return (
            '==========ENV==========\n'
            f'{ "|".join(["dev_channel"]) }\n'
            f'{ "|".join([Environment.dev_channel]) }\n'
            '==========ENV=========='
        )


def initialize_runtime_environment(
    params: Dict[str, Any],
    runtime_cfg_path: str,
    credential_cfg: Union[str, Dict[str, Any]] = None,
    console_mode: bool = True
):
    """
    Initialize the runtime environment with the given parameters and configuration files.

    Args:
        params (dict): Base parameters to initialize the environment.
        runtime_cfg_path (str): Path to the local server runtime configuration file.
        credential_cfg (str|dict): Path to a credential config file or a dict of credentials.
        console_mode (bool): Whether to run in console mode.

    Raises:
        FileNotFoundError: If the runtime configuration file or credential file is not found.
        ValueError: If configuration for the current platform cannot be found.
    """

    # Include the current platform in parameters
    params.update({'platform': sys.platform})

    # Create or retrieve the singleton Environment instance
    env = Environment(console_mode=console_mode, **params)

    # Verify runtime configuration file exists
    if not os.path.exists(runtime_cfg_path):
        raise FileNotFoundError(
            f"Local server runtime config file not found at {runtime_cfg_path}"
        )

    # Load environment configuration
    env_config = json_loader(runtime_cfg_path)
    base_config = env_config.get(ARG_BASE, {})

    # Retrieve platform-specific configuration, or raise error if not found
    platform_config = env_config.get(sys.platform, None)
    if platform_config is None:
        raise ValueError(
            f"No local server runtime config found for platform {sys.platform}"
        )

    # Merge platform config into base config
    base_config.update(platform_config)

    # Apply the combined configuration to the environment
    env.append_server_config(base_config)

    # Handle credential configuration
    if not credential_cfg:
        logger.warning("Skipping credential config loading.")
    else:
        # If credential_cfg is a path, load it from file
        if isinstance(credential_cfg, str):
            if not os.path.exists(credential_cfg):
                raise FileNotFoundError(
                    f"Credential file not found at {credential_cfg}"
                )
            credential_cfg = json_loader(credential_cfg)

        # Select credentials based on debug or production mode
        env_credentials = credential_cfg.get(ARG_DEV if env.debug_mode else ARG_PROD, {})
        env.register_credentials(key_dict=env_credentials)

    # Save the current state of environment variables as a snapshot
    env.save_snapshot()
