import pyjson


# all_data = load_files("/home/james/git/CSME-Stores-AIOC-AEM/azureCSharp/Tests/Utilities/Data")
all_data = pyjson.load_files("/home/jahaller/git/CSME-Stores-AIOC-AEM/adobeIo/jasmineTests/data")
# all_data = pyjson.load_files("./data")

def is_valid(data: pyjson.JsonData) -> bool:
    avs = data.get_path(".Product.DisplaySkuAvailabilities[0].Availabilities[]")

    # Has availabilities
    if avs is None or not avs.any():
        return False

    # Has BundleTag
    bundle_tag = avs.get_path(".BundleTag")
    if bundle_tag is None or not bundle_tag.any():
        return False

    # Has remediations
    rems = avs.get_path(".Remediations[]")
    if rems is None or not rems.any():
        return False

    # Has RemediationType = ChangeOrder
    rem_types = rems.get_path(".Type")
    if rem_types is None or not rem_types.any(lambda rt: rt == "ChangeOrder"):
        return False

    # Has BigIdCardinality = BundleEnforced
    cardinality = rems.get_path(".CartBasedRemediation.RequiredBigIdCardinality")
    if cardinality is None or not cardinality.any(lambda c: c == "BundleEnforced"):
        return False

    return True


pyjson.list_files(all_data, is_valid)
