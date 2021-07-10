import pyjson


all_data = pyjson.load_files("/home/james/git/CSME-Stores-AIOC-AEM/azureCSharp/Tests/Utilities/Data")
# all_data = pyjson.load_files("/home/james/git/CSME-Stores-AIOC-AEM/adobeIo/jasmineTests/data")
# all_data = pyjson.load_files("./data")

def is_valid(data: pyjson.JsonData) -> bool:
    avs = data.one("Product").many("DisplaySkuAvailabilities").one(0).many("Availabilities")

    for avidx, av in enumerate(avs):

        # Has BundleTag
        if not av.one("BundleTag").has_data():
            continue

        rems = av.many("Remediations")
        rems.any(lambda r: \
            # Has RemediationType = ChangeOrder
            r.one("Type") == "ChangeOrder" and \

            # Has BigIdCardinality = BundleEnforced
            r.one("CartBasedRemediation").one("RequiredBigIdCardinality") == "BundleEnforced" \
        )

        return True, avidx

    return False


pyjson.list_files(all_data, is_valid)
