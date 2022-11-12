import os
from typing import Union

import tomlkit

from common.dirs import get_config_dir


def _merge(a: dict, b: dict, path=None):
    """
    Recursively merges b into a, with b taking precedence.

    From: https://stackoverflow.com/a/7205107/965332
    """
    if path is None:
        path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                _merge(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass  # same leaf value
            else:
                a[key] = b[key]
        else:
            a[key] = b[key]
    return a


def _comment_out_toml(s: str):
    return "\n".join(["#" + line for line in s.split("\n")])


def load_config_toml(appname: str, default_config: str) -> Union[dict, tomlkit.container.Container]:
    config_dir = get_config_dir(appname)
    config_file_path = os.path.join(config_dir, f"{appname}.toml")

    # Run early to ensure input is valid toml before writing
    default_config_toml = tomlkit.parse(default_config)

    # Override defaults from existing config file
    if os.path.isfile(config_file_path):
        with open(config_file_path) as f:
            config = f.read()
        config_toml = tomlkit.parse(config)
    else:
        # If file doesn't exist, write with commented-out default config
        with open(config_file_path, "w") as f:
            f.write(_comment_out_toml(default_config))
        config_toml = dict()

    config = _merge(default_config_toml, config_toml)

    return config
