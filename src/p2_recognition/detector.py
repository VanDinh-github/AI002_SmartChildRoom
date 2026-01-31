# src/p2_recognition/detector.py

from ultralytics import YOLO
import numpy as np
from typing import List
from src.utils.helpers import DetectionResult  
from src.utils.position_classification import bbox_in_zone
from src.utils.load_config import get_polygons

class ObjectDetector:
    def __init__(self, model_path: str = "yolov8x-oiv7.pt", confidence_threshold: float = 0.3):
        """
        Khởi tạo Module P2: Nhận diện vật thể.
        :param model_path: Đường dẫn tới trọng số YOLOv8.
        :param confidence_threshold: Ngưỡng tin cậy để lọc các nhận diện nhiễu 
        """
        
        try:
            self.model = YOLO(model_path)
        except Exception as e:
            print(f"[Error] Không thể tải model: {e}")
            raise

        self.conf_threshold = confidence_threshold

    def _classify_position(self, bbox) -> bool:
       polygons = get_polygons()
       for zone_name, zone_polygon in polygons.items():
           if bbox_in_zone(bbox, zone_polygon):
               print(f'Object in zone: {zone_name}')
               return zone_name
       return "GLOBAL"

    def detect_objects(self, data_packet: dict) -> List[DetectionResult]:
        """
        Thực hiện nhận diện và phân loại vị trí.
        :param data_packet: Packet từ Module P1 chứa processed_frame và metadata.
        :return: Danh sách các đối tượng DetectionResult.
        """
        # Đầu vào là processed_frame (640x640) từ P1
        img = data_packet["processed_frame"]
        frame_h = data_packet["metadata"]["frame_height"]
        frame_w = data_packet["metadata"]["frame_width"]

        # 1. Chạy Inference (Dự đoán)
        results = self.model.predict(source=img, conf=self.conf_threshold, verbose=False, device='cpu')
        
        detections = []
        
        # 2. Xử lý kết quả trả về từ YOLOv8
        for r in results:
            boxes = r.boxes
            for box in boxes:
                # Lấy tọa độ bbox (định dạng xyxy)
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                
                # Tính toán vị trí (Node P2.3)
                # Dùng y1, y2 trên khung hình 640 để tính tỉ lệ relative_y
                
                # Chuyển đổi tọa độ ngược lại kích thước raw_frame để vẽ sau này
                scale_x = frame_w / 640
                scale_y = frame_h / 640
                original_bbox = [
                    int(x1 * scale_x), int(y1 * scale_y), 
                    int(x2 * scale_x), int(y2 * scale_y)
                ]
                position = self._classify_position(original_bbox)

                # Tạo đối tượng DetectionResult 
                obj = DetectionResult(
                    class_name=self.model.names[int(box.cls)],
                    confidence=float(box.conf),
                    bbox=original_bbox,
                    position=position,
                    metadata=data_packet["metadata"]
                )
                
                detections.append(obj)

        return detections

# --- Đoạn mã chạy thử nghiệm (Unit Test cho Module P2) ---
if __name__ == "__main__":
    from src.p1_acquisition.data_reader import DataAcquisition
    import cv2

    # Giả lập pipeline P1 -> P2
    acquisition = DataAcquisition(source='./data/kitchenroom1.mp4')
    detector = ObjectDetector()

    for packet in acquisition.get_stream():
        print(packet)
        
        results = detector.detect_objects(packet)
        
        raw_img = packet["raw_frame"]
        for res in results:
            x1, y1, x2, y2 = res.bbox
            # Vẽ bounding box và thông tin vị trí
            color = (0, 255, 0) # Mặc định xanh lá
            cv2.rectangle(raw_img, (x1, y1), (x2, y2), color, 2)
            cv2.putText(raw_img, f"{res.class_name} ({res.position})", 
                        (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        cv2.imshow("Module P2 Test - Press Q to exit", raw_img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()