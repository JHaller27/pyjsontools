import typer
from pathlib import Path
from typing import Any, Union

import pyjson


def is_valid(*data: pyjson.JsonData) -> Union[tuple[bool, Any], bool]:
    datum = data[0]
    if datum is None:
        return False

    lps = datum.many('Products').many('MarketProperties').many('BundleConfig').many('BundleSlots').many('LocalizedProperties')

    slots = []
    for lp in lps:
        lang = lp.one('Language').value
        slot_title = lp.one('SlotTitle').value
        if lang == 'fr-ca':
            slots.append((slot_title))

    return True, set(slots)


def main(roots: list[Path], recurse: bool = True):
    all_data = pyjson.load_files(*roots, recurse=recurse)
    pyjson.list_files(all_data, filter_fn=is_valid)


if __name__ == "__main__":
    typer.run(main)
