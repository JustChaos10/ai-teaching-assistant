import argparse
import csv
import json
import os
import signal
import sys
import time
from datetime import datetime
from argparse import Namespace

import cv2
import mediapipe as mp

def run(args=None):
    """
    Runs the head-center checking logic.
    If 'args' is None, it runs with a set of default values.
    """
    if args is None:
        print("INFO: No arguments provided. Running with default settings.")
        args = Namespace(
            check_interval_sec=5,
            duration_sec=0,
            report_prefix="",
            out_dir="sessions",
            show_preview=True
        )

    if os.name == "nt":
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    else:
        cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("ERROR: Cannot open webcam")
        return 1
    cap.set(cv2.CAP_PROP_FPS, 30)

    mp_face = mp.solutions.face_detection
    face_det = mp_face.FaceDetection(model_selection=0, min_detection_confidence=0.5)

    total_takes = 0
    head_counts = 0
    checks_log = []

    check_interval = max(1, int(args.check_interval_sec))
    next_check_time = time.time() + check_interval
    start_time = time.time()

    out_dir = args.out_dir or "sessions"
    os.makedirs(out_dir, exist_ok=True)

    stop_flag = {"stop": False}
    def on_sigint(sig, frame):
        stop_flag["stop"] = True
    signal.signal(signal.SIGINT, on_sigint)

    window_name = "Head Center Checks (press q to quit)"
    if args.show_preview:
        try:
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        except Exception:
            pass

    print(f"Head-center checks every {check_interval}s. Press Ctrl+C or 'q' to stop.")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                time.sleep(0.02)
                continue

            h, w, _ = frame.shape
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            res = face_det.process(rgb)

            box_w = int(w * (2.0 / 3.0))
            box_h = int(h * (2.0 / 3.0))
            x1 = (w - box_w) // 2
            y1 = (h - box_h) // 2
            x2 = x1 + box_w
            y2 = y1 + box_h

            head_in_box = 0
            face_cx, face_cy = None, None

            if res.detections:
                det = res.detections[0]
                bbox = det.location_data.relative_bounding_box
                fx = max(0, min(1, bbox.xmin))
                fy = max(0, min(1, bbox.ymin))
                fw = max(0, min(1, bbox.width))
                fh = max(0, min(1, bbox.height))

                rx1 = int(fx * w)
                ry1 = int(fy * h)
                rx2 = int((fx + fw) * w)
                ry2 = int((fy + fh) * h)

                face_cx = (rx1 + rx2) // 2
                face_cy = (ry1 + ry2) // 2

                if x1 <= face_cx <= x2 and y1 <= face_cy <= y2:
                    head_in_box = 1

            now = time.time()
            if now >= next_check_time:
                total_takes += 1
                head_counts += head_in_box
                checks_log.append({
                    "timestamp": datetime.now().isoformat(timespec="seconds"),
                    "face_detected": int(res.detections is not None and len(res.detections) > 0),
                    "face_cx": face_cx if face_cx is not None else -1,
                    "face_cy": face_cy if face_cy is not None else -1,
                    "head_in_box": head_in_box
                })
                print(f"[Check {total_takes}] head_in_box={head_in_box}  counts={head_counts}/{total_takes}")
                next_check_time = now + check_interval

            if args.show_preview:
                overlay = frame.copy()
                cv2.rectangle(overlay, (x1, y1), (x2, y2), (60, 200, 255), 2)
                if res.detections:
                    bbox = res.detections[0].location_data.relative_bounding_box
                    rx1 = int(max(0, min(1, bbox.xmin)) * w)
                    ry1 = int(max(0, min(1, bbox.ymin)) * h)
                    rx2 = int(max(0, min(1, bbox.xmin + bbox.width)) * w)
                    ry2 = int(max(0, min(1, bbox.ymin + bbox.height)) * h)
                    cv2.rectangle(overlay, (rx1, ry1), (rx2, ry2), (0, 255, 0), 1)
                    if face_cx is not None and face_cy is not None:
                        cv2.circle(overlay, (face_cx, face_cy), 4, (0, 255, 255), -1)

                pct = 0.0 if total_takes == 0 else (100.0 * head_counts / total_takes)
                status = f"in_box={head_in_box}  counts={head_counts}/{total_takes}  {pct:.1f}%"
                color = (0, 200, 0) if head_in_box else (0, 0, 255)
                cv2.putText(overlay, status, (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

                cv2.imshow(window_name, overlay)
                if cv2.waitKey(10) & 0xFF == ord('q'):
                    stop_flag["stop"] = True

            if stop_flag["stop"]:
                break
            if args.duration_sec > 0 and (now - start_time) >= args.duration_sec:
                break

            time.sleep(0.005)
    finally:
        cap.release()
        try:
            cv2.destroyAllWindows()
        except Exception:
            pass
        face_det.close()

    # --- FINAL REPORT (Changes are here) ---
    attention_percent = 0.0 if total_takes == 0 else round(100.0 * head_counts / total_takes, 1)
    print("\nSession ended.")
    print(f"Head-in-box checks: {head_counts}/{total_takes} -> {attention_percent}%")

    # **MODIFIED**: Use a friendlier timestamp for the filename (e.g., 2025-08-17_02-01PM)
    prefix = args.report_prefix or datetime.now().strftime("Attendance_%Y-%m-%d_%I-%M%p")
    json_path = os.path.join(out_dir, f"{prefix}.json")

    # **REMOVED**: The CSV file writing block is now gone.

    # JSON report
    summary = {
        "checks_total": total_takes,
        "checks_head_in_box": head_counts,
        "attention_percent": attention_percent,
        "check_interval_sec": check_interval,
        "started_at": datetime.fromtimestamp(start_time).isoformat(timespec="seconds"),
        "ended_at": datetime.now().isoformat(timespec="seconds"),
        "central_box_fraction": {"width": "2/3", "height": "2/3"},
        "output_dir": os.path.abspath(out_dir),
        "report_prefix": prefix,
        "log": checks_log # Storing the detailed log inside the JSON
    }
    with open(json_path, "w") as jf:
        json.dump(summary, jf, indent=2)

    # **MODIFIED**: The final print statement only shows the JSON path.
    print(f"Saved report: {json_path}")
    return 0

def parse_args():
    ap = argparse.ArgumentParser(description="Head-in-Center Checks using MediaPipe Face Detection")
    ap.add_argument("--check_interval_sec", type=int, default=5, help="Interval between checks (seconds)")
    ap.add_argument("--duration_sec", type=int, default=0, help="Run duration (0 = until Ctrl+C)")
    ap.add_argument("--report_prefix", type=str, default="", help="Prefix for JSON output")
    ap.add_argument("--out_dir", type=str, default="sessions", help="Directory to save JSON report")
    ap.add_argument("--show_preview", action="store_true", help="Show live preview with central box")
    return ap.parse_args()

if __name__ == "__main__":
    try:
        sys.exit(run(parse_args()))
    except KeyboardInterrupt:
        sys.exit(0)