"""Configuration map"""
import os
import yaml
from .types import Config


def load_configurations(path: str = "config/") -> Config:
    """Load the configuration files from the given path
    and return a dictionary containing the configuration data.

    Args:
        path: path to the configuration files

    Returns:
        dictionary containing the configuration data
    """
    with open(os.path.join(path, "settings.yaml"), "r", encoding="utf-8") as main_settings:
        new_config = yaml.load(main_settings, Loader=yaml.SafeLoader)

        new_config["notices_groups"] = {}

        notices_groups_path = f"{path}/notices_groups"

        for group_file_path in os.listdir(notices_groups_path):
            group_id = group_file_path.replace(".yaml", "")
            full_group_path = os.path.join(notices_groups_path, group_file_path)
            with open(full_group_path, "r", encoding="utf-8") as group_file:
                new_config["notices_groups"][group_id] = yaml.load(group_file, Loader=yaml.SafeLoader)

    return new_config


config_map: Config = load_configurations()
