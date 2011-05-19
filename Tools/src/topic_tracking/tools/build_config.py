from topic_tracking.util.configuration import load_yaml_config
import fnmatch
import os
import sys
import yaml


def find_source_files(root_path):
    """Finds all source files with the name format '[!_]*.yaml'."""

    matches = []
    for root, _, filenames in os.walk(root_path):
        for filename in fnmatch.filter(filenames, '[!_]*.yaml'):
            path = os.path.join(root, filename)# absolute path
            path = os.path.relpath(path, root_path) # path relative to the root
            matches.append(path)
    return matches


def build_config_file(file_path, include_path, destination_path):
    """Takes a source file path relative to the include path and creates an
    output configuration file. Builds necessary folders."""
    
    # build the configuration
    config = load_yaml_config(include_path, file_path)

    # prepare the folder
    output_file = os.path.join(destination_path, file_path)
    output_folder = os.path.dirname(output_file)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # write the file
    with open(output_file, 'w') as f:
        yaml.dump(config, f, indent=4, default_flow_style=False)

    print('Written: %s' % output_file)


if __name__ == '__main__':
    source_path = sys.argv[1]
    destination_path = sys.argv[2]
    files = find_source_files(source_path)
    for f_path in files:
        build_config_file(f_path, source_path, destination_path)
