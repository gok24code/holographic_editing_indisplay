import cv2
import mediapipe as mp
import math
import time
import config

class HandTracker:
    def __init__(self, model_path):
        BaseOptions = mp.tasks.BaseOptions
        HandLandmarker = mp.tasks.vision.HandLandmarker
        HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
        VisionRunningMode = mp.tasks.vision.RunningMode

        options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            running_mode=VisionRunningMode.LIVE_STREAM,
            num_hands=1,
            min_hand_detection_confidence=0.6,
            min_hand_presence_confidence=0.6,
            min_tracking_confidence=0.6,
            result_callback=self._on_result
        )
        self.landmarker = HandLandmarker.create_from_options(options)
        self.latest_result = None
        self.smoothed_x = -1
        self.smoothed_y = -1

    def _on_result(self, result, output_image, timestamp_ms):
        self.latest_result = result

    def process_frame(self, frame, timestamp_ms):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        self.landmarker.detect_async(mp_image, timestamp_ms)

    def get_gesture_and_coords(self, w, h):
        if not self.latest_result or not self.latest_result.hand_landmarks:
            return config.GESTURE_NONE, None, -1, -1

        landmarks = self.latest_result.hand_landmarks[0]
        
        # 1. Fare Koordinatı (İşaret Parmağı ile Baş Parmağın ortası veya sadece işaret)
        # Tony Stark tutuşu için başparmak ve işaret parmağı ortasını kullanmak daha stabildir.
        ix, iy = landmarks[8].x, landmarks[8].y  # İşaret ucu
        tx, ty = landmarks[4].x, landmarks[4].y  # Başparmak ucu
        
        raw_x = int((ix + tx) / 2 * config.SCREEN_W)
        raw_y = int((iy + ty) / 2 * config.SCREEN_H)

        # Exponential Moving Average (EMA) Jitter'ı engeller
        if self.smoothed_x == -1:
            self.smoothed_x, self.smoothed_y = raw_x, raw_y
        else:
            self.smoothed_x = config.SMOOTHING_ALPHA * raw_x + (1 - config.SMOOTHING_ALPHA) * self.smoothed_x
            self.smoothed_y = config.SMOOTHING_ALPHA * raw_y + (1 - config.SMOOTHING_ALPHA) * self.smoothed_y

        # Ekranın dışına çıkmayı engelle
        cx = max(0, min(config.SCREEN_W - 1, int(self.smoothed_x)))
        cy = max(0, min(config.SCREEN_H - 1, int(self.smoothed_y)))

        # 2. Parmak Durumları ve Jest Algılama
        fingers = {
            'index': landmarks[8].y < landmarks[6].y,
            'middle': landmarks[12].y < landmarks[10].y,
            'ring': landmarks[16].y < landmarks[14].y,
            'pinky': landmarks[20].y < landmarks[18].y,
        }
        
        dist_pinch = math.sqrt((landmarks[8].x - landmarks[4].x)**2 + (landmarks[8].y - landmarks[4].y)**2)
        is_pinching = dist_pinch < config.PINCH_THRESHOLD_RATIO

        active_fingers = sum(fingers.values())

        gesture = config.GESTURE_NONE
        
        if active_fingers == 0 and not is_pinching:
            gesture = config.GESTURE_CANCEL # Yumruk
        elif is_pinching:
            gesture = config.GESTURE_GRAB # Tutma / Seçme
        elif active_fingers == 1 and fingers['index']:
            gesture = config.GESTURE_MOVE # Sadece fareyi oynat
        elif active_fingers == 2 and fingers['index'] and fingers['middle']:
            gesture = config.GESTURE_ORBIT # 2 Parmak -> Orta Fare Tuşu (Döndür)
        elif active_fingers == 3 and fingers['index'] and fingers['middle'] and fingers['ring']:
            gesture = config.GESTURE_PAN # 3 Parmak -> Shift + Orta Tuş (Kaydır)
        else:
            gesture = config.GESTURE_MOVE # Tanımsızsa sadece oynat

        return gesture, landmarks, cx, cy

    def close(self):
        self.landmarker.close()
