import os
import yaml


def load_configurations(path: str = 'config/'):
    config_map = yaml.load(open(f'{path}/settings.yaml', 'r'), Loader=yaml.SafeLoader)

    config_map["notices_groups"] = dict()

    notices_groups_path = f'{path}/notices_groups'

    for group_file_path in os.listdir(notices_groups_path):
        group_id = group_file_path.replace(".yaml", "")
        group_config = yaml.load(open(f'{notices_groups_path}/{group_file_path}', 'r'), Loader=yaml.SafeLoader)

        config_map["notices_groups"][group_id] = group_config

    return config_map
