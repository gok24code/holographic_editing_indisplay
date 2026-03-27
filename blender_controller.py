import pyautogui as p
import config

class BlenderController:
    def __init__(self):
        self.current_state = config.GESTURE_NONE
        
    def execute_gesture(self, gesture, cx, cy):
        # Durum değişmediyse sadece fareyi hareket ettir (spam engelleme)
        if gesture == self.current_state:
            # Sadece Cancel durumunda fare oynamasın
            if gesture != config.GESTURE_CANCEL:
                p.moveTo(cx, cy)
            return

        print(f"[*] TRANSITION: {self.current_state} -> {gesture}")
        
        # 1. Eski Durumu Temizle (Clean up previous state)
        self._release_current_state()
        
        # 2. Yeni Duruma Geç (Apply new state)
        self.current_state = gesture
        self._apply_new_state(gesture)
        
        # 3. Fareyi taşı (ilk hareket)
        if gesture != config.GESTURE_CANCEL:
            p.moveTo(cx, cy)

    def _release_current_state(self):
        if self.current_state == config.GESTURE_GRAB:
            p.mouseUp(button='left')
        elif self.current_state == config.GESTURE_ORBIT:
            p.mouseUp(button='middle')
        elif self.current_state == config.GESTURE_PAN:
            p.keyUp('shift')
            p.mouseUp(button='middle')

    def _apply_new_state(self, gesture):
        if gesture == config.GESTURE_GRAB:
            p.mouseDown(button='left')
        elif gesture == config.GESTURE_ORBIT:
            p.mouseDown(button='middle')
        elif gesture == config.GESTURE_PAN:
            p.keyDown('shift')
            p.mouseDown(button='middle')
        elif gesture == config.GESTURE_CANCEL:
            p.press('esc')
            
    def release_all(self):
        self._release_current_state()
        self.current_state = config.GESTURE_NONE
