import os
import yaml

with open(os.path.join(os.path.dirname(__file__), '../../configs/risk_mapping.yaml'),  'r',encoding='utf-8') as f:
    RISK_MAPPING = yaml.safe_load(f)

def get_polygons(risk_mapping=RISK_MAPPING):
    """
    Hàm lấy thông tin đa giác từ cấu hình risk_mapping.yaml
    """
    polygons = {}
    for zone_name, zone_info in risk_mapping['zones'].items():
        if zone_name != "GLOBAL":
            polygons[zone_name] = zone_info['polygon']
    return polygons

def get_levels(risk_mapping=RISK_MAPPING):
    """
    Hàm lấy thông tin mức độ rủi ro từ cấu hình risk_mapping.yaml
    """
    levels = risk_mapping.get('levels', {})
    return levels

def get_safety_rules(risk_mapping=RISK_MAPPING):
    """
    Hàm lấy quy tắc an toàn từ cấu hình risk_mapping.yaml
    """
    safety_rules = {}
    for zone_name, zone_info in risk_mapping['zones'].items():
        safety_rules[zone_name] = zone_info.get('forbidden_objects', {})
    return safety_rules
if __name__ == "__main__":
    #print(RISK_MAPPING)
    print(get_polygons())
    # print(get_levels())
    # print(get_safety_rules())