import cv2
import numpy as np
import time
import math
from config import COLORS

def draw_hud_panel(frame, x, y, w, h, color, alpha=0.35):
    overlay = frame.copy()
    cv2.rectangle(overlay, (x, y), (x + w, y + h), (0, 0, 0), -1)
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
    # Köşeler
    size = 12
    thickness = 2
    cv2.line(frame, (x, y), (x + size, y), color, thickness)
    cv2.line(frame, (x, y), (x, y + size), color, thickness)
    cv2.line(frame, (x + w, y), (x + w - size, y), color, thickness)
    cv2.line(frame, (x + w, y), (x + w, y + size), color, thickness)
    cv2.line(frame, (x, y + h), (x + size, y + h), color, thickness)
    cv2.line(frame, (x, y + h), (x, y + h - size), color, thickness)
    cv2.line(frame, (x + w, y + h), (x + w - size, y + h), color, thickness)
    cv2.line(frame, (x + w, y + h), (x + w, y + h - size), color, thickness)
    cv2.rectangle(frame, (x, y), (x + w, y + h), (*color[::-1], 60), 1)

def draw_text(frame, text, x, y, scale=0.5, color=(0, 255, 160), thickness=1):
    font = cv2.FONT_HERSHEY_DUPLEX
    cv2.putText(frame, text, (x + 1, y + 1), font, scale, (0, 0, 0), thickness + 1)
    cv2.putText(frame, text, (x, y), font, scale, color, thickness)

def draw_hand_skeleton(frame, landmarks, w, h, color):
    connections = [
        (0,1),(1,2),(2,3),(3,4),
        (0,5),(5,6),(6,7),(7,8),
        (0,9),(9,10),(10,11),(11,12),
        (0,13),(13,14),(14,15),(15,16),
        (0,17),(17,18),(18,19),(19,20),
        (5,9),(9,13),(13,17),
    ]
    pts = [(int(lm.x * w), int(lm.y * h)) for lm in landmarks]

    for a, b in connections:
        cv2.line(frame, pts[a], pts[b], color, 1)

    for i, pt in enumerate(pts):
        if i in [4, 8, 12, 16, 20]: # Parmak Uçları
            cv2.circle(frame, pt, 5, color, -1)
            cv2.circle(frame, pt, 7, color, 1)
        else:
            cv2.circle(frame, pt, 3, color, -1)

def draw_target_ring(frame, cx, cy, radius, color, t):
    for i in range(2):
        alpha_ring = 0.15 - i * 0.05
        ov = frame.copy()
        cv2.circle(ov, (cx, cy), radius + i * 4, color, 1)
        cv2.addWeighted(ov, alpha_ring, frame, 1 - alpha_ring, 0, frame)

    cv2.circle(frame, (cx, cy), radius, color, 1)
    angle = (t * 4) % 360
    rad = math.radians(angle)
    ex = int(cx + radius * math.cos(rad))
    ey = int(cy + radius * math.sin(rad))
    cv2.line(frame, (cx, cy), (ex, ey), color, 2)
    cv2.circle(frame, (cx, cy), 3, color, -1)

def render_ui(frame, fps, gesture, active_color, w, h):
    t = time.time()
    
    # Tarama çizgileri
    overlay = frame.copy()
    for y in range(0, h, 4):
        cv2.line(overlay, (0, y), (w, y), (0, 0, 0), 1)
    cv2.addWeighted(overlay, 0.05, frame, 0.95, 0, frame)

    # Üst Bar
    draw_hud_panel(frame, 10, 10, w - 20, 40, active_color)
    draw_text(frame, "STARK INDUSTRIES | HOLOGRAPHIC INTERFACE", 20, 35, 0.5, active_color)
    draw_text(frame, f"FPS: {fps:.1f}", w - 120, 35, 0.5, active_color)
    
    # Alt Bar (Durum)
    draw_hud_panel(frame, 10, h - 50, w - 20, 40, active_color)
    status_text = f"ACTIVE MODE: {gesture}"
    ts = cv2.getTextSize(status_text, cv2.FONT_HERSHEY_DUPLEX, 0.6, 1)[0]
    draw_text(frame, status_text, (w - ts[0]) // 2, h - 25, 0.6, active_color)
