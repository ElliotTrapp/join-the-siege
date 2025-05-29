from dataclasses import dataclass
from pathlib import Path
import yaml

try:
    with open(Path(Path(__file__).parent, 'config.yml'), 'r') as fo:
        yaml_config = yaml.safe_load(fo)
except Exception as e:
    print(f'failed to load config from config.yml, {e}')
    Exception(f'failed to load config from config.yml')

@dataclass
class Config:
    MODEL = yaml_config["model"]
    MAX_DOC_BYTES = yaml_config["max_doc_bytes"]
    MIN_CONFIDENCE = yaml_config["min_confidence"]
    REFERENCE_SENTENCES = yaml_config["reference_sentences"]

config = Config()
