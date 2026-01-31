# main.py
import os
import sys
import tempfile
from datetime import datetime
import time
from src.utils.load_config import *
# 1. Cấu hình đường dẫn dự án
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# 2. Import các thư viện
import streamlit as st
import cv2
import numpy as np
import pandas as pd

# Import modules dự án
from src.p1_acquisition.data_reader import DataAcquisition
from src.p2_recognition.detector import ObjectDetector
from src.p3_context.rule_engine import RuleEngine
from src.p4_action.alert_manager import AlertManager

# 3. Cấu hình trang 
st.set_page_config(page_title="Smart Home Safety Monitor", layout="wide")

def main():
    st.title("Hệ thống Phát hiện & Cảnh báo Đồ vật nguy hiểm trong phòng trẻ em")
    st.sidebar.header("Cấu hình hệ thống")
    
    # --- STEP 1: CẤU HÌNH INPUT ---
    input_source = st.sidebar.file_uploader("Tải file video", type=["mp4", "avi", "mov"])
    video_path = None
    
    if input_source is not None:
        tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") 
        tfile.write(input_source.read())
        video_path = tfile.name
        tfile.close()
    

    # --- STEP 2: KHỞI TẠO CÁC MODEL TĨNH (Detector, Rules) ---
    if 'detector' not in st.session_state:
        with st.spinner('Đang tải mô hình AI...'):
            st.session_state.detector = ObjectDetector()
            st.session_state.rule_engine = RuleEngine()
            st.session_state.alert_manager = AlertManager()
            st.session_state.alert_logs = [] # Lưu log

    # --- STEP 3: BỐ CỤC GIAO DIỆN ---
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📺 Camera Live Stream")
        video_placeholder = st.empty() # Chỗ để hiển thị video

    with col2:
        st.subheader("⚠️ Danh sách Cảnh báo")
        log_placeholder = st.empty()
        # Nút dừng
        stop_btn = st.button("Dừng giám sát")

    # Nút bắt đầu
    start_btn = st.sidebar.button("Bắt đầu giám sát")
    
    # Biến kiểm soát trạng thái chạy
    if 'is_running' not in st.session_state:
        st.session_state.is_running = False

    if start_btn:
        st.session_state.is_running = True
        # Reset log khi bắt đầu mới
        st.session_state.alert_logs = [] 
    
    if stop_btn:
        st.session_state.is_running = False

    # --- STEP 4: MAIN LOOP ---
    if st.session_state.is_running and video_path:
        # Khởi tạo DataAcquisition mỗi lần chạy để đảm bảo lấy đúng video mới nhất
        acquisition = DataAcquisition(source=video_path)

        prev_time = 0
        fps_display = 0

        # P1: Data Acquisition Loop
        for packet in acquisition.get_stream():
            if not st.session_state.is_running:
                break
            

            raw_frame = packet["raw_frame"]
            
            # P2: Object Recognition
            detections = st.session_state.detector.detect_objects(packet)
            
            for det in detections:
                # P3: Context Analysis
                is_violation, v_type, severity, msg = st.session_state.rule_engine.validate_detection(det)
                if not is_violation:
                    continue
                center_x = (det.bbox[0] + det.bbox[2]) / 2
                center_y = (det.bbox[1] + det.bbox[3]) / 2
                print(f'Tọa độ trung tâm bbox: ({center_x}, {center_y})')
                print(det.bbox)
                if severity == "High Risk":

                    color = (0, 0, 255)  # Red
                elif severity == "Medium Risk":
                    color = (0, 165, 255)  # Orange
                else:
                    color = (0, 255, 255)  # Yellow
                label = f"{det.class_name}"
                print(f"Detection: {label}, Violation: {is_violation}, Type: {v_type}, Severity: {severity}")
                
                # Vẽ Bounding Box
                x1, y1, x2, y2 = det.bbox
                cv2.rectangle(raw_frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(raw_frame, label, (x1, y1 - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

                
                #Vẽ polygon zone
                polygon = get_polygons()
                overlay = raw_frame.copy()
                for zone_name, p in polygon.items():
                    pts = np.array(p, np.int32)
                    pts = pts.reshape((-1, 1, 2))
                    cv2.polylines(overlay, [pts], isClosed=True, color=(0,0,255), thickness=2)
                    cv2.putText(raw_frame, zone_name, tuple(pts[0][0]), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1.5   , ( 51,255,255), 2)
                    cv2.fillPoly(overlay, [pts], (0, 255, 0))
                cv2.addWeighted(overlay, 0.3, raw_frame, 0.7, 0, raw_frame)
                
                # P4: Action Triggering (Chỉ xử lý khi có vi phạm)
                if is_violation:
                    triggered = st.session_state.alert_manager.trigger(det, (is_violation, v_type, severity, msg))
                    if triggered:
                        new_log = {
                            "Thời gian": det.metadata['timestamp'].strftime("%H:%M:%S"),
                            "Vị trí": det.position, # Hiển thị tên tiếng Việt cho đẹp
                            "Vật thể": det.class_name,
                            "Mức độ": severity,
                            "Nội dung": msg
                        }
                        st.session_state.alert_logs.insert(0, new_log)

            # Tính FPS hiển thị
            curr_time = time.time()
            if (curr_time - prev_time) >= 0.0:
                fps_display = int(1.0 / (curr_time - prev_time))
                
            prev_time = curr_time
            # Vẽ FPS lên khung hình, hiển thị chữ to hơn
            cv2.putText(raw_frame, f"FPS: {int(fps_display)}", (20, 40), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0, 255), 2)
            # --- CẬP NHẬT GIAO DIỆN ---
            # Chuyển BGR -> RGB
            frame_rgb = cv2.cvtColor(raw_frame, cv2.COLOR_BGR2RGB)
            video_placeholder.image(frame_rgb, channels="RGB", width=500)
            
            # Cập nhật bảng Log
            if st.session_state.alert_logs:
                df_logs = pd.DataFrame(st.session_state.alert_logs).head(10)
                log_placeholder.table(df_logs)

    elif st.session_state.is_running and not video_path:
        st.warning("Vui lòng tải lên file video trước khi bắt đầu!")
        st.session_state.is_running = False

if __name__ == "__main__":
    main()