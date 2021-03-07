import yaml

from module.config import load_configurations

DATA_FOLDER = 'tests/config_migration_minimal/data'

def test_new_configuration_loading():
    with open(f'{DATA_FOLDER}/old/settings.yaml', 'r') as yaml_config:
        old_config_map = yaml.load(yaml_config, Loader=yaml.SafeLoader)

    new_config_map = load_configurations(f'{DATA_FOLDER}/new/')

    assert old_config_map == new_config_map