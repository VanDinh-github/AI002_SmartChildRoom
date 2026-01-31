# src/p1_acquisition/data_reader.py

import cv2
import datetime
import time
import numpy as np
from typing import Generator, Dict, Any, Union

from cv2 import VideoCapture
from cv2 import waitKey

class DataAcquisition:
    def __init__(self, source: Union[str, int]):
        """
        Khởi tạo module thu thập dữ liệu (P1).
        :param source: Đường dẫn file video hoặc ID camera (0 cho webcam).
        """
        self.source = source
        self.cap = None

    def _preprocess(self, frame: np.ndarray) -> np.ndarray:
        """
        Node P1.2: Tiền xử lý khung hình (Resize)
        """
        # 1. Resize về 640x640 
        resized = cv2.resize(frame, (640, 640))

        return resized

    def get_stream(self) -> Generator[Dict[str, Any], None, None]:
        """
        Trả về một dictionary chứa đầy đủ dữ liệu và metadata.
        """
        self.cap = cv2.VideoCapture(self.source)

        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            timestamp = datetime.datetime.now()
            
            # Thực hiện tiền xử lý
            processed_frame = self._preprocess(frame)

            # Đóng gói dữ liệu đầu ra của P1
            data_packet = {
                "raw_frame": frame,          
                "processed_frame": processed_frame,
                "metadata": {
                    "timestamp": timestamp,
                    "frame_height": frame.shape[0],
                    "frame_width": frame.shape[1]
                }
            }

            yield data_packet

        self.cap.release()

# --- Đoạn mã chạy thử nghiệm  ---
if __name__ == "__main__":
    acquisition = DataAcquisition(source='./data/kitchenroom1.mp4')
    
    for packet in acquisition.get_stream():
        frame = packet["raw_frame"]
        meta = packet["metadata"]
        
        # Hiển thị thông tin metadata lên frame
        cv2.putText(frame, f"Ahii - Timestamp: {meta['timestamp']}", 
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        cv2.imshow("Module P1 Test - Press Q to exit", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()