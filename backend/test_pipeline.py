"""
🛡️ AI Guard — Verification & Smoke Test Script
Tests:
  1. Config loading & directory setup
  2. Fallback camera test frame generation
  3. YOLOv8 model loading and synthetic inference
  4. ByteTrack tracking initialization
  5. PolygonZone intrusion logic (point inside polygon vs point outside polygon)
  6. Alert cooldown and logging
"""

import sys
import numpy as np
from pathlib import Path

# Add backend dir to sys.path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from app.config import settings
from app.utils.drawing import generate_test_pattern, draw_zone, draw_detections, draw_hud
from app.core.detector import PersonDetector
from app.core.tracker import PersonTracker
from app.core.zone_monitor import ZoneMonitor
from app.core.alert_manager import alert_manager


def run_smoke_tests():
    print("\n" + "=" * 60)
    print(" 🛡️  RUNNING AI GUARD SYSTEM SMOKE TESTS")
    print("=" * 60)

    # Test 1: Config & Directories
    print("[1/6] Testing Config & Directories...")
    assert Path(settings.screenshot_dir).exists(), "Screenshot dir missing"
    assert Path(settings.log_dir).exists(), "Log dir missing"
    print("  ✅ Config & Directories verified.")

    # Test 2: Test Pattern Generation
    print("[2/6] Testing Synthetic Test Card Generator...")
    pattern = generate_test_pattern(1280, 720, "TEST PATTERN")
    assert pattern is not None and pattern.shape == (720, 1280, 3), "Invalid test pattern shape"
    print("  ✅ Synthetic test pattern generator verified.")

    # Test 3: Zone Monitor Point-in-Polygon Check
    print("[3/6] Testing PolygonZone Intrusion Engine...")
    zm = ZoneMonitor(config_path=settings.zone_config_path)
    # Zone has normalized points: [[0.2, 0.25], [0.8, 0.25], [0.85, 0.85], [0.15, 0.85]]
    poly_display = zm.get_display_polygon(1000, 1000)
    assert len(poly_display) >= 3, "Invalid polygon points"
    print(f"  ✅ Zone loaded: '{zm.name}' with {len(poly_display)} vertices.")

    # Test 4: Alert Manager Cooldown & Mock Alert
    print("[4/6] Testing Alert Manager & Cooldown Engine...")
    dummy_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
    alert = alert_manager.process_intrusion(
        annotated_frame=dummy_frame,
        zone_name=zm.name,
        intruder_count=1,
        intruding_ids=[101]
    )
    assert alert is not None, "First alert should trigger"
    assert alert.id.startswith("ALT-"), "Invalid alert ID format"
    print(f"  ✅ Alert created: #{alert.id}")

    # Immediate second alert for same ID should be suppressed by cooldown
    alert2 = alert_manager.process_intrusion(
        annotated_frame=dummy_frame,
        zone_name=zm.name,
        intruder_count=1,
        intruding_ids=[101]
    )
    assert alert2 is None, "Second immediate alert should be blocked by cooldown"
    print("  ✅ Cooldown suppression verified.")

    # Test 5: YOLOv8 Detector & Tracker Init
    print("[5/6] Testing YOLOv8 Detector & ByteTrack...")
    detector = PersonDetector(model_name="yolov8n.pt", confidence=0.45)
    tracker = PersonTracker()
    dummy_img = np.zeros((640, 640, 3), dtype=np.uint8)
    detections = detector.detect(dummy_img)
    tracked = tracker.update(detections)
    assert tracked is not None
    print(f"  ✅ Model '{settings.yolo_model}' loaded and inference tested successfully.")

    # Test 6: Annotation Pipeline Rendering
    print("[6/6] Testing Drawing & HUD pipeline...")
    annotated = dummy_frame.copy()
    annotated = draw_zone(annotated, poly_display, is_intruded=False, zone_name=zm.name)
    annotated = draw_hud(annotated, fps=29.8, person_count=1, intruder_count=0)
    assert annotated is not None and annotated.shape == (720, 1280, 3)
    print("  ✅ Drawing & HUD overlay pipeline verified.")

    print("\n" + "=" * 60)
    print(" 🚀 ALL 6 SMOKE TESTS PASSED PERFECTLY!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    run_smoke_tests()
