import pyjson


# all_data = load_files("/home/james/git/CSME-Stores-AIOC-AEM/azureCSharp/Tests/Utilities/Data")
all_data = pyjson.load_files("/home/jahaller/git/CSME-Stores-AIOC-AEM/adobeIo/jasmineTests/data")
# all_data = pyjson.load_files("./data")

def is_valid(data: pyjson.JsonData) -> bool:
    def _is_av_valid(av: pyjson.JsonData):
        if av is None:
            return False

        # Has BundleTag
        bundle_tag = av.get_path(".BundleTag")
        if bundle_tag is None or not bundle_tag.any():
            return False

        # Has remediations
        rems = av.get_path(".Remediations[]")
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

    avs = data.get_path(".Product.DisplaySkuAvailabilities[0].Availabilities[]")
    if avs is None:
        return False

    return avs.any(_is_av_valid)


pyjson.list_files(all_data, is_valid)
