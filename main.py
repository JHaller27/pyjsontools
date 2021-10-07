import typer
from pathlib import Path
from typing import Any, Union, Optional

import pyjson


def is_valid(*data: Optional[pyjson.JsonData]) -> Union[tuple[bool, Any], bool]:
    bb_datum, seo_datum = data

    if bb_datum is None or seo_datum is None:
        return False, (bb_datum, seo_datum)

    bb_prod_info = bb_datum.one("productInfo")
    bb_price = bb_prod_info.one("price")
    bb_value = bb_price.one("currentValue")

    seo_offers = seo_datum.one("offers")
    seo_value = seo_offers.one("lowPrice")

    return bb_value != seo_value, (bb_value, seo_value)


def main(roots: list[Path], recurse: bool = True):
    all_data = pyjson.load_files(*roots, recurse=recurse)
    pyjson.list_files(all_data, filter_fn=is_valid)


if __name__ == "__main__":
    typer.run(main)
