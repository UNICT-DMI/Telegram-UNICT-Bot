import yaml

from module.config import load_configurations

# def test_new_configuration_loading():
#     with open('tests/config_migration/data/old/settings.yaml', 'r') as yaml_config:
#         old_config_map = yaml.load(yaml_config, Loader=yaml.SafeLoader)

#     new_config_map = load_configurations('tests/config_migration/data/new/')

#     assert old_config_map == new_config_map