from topic_tracking.util.dict import recursive_update
import os
import yaml


def load_yaml_config(root_path, relative_file_path):
    """Parses a YAML configuration file.
    
    Takes _include statements into account.
    """
    
    # load the main file
    file_path = os.path.join(root_path, relative_file_path)
    with open(file_path, 'r') as f:
        data = yaml.load(f)

    if not '_include' in data:
        return data

    # data to be updated
    include_data = {}

    # update the data with content from every file
    for rel_path in data['_include']:
        update_data = load_yaml_config(root_path, rel_path + '.yaml')
        recursive_update(include_data, update_data)

    recursive_update(include_data, data)
    del include_data['_include']

    return include_data
