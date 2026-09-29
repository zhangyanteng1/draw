import os
import yaml
from dotenv import load_dotenv

load_dotenv()

_APP_ENV = os.getenv("APP_ENV", "test")
_CONFIG_FILE = f"config-{_APP_ENV}.yaml"


class BaseConfig:

    def __init__(self, file_name):
        self.configPath = os.sep.join([os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
                                       "config", file_name]).replace("\\", "/")

    def read_conf_all(self) -> dict:
        with open(self.configPath, encoding="utf-8") as f:
            return yaml.load(f, Loader=yaml.FullLoader)


_config_cache: dict = BaseConfig(_CONFIG_FILE).read_conf_all()


def get_app_config(key: str):
    """从 .env 指定的环境配置文件中读取配置项"""
    value = _config_cache.get(key)
    if value is None:
        raise KeyError(f"配置项不存在: {key}")
    return value
