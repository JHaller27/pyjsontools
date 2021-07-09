import os
import json
from typing import Callable
import pyjson


def load_files(start: str, match_fn: Callable[[str], bool] = None, *, recurse: bool = True) -> list:
    if match_fn is None:
        match_fn = lambda p: p.endswith(".json")

    data = []

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
                except json.JSONDecodeError as err:
                    print(f"Warning: Failed to parse '{path}' as JSON")
                    print(f"\t{err}")
                finally:
                    data.append((path, content))

        # If we're not recursing, return after first loop iteration
        if not recurse:
            return data

    return data


# all_data = load_files("/home/james/git/CSME-Stores-AIOC-AEM/azureCSharp/Tests/Utilities/Data")
all_data = pyjson.load_files("/home/james/git/CSME-Stores-AIOC-AEM/adobeIo/jasmineTests/data")
# all_data = pyjson.load_files("./data")
print(len(all_data))

def is_valid(data: pyjson.JsonData) -> bool:
    try:
        avs = data.get_path(".Product.DisplaySkuAvailabilities[0].Availabilities[]")
        if avs is None:
            return False

        for avidx, av in enumerate(avs):
            if av is None:
                return False

            # Has BundleTag
            bundle_tag = av.get_path(".BundleTag")
            if bundle_tag is None or not bundle_tag.any():
                continue

            rems = av.get_path(".Remediations[]")
            if rems is None or not rems.any():
                continue

            rem_types = rems.get_path(".Type")
            if rem_types is None or not rem_types.any(lambda rt: rt == "ChangeOrder"):
                continue

            # for rem in rems:
            #     # Remediation.Type is ChangeOrder
            #     rem_type = rem.get_path(".Type")
            #     if rem_type is None or rem_type == "ChangeOrder":
            #         continue

        #         # BigIdCardinality is BundleEnforced
        #         cardinality = rem.get("CartBasedRemediation").get("RequiredBigIdCardinality")
        #         if cardinality is None or cardinality != "BundleEnforced":
        #             continue

        #         print(avidx, path)

            return True

        return False

    except (AttributeError, TypeError):
        return False


filtered_data = list(filter(is_valid, all_data))
# filtered_data = [d for d in all_data if d.get_path(".Product.DisplaySkuAvailabilities[].Availabilities[].Remediations[].RemediationId") is not None]
# print("\n".join([d[0] for d in filtered_data]))
print(len(filtered_data))
