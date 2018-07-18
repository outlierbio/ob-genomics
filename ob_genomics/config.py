import os
import os.path as op

import yaml

# All configuration is matched to an environment (ENV)
ENV = 'prod' if os.environ.get('ENV') == 'prod' else 'test'

CONFIG_FILE = op.join(op.dirname(__file__), '..', 'config.yml')
with open(CONFIG_FILE) as f:
    cfg = yaml.load(f)[ENV]

# Add back the environment
cfg['ENV'] = ENV
