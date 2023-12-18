from typing import List, Dict

feature_type_map = {"float": "Fractional", "long": "Integral", "string": "String"}


def format_feature_def(feature_def: Dict):
    retval = {"FeatureName": feature_def["name"]}
    retval["FeatureType"] = feature_type_map[feature_def["type"]]
    return retval


def format_feature_defs(feature_definitions: List[Dict]):
    return [format_feature_def(k) for k in feature_definitions]
