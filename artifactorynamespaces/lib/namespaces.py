import json
import logging
import yaml
import os

from .helper import as_list


def read_namespaces(config):
    logging.info(f"Reading namespace definitions from '{config.namespaces_file}'")
    with open(config.namespaces_file) as yaml_file:
        namespace_definitions = yaml.safe_load(yaml_file) or {}

    public_patterns = []
    internal_patterns = []
    public_thirdparty_patterns = []
    internal_thirdparty_patterns = []
    namespaces_markdown = []

    out_dir = config.output_dir
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    namespaces_markdown.append(f"| Namespace | Patterns |")
    namespaces_markdown.append(f"| :--- | :--- |")

    for namespace in namespace_definitions.get('namespaces'):
        all_patterns = []
        all_thirdparty_patterns = []
        if namespace.get('publicPattern'):
            public_patterns.append(namespace.get('publicPattern'))
            internal_patterns.append(namespace.get('publicPattern'))
            all_patterns.append(namespace.get('publicPattern'))
        if namespace.get('internalPattern'):
            internal_patterns.append(namespace.get('internalPattern'))
            all_patterns.append(namespace.get('internalPattern'))
        if namespace.get('restrictedPattern'):
            all_patterns.append(namespace.get('restrictedPattern'))

        name = "ns-" + namespace.get('name')
        permission_target = get_permission_target(name, all_patterns,
                                                  config.internal_repos,
                                                  as_list(namespace.get('write')), [])
        write_permission_target(name, config, permission_target)

        # Thirdparty patterns
        if namespace.get('publicThirdpartyPattern'):
            public_thirdparty_patterns.append(namespace.get('publicThirdpartyPattern'))
            internal_thirdparty_patterns.append(namespace.get('publicThirdpartyPattern'))
            all_thirdparty_patterns.append(namespace.get('publicThirdpartyPattern'))
        if namespace.get('internalThirdpartyPattern'):
            internal_thirdparty_patterns.append(namespace.get('internalThirdpartyPattern'))
            all_thirdparty_patterns.append(namespace.get('internalThirdpartyPattern'))
        if namespace.get('restrictedThirdpartyPattern'):
            all_thirdparty_patterns.append(namespace.get('restrictedThirdpartyPattern'))

        name = "ns-" + namespace.get('name') + "-thirdparty"
        permission_target = get_permission_target(name, all_thirdparty_patterns,
                                                  config.thirdparty_repos,
                                                  as_list(namespace.get('write')), [])
        write_permission_target(name, config, permission_target)

        # Create markdown entries
        add_markdown_row(namespace, all_patterns + all_thirdparty_patterns, namespaces_markdown)

    # Write public permission
    permission_target = get_permission_target("global-public", public_patterns,
                                              config.internal_repos, config.public_groups, config.public_users)
    write_permission_target("global-public", config, permission_target)

    # Write internal permission
    permission_target = get_permission_target("global-internal", internal_patterns,
                                              config.internal_repos, config.internal_groups, config.internal_users)
    write_permission_target("global-internal", config, permission_target)

    # Write public thirdparty permission
    permission_target = get_permission_target("global-thirdparty-public", public_thirdparty_patterns,
                                              config.thirdparty_repos, config.public_groups, config.public_users)
    write_permission_target("global-thirdparty-public", config, permission_target)

    # Write internal thirdparty permission
    permission_target = get_permission_target("global-thirdparty-internal", internal_thirdparty_patterns,
                                              config.thirdparty_repos, config.internal_groups, config.internal_users)
    write_permission_target("global-thirdparty-internal", config, permission_target)

    # Write markdown doc
    write_markdown_doc(namespaces_markdown, config)


def write_permission_target(name, config, permission_target):
    if config.output_format == "yaml":
        file_name = config.output_dir + name + '.yaml'
        with open(file_name, 'w+') as permission_file:
            yaml.dump(permission_target, permission_file, default_flow_style=False)
    elif config.output_format == "json":
        file_name = config.output_dir + name + '.json'
        with open(file_name, 'w+') as permission_file:
            json.dump(permission_target, permission_file, indent=4, sort_keys=True)

    logging.info(f"Writing permission target '{name}' to '{file_name}'")


def get_write_permissions() -> list:
    return ["read", "write", "annotate", "delete"]


def get_permission_target(name, includes, repos, groups, users) -> dict:
    groups_permissions = {}
    users_permissions = {}

    for group in groups:
        groups_permissions[group] = get_write_permissions()
    for user in users:
        users_permissions[user] = get_write_permissions()

    return {'name': name,
            'repo': {'include-patterns': includes,
                     'exclude-patterns': [],
                     'repositories': repos,
                     'actions': {'users': users_permissions, 'groups': groups_permissions}}}


def add_markdown_row(namespace: dict, include_patterns: list, markdown_entries):
    patterns = ', '.join(e.replace('*', '\\*') for e in include_patterns)
    markdown_entries.append(f"| {namespace.get('name')} | {patterns} |")


def write_markdown_doc(namespaces: list, config):
    file_name = config.output_dir + 'namespaces.md'
    with open(file_name, 'w+') as markdown_file:
        for entry in namespaces:
            markdown_file.write(f"{entry}\n")

    logging.info(f"Writing markdown doc to '{file_name}'")


class Namespace:
    name: str = ""
    groups: list = []
    users: list = []
    repositories: list = []
    public_patterns: list = []
    internal_patterns: list = []
    restricted_patterns: list = []
    public_thirdparty_patterns: list = []
    internal_thirdparty_patterns: list = []
    restricted_thirdparty_patterns: list = []

    def __init__(self, initial_dict):
        pass
