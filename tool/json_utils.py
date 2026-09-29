import json
import os


class JsonConfig:

    def __init__(self, file_name):
        self.config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
            file_name
        )

    def read_conf(self) -> dict:
        with open(self.config_path, encoding="utf-8") as f:
            return json.load(f)

    def write_conf(self, data: dict) -> None:
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def load_qc_cookie() -> dict:
    return JsonConfig("qc_cookie.json").read_conf()


def save_qc_cookie(data: dict) -> None:
    JsonConfig("qc_cookie.json").write_conf(data)
