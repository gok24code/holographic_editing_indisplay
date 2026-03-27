import cv2
import time
import os
import config
from hand_tracker import HandTracker
from blender_controller import BlenderController
from ui_overlay import render_ui, draw_hand_skeleton, draw_target_ring, draw_text

def list_available_cameras():
    """Sistemdeki aktif kameralari hizli bir sekilde tarar."""
    available_cameras = []
    # Menzili 3'e dusurduk ve sadece isOpened kontrolu yapiyoruz
    for index in range(3):
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            available_cameras.append(index)
            cap.release()
    return available_cameras

def main():
    print("[*] Stark Industries Holographic Interface baslatiliyor...")
    
    # 1. Kamerayi hemen ac (Donanim baslatma suresini maskelemek icin)
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    # 2. Donanim taramasini hizli yap
    cameras = list_available_cameras()
    if cameras: print(f"[*] Aktif kameralar: {cameras}")

    # 3. Model yukleme
    model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hand_landmarker.task')
    if not os.path.exists(model_path):
        print(f"HATA: Model dosyasi bulunamadi: {model_path}")
        return

    tracker = HandTracker(model_path)
    controller = BlenderController()
    
    timestamp = 0
    start_time = time.time()
    frame_count = 0
    fps = 0

    print("STARK INDUSTRIES GESTURE INTERFACE BASLATILDI.")
    print("Kapatmak icin 'q' tusuna basin.")

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break

            frame = cv2.flip(frame, 1) # Ayna Modu
            h, w = frame.shape[:2]
            timestamp += 1
            frame_count += 1

            # FPS Hesapla
            elapsed = time.time() - start_time
            if elapsed > 1.0:
                fps = frame_count / elapsed
                frame_count = 0
                start_time = time.time()

            # 1. MediaPipe İsleme
            tracker.process_frame(frame, timestamp)

            # 2. Veri Çekme ve Eylem
            gesture, landmarks, cx, cy = tracker.get_gesture_and_coords(w, h)
            active_color = config.COLORS.get(gesture, config.COLORS["HUD_BASE"])

            if landmarks:
                # 3. Blender Komutu Gönder (Eğer jest veya pozisyon değiştiyse)
                controller.execute_gesture(gesture, cx, cy)

                # 4. El iskeletini çiz
                draw_hand_skeleton(frame, landmarks, w, h, active_color)

                # 5. Elin merkezine odak halkası çiz
                hand_cx = int(landmarks[9].x * w)
                hand_cy = int(landmarks[9].y * h)
                draw_target_ring(frame, hand_cx, hand_cy, 60, active_color, time.time())
                
                # Parmağın ucuna küçük bir crosshair çiz
                screen_map_x = int(landmarks[8].x * w)
                screen_map_y = int(landmarks[8].y * h)
                cv2.circle(frame, (screen_map_x, screen_map_y), 5, (255, 255, 255), -1)

            else:
                controller.release_all() # El ekrandan çıkarsa her şeyi bırak

            # 6. HUD Çizimi
            render_ui(frame, fps, gesture, active_color, w, h)

            cv2.imshow('HOLOGRAPHIC EDITOR', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except Exception as e:
        print(f"Sistem Hatası: {e}")
    finally:
        controller.release_all()
        tracker.close()
        cap.release()
        cv2.destroyAllWindows()
        print("Sistem Kapatildi.")

if __name__ == "__main__":
    main()
