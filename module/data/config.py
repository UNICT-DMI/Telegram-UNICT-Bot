"""Configuration map"""
import os
from typing import TypedDict
import yaml


class PageConfig(TypedDict):
    """page sub-configuration type definition"""

    label: str
    urls: "list[str]"
    channels: "list[str | int]"


class GroupConfig(TypedDict):
    """group sub-configuraiton type definition"""

    base_url: str
    approval_group_chatid: "int | None"
    pages: "dict[str, PageConfig]"


class Config(TypedDict):
    """config_map type definition"""

    token: str
    dev_group_chatid: int
    log_group_chatid: int
    logfile_reset_interval_minutes: int
    update_interval: int
    max_messages_length: int
    max_length_footer: str
    max_connection_tries: int
    notices_groups: "dict[str, GroupConfig]"


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
