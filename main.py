from typing import Any
import pyjson
import sys


data_dir = sys.argv[1]
all_data = pyjson.load_files(data_dir)


def wrong_order(lst: list):
    for i in range(len(lst) - 1):
        if lst[i] > lst[i+1]:
            return True

    return False


def is_valid(data: pyjson.JsonData) -> tuple[bool, Any]:
    family = data.one("Product").one("ProductFamily")
    pid = data.one("Product").one("ProductId")
    # return family == "Bundles", family
    return pid.has_data() and pid.value.upper() == "CFQTTC0K5DM", family


pyjson.list_files(all_data, is_valid)
