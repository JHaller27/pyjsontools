import pyjson


all_data = pyjson.load_files("/home/james/git/CSME-Stores-AIOC-AEM/azureCSharp/Tests/Utilities/Data")
# all_data = pyjson.load_files("/home/james/git/CSME-Stores-AIOC-AEM/adobeIo/jasmineTests/data")
# all_data = pyjson.load_files("./data")

def is_valid(data: pyjson.JsonData) -> bool:
    avs = data.get_path(".Product.DisplaySkuAvailabilities[0].Availabilities[]")

    for avidx, av in enumerate(avs):

        # Has BundleTag
        if not av.get_path(".BundleTag").has_data():
            continue

        rems = av.get_path(".Remediations[]")
        rems.any(lambda r: r.get_path(".Type"))

        # Has RemediationType = ChangeOrder
        rem_types = rems.get_path(".Type")
        if not rem_types.any(lambda rt: rt == "ChangeOrder"):
            continue

        # Has BigIdCardinality = BundleEnforced
        cardinality = rems.get_path(".CartBasedRemediation.RequiredBigIdCardinality")
        if cardinality.any(lambda c: c != "BundleEnforced"):
            continue

        return True, avidx

    return False


pyjson.list_files(all_data, is_valid)
