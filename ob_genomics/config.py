import os
import os.path as op

import yaml

# All configuration is matched to an environment (ENV)
ENV = os.environ.get('ENV', 'test')

CONFIG_FILE = op.join(op.dirname(__file__), '..', 'config.yml')
with open(CONFIG_FILE) as f:
    cfg = yaml.load(f)[ENV]

# Add back the environment
cfg['ENV'] = ENV

cfg['REFERENCE'] = op.expanduser(cfg['REFERENCE'])
cfg['SCRATCH'] = op.expanduser(cfg['SCRATCH'])

cfg['TEST_GENES'] = [3845, 7157, 4609, 2597]
cfg['TEST_ISOFORMS'] = ['uc001aaa.3', 'uc001aab.3', 'uc001aac.3', 'uc001aae.3', 'uc001aah.3', 'uc001aai.1', 'uc001aak.2', 'uc001aal.1']

cfg['TCGA'] = {
    
}