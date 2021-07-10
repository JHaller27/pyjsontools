import pyjson
import sys


data_dir = sys.argv[1]
all_data = pyjson.load_files(data_dir)


def is_valid(data: pyjson.JsonData) -> bool:
    avs = data.one("Product").many("DisplaySkuAvailabilities").one(0).many("Availabilities")

    for avidx, av in enumerate(avs):

        # Has BundleTag
        if av.one("BundleTag").has_data():
            continue

        rems = av.many("Remediations")
        for rem in rems:
            rt = rem.one("Type")

            if rt == "Redirect":
                return False

            elif rt == "ChangeOrder":
                return False

            else:
                return True, avidx

    return False


pyjson.list_files(all_data, is_valid)
