from functools import reduce
from json.decoder import JSONDecodeError
import os
import re
import json
from typing import Any, Callable, Optional, Union
from dataclasses import dataclass


@dataclass
class JsonData:
    path_regex = re.compile(r"\.(?P<pathel>((?P<name>[A-Za-z][\w]*))?(?P<index>\[\d*\])?)|(?P<mismatch>.)")
    path: str
    content: Any

    def __len__(self) -> str:
        return len(self.content)

    def __contains__(self, other) -> bool:
        return other in self.content

    def __iter__(self):
        return map(lambda c: JsonData(path=self.path, content=c), self.content)

    def __getitem__(self, idx: int):
        return JsonData(path=self.path, content=self.content[idx])

    def __eq__(self, other):
        return self.content == other

    def __str__(self) -> str:
        return str(self.content)

    def __repr__(self) -> str:
        return f"JsonData(path='{self.path}', content='{self.content}'"

    def has_data(self) -> bool:
        return self.content is not None and len(self.content) > 0

    def get_path(self, path: str) -> 'JsonData':
        content = self._sub_content(path)
        return JsonData(path=self.path, content=content)

    def _sub_content(self, path: str) -> 'JsonData':
        def _clone_content(content):
            if isinstance(content, dict):
                return dict(content)
            if isinstance(content, list):
                return list(content)
            return content

        some_match = False
        curr = self.content

        for mo in JsonData.path_regex.finditer(path):
            kind = mo.lastgroup
            name = mo['name']
            idx_str = mo['index']

            if kind == "mismatch":
                return JsonData(path=self.path, content=None)

            some_match = True

            if curr is None:
                return JsonData(path=self.path, content=None)

            if not isinstance(curr, list):
                curr = [curr]
            curr = [_clone_content(c) for c in curr]

            if name is not None:
                try:
                    curr = [c.get(name) for c in curr]
                    curr = [x for x in curr if x is not None]
                except AttributeError:
                    return JsonData(path=self.path, content=None)

            if idx_str is not None and curr is not None:
                if not isinstance(curr, list):
                    return JsonData(path=self.path, content=None)

                if idx_str == "[]":
                    curr = reduce(lambda acc, el: acc + el, curr, [])
                    continue

                idx = int(idx_str[1:-1])
                try:
                    # curr = curr[idx]
                    curr = [c[idx] for c in curr if len(c) > idx]
                    # curr = reduce(lambda acc, el: acc + [el[idx]] if idx < len(el) else None, curr)
                    curr = [x for x in curr if x is not None]
                except IndexError:
                    return JsonData(path=self.path, content=None)

            if len(curr) == 0:
                return curr

        if not some_match:
            return JsonData(path=self.path, content=None)

        return curr

    def has_path(self, path: str) -> bool:
        return self.get_path(path) is not None

    def where(self, callback: Callable[['JsonData'], bool]) -> 'JsonData':
        return [d for d in self if callback(d)]

    def any(self, callback: Optional[Callable[['JsonData'], bool]] = None):
        if callback is None:
            callback = lambda _: True

        for jd in self:
            result = callback(jd)
            if result:
                return True

        return False

    def all(self, callback: Optional[Callable[['JsonData'], bool]] = None):
        if callback is None:
            callback = lambda _: True

        for jd in self:
            if not callback(jd):
                return False

        return True


def load_files(start: str, match_fn: Callable[[str], bool] = None, *, recurse: bool = True) -> list[JsonData]:
    if match_fn is None:
        match_fn = lambda p: p.endswith(".json")

    data: list[JsonData] = []

    for root, dnames, fnames in os.walk(start):
        for fname in fnames:
            path = os.path.join(root, fname)
            if not match_fn(path):
                continue

            with open(path, "rb") as fin:
                # Read file as bytes (opened in binary mode)
                bdata = fin.read()

                # Try to decode file content to string
                try:
                    sdata = bdata.decode("utf-8")
                except UnicodeDecodeError:
                    sdata = bdata.decode("latin1")

                # Ignore garbage at beginning
                first_obj_idx = sdata.find("{")
                if first_obj_idx == -1:
                    first_obj_idx = len(sdata)

                first_arr_idx = sdata.find("[")
                if first_arr_idx == -1:
                    first_arr_idx = len(sdata)

                start_json_idx = min(first_obj_idx, first_arr_idx)

                sdata = sdata[start_json_idx:]

                # Try parse as JSON
                content = None
                try:
                    content = json.loads(sdata)
                except JSONDecodeError as err:
                    print(f"Warning: Failed to parse '{path}' as JSON")
                    print(f"\t{err}")
                finally:
                    data.append(JsonData(path=path, content=content))

        # If we're not recursing, return after first loop iteration
        if not recurse:
            return data

    return data


def list_files(data: list[JsonData], filter_fn: Callable[[JsonData], Union[bool, tuple[bool, Any]]] = None) -> list[JsonData]:
    if filter_fn is None:
        filter_fn = lambda _: True

    count = 0
    for d in data:
        result = filter_fn(d)
        if isinstance(result, bool):
            if result:
                print(d.path)
                count += 1

        elif isinstance(result, tuple):
            check, extra = result
            if check:
                print(d.path, "|", str(extra))
                count += 1

    print(f"({count}/{len(data)} match)")


if __name__ == "__main__":
    print("Load files with load_files(start, [match_fn (default: endswith('*.json')], *, recurse=True).")
