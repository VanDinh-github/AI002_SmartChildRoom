# src/p3_context/rule_engine.py

from src.utils.load_config import *
from src.utils.helpers import DetectionResult
from typing import Tuple, Optional

class RuleEngine:
    def __init__(self):
        self.rules = get_safety_rules()
        self.levels = get_levels()

    def validate_detection(self, det):
        """
        Node P3.2 & P3.3: Đối soát quy tắc an toàn.
        Trả về: (is_violation, violation_type, severity, message)
        """
        obj_name = det.class_name
        pos = det.position
        
        if obj_name in self.rules.get('GLOBAL', {}):
            is_violation = True
            violation_type = pos
            severity = self.levels.get(self.rules['GLOBAL'][obj_name], "UNKNOWN").get('name', "UNKNOWN")
            message = f"Vật thể '{obj_name}' bị cấm trong khu vực '{pos}'"
            return is_violation, violation_type, severity, message

        if obj_name in self.rules.get('FLOOR', {}):
            is_violation = True
            violation_type = pos
            severity = self.levels.get(self.rules['FLOOR'][obj_name], "UNKNOWN").get('name', "UNKNOWN")
            message = f"Vật thể '{obj_name}' bị cấm trong khu vực '{pos}'"
            return is_violation, violation_type, severity, message
        
        if obj_name in self.rules.get('SHELF', {}):
            is_violation = True
            violation_type = pos
            severity = self.levels.get(self.rules['SHELF'][obj_name], "UNKNOWN").get('name', "UNKNOWN")
            message = f"Vật thể '{obj_name}' bị cấm trong khu vực '{pos}'"
            return is_violation, violation_type, severity, message
        
        return False, None, "INFO", ""

if __name__ == "__main__":
    # Test RuleEngine
    engine = RuleEngine()
    test_det = DetectionResult(class_name="Knife", confidence=0.9, bbox=[100, 150, 200, 250], position="FLOOR", metadata={})
    violation = engine.validate_detection(test_det)
    print(violation)