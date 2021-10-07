import os
import json
from pathlib import Path
from typing import Any, Callable, Iterator, Optional, Union


class JsonData:
    def __init__(self, path: Path, content: Any) -> None:
        self._path = path
        self._content = content

    def __eq__(self, other):
        return self._content == other

    def __lt__(self, other: 'JsonData'):
        return self._content < other._content

    def __str__(self) -> str:
        return str(self._content)

    def __repr__(self) -> str:
        return f"JsonData(path='{self._path}', content='{self._content}')"

    def __contains__(self, item) -> bool:
        if not self.has_data():
            return False

        return item in self._content

    @property
    def none(self) -> 'JsonData':
        return JsonData(path=self._path, content=None)

    @property
    def path(self) -> Path:
        return self._path

    @property
    def name(self) -> str:
        return self._path.name

    @property
    def value(self) -> Any:
        return self._content

    def one(self, key: str) -> 'JsonData':
        if key is None:
            return JsonData(path=self._path, content=self._content)

        if not isinstance(self._content, dict):
            return self.none

        content = self._content.get(key)
        return JsonData(path=self._path, content=content)

    def many(self, key: str) -> 'JsonListData':
        if key is None:
            return JsonListData(path=self._path, content=self._content)

        child = self.one(key)
        return JsonListData(path=child._path, content=child._content)

    def has_data(self) -> bool:
        return self._content is not None


class JsonListData(JsonData):
    @property
    def none(self) -> 'JsonListData':
        return JsonListData(path=self._path, content=None)

    def one(self, idx: int) -> 'JsonData':
        if idx is None:
            return JsonData(path=self._path, content=self._content)

        if not isinstance(self._content, list):
            return self.none

        if len(self._content) <= idx:
            return self.none

        content = self._content[idx]
        return JsonData(path=self._path, content=content)

    def many(self, key: str) -> 'JsonListData':
        if key is None:
            return self

        if not isinstance(self._content, list):
            return self.none

        content = []

        for item in self._content:
            if isinstance(item, dict):
                sub_item = item.get(key)

                if sub_item is not None:
                    if isinstance(sub_item, list):
                        content.extend(sub_item)
                    else:
                        content.append(sub_item)

        return JsonListData(path=self._path, content=content)

    def has_data(self) -> bool:
        return super().has_data() and len(self._content) > 0

    def __repr__(self) -> str:
        return f"JsonListData(path='{self._path}', content='{self._content}'"

    def __len__(self) -> int:
        return len(self._content)

    def __iter__(self) -> Iterator[JsonData]:
        if not self.has_data():
            return iter([])

        return map(lambda c: JsonData(path=self._path, content=c), self._content)

    def where(self, callback: Callable[['JsonData'], bool]) -> 'JsonData':
        return JsonListData(path=self._path, content=[d for d in self if callback(d)])

    def any(self, callback: Optional[Callable[['JsonData'], bool]] = None):
        if callback is None:
            def callback(_):
                return True

        for jd in self:
            if callback(jd):
                return True

        return False

    def all(self, callback: Optional[Callable[['JsonData'], bool]] = None):
        if callback is None:
            def callback(_):
                return True

        for jd in self:
            if not callback(jd):
                return False

        return True


def load_files(*starts: str, match_fn: Callable[[str], bool] = None, recurse: bool = True) -> tuple[tuple[JsonData, ...], ...]:
    if match_fn is None:
        def match_fn(p):
            return p.endswith(".json")

    def _load_data_single_dir(start: str) -> dict[str, JsonData]:
        data: dict[str, JsonData] = {}

        for root, d_names, f_names in os.walk(start):
            for fname in f_names:
                path = os.path.join(root, fname)
                if not match_fn(path):
                    continue

                with open(path, "rb") as fin:
                    # Read file as bytes (opened in binary mode)
                    b_data = fin.read()

                    # Try to decode file content to string
                    try:
                        s_data = b_data.decode("utf-8")
                    except UnicodeDecodeError:
                        s_data = b_data.decode("latin1")

                    # Ignore garbage at beginning
                    first_obj_idx = s_data.find("{")
                    if first_obj_idx == -1:
                        first_obj_idx = len(s_data)

                    first_arr_idx = s_data.find("[")
                    if first_arr_idx == -1:
                        first_arr_idx = len(s_data)

                    start_json_idx = min(first_obj_idx, first_arr_idx)

                    s_data = s_data[start_json_idx:]

                    # Try parse as JSON
                    content = None
                    try:
                        content = json.loads(s_data)
                    except json.JSONDecodeError as err:
                        print(f"Warning: Failed to parse '{path}' as JSON")
                        print(f"\t{err}")
                    finally:
                        if fname not in data:
                            data[fname] = JsonData(path=Path(path), content=content)

            # If we're not recursing, return after first loop iteration
            if not recurse:
                return data

        return data

    all_data: tuple[dict[str, JsonData]] = tuple(_load_data_single_dir(start) for start in starts)

    key_set: set[str] = set()
    for data_dict in all_data:
        key_set = key_set.union(set(data_dict.keys()))

    json_data_matches: tuple[tuple[JsonData, ...], ...] = tuple(tuple(d.get(key) for d in all_data) for key in key_set)

    return json_data_matches


def download_files(root: str, ids: list[str], batch_size: int = 20, force: bool = True):
    import requests

    out_root = Path(root)
    index_path: Path = out_root / 'index.json'

    if not force and index_path.is_file():
        with index_path.open('r') as fp:
            existing_ids = json.load(fp)
        ids = list(set(ids) - set(existing_ids))

    all_products = []
    for i in range(0, len(ids), batch_size):
        ids_str = ','.join(ids[i:i + batch_size])
        url = f'https://products.production.store-web.dynamics.com/products/v1/byBigCatId?clientType=storeWeb&catalogIds=1&ids={ids_str}&market=us&languages=en-us&ms-cv=python-test'
        print(url)
        resp = requests.get(url)
        if not resp.ok:
            print(f'Download failed for productIds={ids_str} ({resp.status_code})')
        else:
            all_products.extend(resp.json()['Products'])

    downloaded_count = len(all_products)

    written_count = 0
    new_ids = set()
    for product in all_products:
        filename = product['ProductId'] + '.json'
        path: Path = out_root / filename

        obj = {'Product': product}
        with path.open('w') as fp:
            json.dump(obj, fp)

        written_count += 1
        if product['ProductId'] in new_ids:
            print(f'Overwriting duplicate productId {product["ProductId"]}')
        new_ids.add(product['ProductId'])

    with index_path.open('w') as fp:
        json.dump(list(new_ids), fp)

    return downloaded_count, written_count


def list_files(matched_data: tuple[tuple[JsonData, ...]], filter_fn: Callable[[Optional[JsonData], ...], Union[bool, Union[tuple[bool, Any], bool]]] = None) -> None:
    if filter_fn is None:
        def filter_fn(_):
            return True

    count = 0
    for match in matched_data:
        result = filter_fn(*match)

        if isinstance(result, tuple):
            check, extra = result
            if check:
                print(match[0].name, "|", str(extra))
                count += 1

        else:
            if result:
                print(match[0].name)
                count += 1

    print(f"({count}/{len(matched_data)} match)")


if __name__ == "__main__":
    print("Load files with load_files(start, [match_fn (default: endswith('*.json')], *, recurse=True).")
