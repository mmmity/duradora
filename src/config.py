import tomllib

with open('config.toml', 'rb') as config_file:
    config = tomllib.load(config_file)
