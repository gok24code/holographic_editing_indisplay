import pyautogui as p

# Ekran Boyutları
SCREEN_W, SCREEN_H = p.size()

# Fare hareketini hızlandırmak ve hata atmasını engellemek için
p.PAUSE = 0
p.FAILSAFE = False

# Yumuşatma Faktörü (Jitter'ı engellemek için, 0 ile 1 arası. 1 = Gecikmesiz ama titrek, 0.2 = Çok yumuşak ama gecikmeli)
SMOOTHING_ALPHA = 0.35

# Jest Durumları
GESTURE_NONE = "NONE"
GESTURE_MOVE = "MOVE"
GESTURE_GRAB = "GRAB"
GESTURE_ORBIT = "ORBIT"
GESTURE_PAN = "PAN"
GESTURE_CANCEL = "CANCEL"

# Renk Şemaları (BGR Formatında - OpenCV Mavi, Yeşil, Kırmızı sırasıyla okur)
COLORS = {
    GESTURE_NONE: (150, 100, 20),      # Koyu Mavi/Gri (Arka plan/Pasif)
    GESTURE_MOVE: (255, 255, 0),       # Parlak Turkuaz (Hareket)
    GESTURE_GRAB: (255, 160, 0),       # Elektrik Mavisi (Tutma)
    GESTURE_ORBIT: (200, 255, 100),    # Açık Su Yeşili/Mavi (Döndürme)
    GESTURE_PAN: (255, 200, 50),       # Gök Mavisi (Kaydırma)
    GESTURE_CANCEL: (100, 50, 255),    # Uyarı Moru/Mavisi (İptal/Yumruk)
    "HUD_BASE": (200, 120, 0),         # Ana HUD Turkuazı
    "TEXT": (255, 255, 255)            # Beyaz
}

# Pinch (Kıstırma) Eşiği - Elin kameraya uzaklığına göre değişebilir
PINCH_THRESHOLD_RATIO = 0.05
