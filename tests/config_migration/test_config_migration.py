import yaml, pytest

from module.config import load_configurations

DATA_FOLDER = 'tests/config_migration/data'

@pytest.mark.parametrize("test_case_id", [
    "minimal",
    "two_groups",
    "disum",
    "server_conf"
])
def test_new_configuration_loading(test_case_id):
    test_case_data_folder = f'{DATA_FOLDER}/{test_case_id}'

    with open(f'{test_case_data_folder}/old/settings.yaml', 'r') as yaml_config:
        old_config_map = yaml.load(yaml_config, Loader=yaml.SafeLoader)

    new_config_map = load_configurations(f'{test_case_data_folder}/new/')

    assert old_config_map == new_config_map