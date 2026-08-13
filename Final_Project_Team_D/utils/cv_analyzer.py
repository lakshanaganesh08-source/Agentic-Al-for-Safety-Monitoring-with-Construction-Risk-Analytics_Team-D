"""
Computer Vision analysis for construction site images.

Detection pipeline:
1. YOLO11n detects actual personnel.
2. Hexmon PPE YOLO model detects PPE and construction hazards.
3. PPE detections are matched to detected personnel using bounding boxes.
4. PPE compliance is calculated from actual detected workers.
5. Results are annotated on the uploaded image.

Supported PPE / hazard classes from the Hexmon model:
- Fall-Detected
- Gloves
- Goggles
- Hardhat
- Ladder
- Mask
- NO-Gloves
- NO-Goggles
- NO-Hardhat
- NO-Mask
- NO-Safety Vest
- Person
- Safety Cone
- Safety Vest
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np


# =========================================================
# DATA CLASSES
# =========================================================

@dataclass
class CVFinding:
    title: str
    severity: str  # pass, warning, danger
    message: str
    score: float = 0.0


@dataclass
class CVAnalysisResult:
    hardhat_compliance_pct: float
    vest_compliance_pct: float
    overall_score: float
    status: str
    status_color: str
    estimated_personnel: int
    findings: list[CVFinding] = field(default_factory=list)
    annotated_image: np.ndarray | None = None

    # Extra information for future UI/reporting
    gloves_compliance_pct: float = 0.0
    goggles_compliance_pct: float = 0.0
    mask_compliance_pct: float = 0.0
    fall_detected: int = 0
    ladders_detected: int = 0
    safety_cones_detected: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "hardhat_compliance_pct": self.hardhat_compliance_pct,
            "vest_compliance_pct": self.vest_compliance_pct,
            "gloves_compliance_pct": self.gloves_compliance_pct,
            "goggles_compliance_pct": self.goggles_compliance_pct,
            "mask_compliance_pct": self.mask_compliance_pct,
            "overall_score": self.overall_score,
            "status": self.status,
            "estimated_personnel": self.estimated_personnel,
            "fall_detected": self.fall_detected,
            "ladders_detected": self.ladders_detected,
            "safety_cones_detected": self.safety_cones_detected,
            "findings": [
                {
                    "title": f.title,
                    "severity": f.severity,
                    "message": f.message,
                    "score": f.score,
                }
                for f in self.findings
            ],
        }


# =========================================================
# MODEL LOADING
# =========================================================

_PERSON_MODEL = None
_PPE_MODEL = None


def _require_cv_dependencies():
    """
    Import computer vision dependencies lazily so the application
    can still start if CV dependencies are unavailable.
    """
    try:
        import cv2
    except ImportError as exc:
        raise ImportError(
            "OpenCV is required. Install with: "
            "pip install opencv-python-headless"
        ) from exc

    try:
        from ultralytics import YOLO
    except ImportError as exc:
        raise ImportError(
            "Ultralytics is required. Install with: "
            "pip install ultralytics"
        ) from exc

    try:
        from huggingface_hub import hf_hub_download
    except ImportError as exc:
        raise ImportError(
            "huggingface_hub is required. Install with: "
            "pip install huggingface_hub"
        ) from exc

    return cv2, YOLO, hf_hub_download


def _load_person_model():
    """
    Load the general YOLO11n model.

    This model is responsible ONLY for detecting people.
    """
    global _PERSON_MODEL

    if _PERSON_MODEL is None:
        _, YOLO, _ = _require_cv_dependencies()

        print("Loading YOLO11n person detection model...")
        _PERSON_MODEL = YOLO("yolo11n.pt")

    return _PERSON_MODEL


def _load_ppe_model():
    """
    Load the Hexmon PPE detection model from Hugging Face.

    The model is cached locally after the first download.
    """
    global _PPE_MODEL

    if _PPE_MODEL is None:
        _, YOLO, hf_hub_download = _require_cv_dependencies()

        print("Loading construction PPE detection model...")

        model_path = hf_hub_download(
            repo_id="Hexmon/vyra-yolo-ppe-detection",
            filename="best.pt",
        )

        _PPE_MODEL = YOLO(model_path)

    return _PPE_MODEL


# =========================================================
# IMAGE CONVERSION
# =========================================================

def _pil_to_bgr(image) -> np.ndarray:
    """Convert PIL Image to OpenCV BGR ndarray."""
    cv2, _, _ = _require_cv_dependencies()

    rgb = np.array(image.convert("RGB"))

    return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)


def bgr_to_rgb(bgr: np.ndarray) -> np.ndarray:
    """Convert OpenCV BGR image to RGB."""
    cv2, _, _ = _require_cv_dependencies()

    return cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)


# =========================================================
# GEOMETRY HELPERS
# =========================================================

def _box_center(box):
    """Return center point of [x1, y1, x2, y2]."""
    x1, y1, x2, y2 = box

    return (
        (x1 + x2) / 2,
        (y1 + y2) / 2,
    )


def _point_inside_box(point, box, margin=0):
    """Check whether a point lies inside a bounding box."""
    px, py = point
    x1, y1, x2, y2 = box

    return (
        px >= x1 - margin
        and px <= x2 + margin
        and py >= y1 - margin
        and py <= y2 + margin
    )


def _box_iou(box_a, box_b):
    """Calculate Intersection over Union."""
    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b

    inter_x1 = max(ax1, bx1)
    inter_y1 = max(ay1, by1)
    inter_x2 = min(ax2, bx2)
    inter_y2 = min(ay2, by2)

    inter_w = max(0, inter_x2 - inter_x1)
    inter_h = max(0, inter_y2 - inter_y1)

    intersection = inter_w * inter_h

    area_a = max(0, ax2 - ax1) * max(0, ay2 - ay1)
    area_b = max(0, bx2 - bx1) * max(0, by2 - by1)

    union = area_a + area_b - intersection

    if union <= 0:
        return 0.0

    return intersection / union


def _match_detection_to_person(
    detection_box,
    person_boxes,
):
    """
    Match a PPE detection to the most likely person.

    Primary method:
        detection center inside person box.

    Secondary method:
        highest IoU.
    """

    center = _box_center(detection_box)

    # -----------------------------------------------------
    # First: center point containment
    # -----------------------------------------------------

    candidates = []

    for index, person_box in enumerate(person_boxes):
        if _point_inside_box(center, person_box):
            candidates.append(index)

    if candidates:
        # If multiple people contain the point, choose
        # the person with the highest IoU.
        return max(
            candidates,
            key=lambda i: _box_iou(detection_box, person_boxes[i]),
        )

    # -----------------------------------------------------
    # Second: IoU fallback
    # -----------------------------------------------------

    best_index = None
    best_iou = 0.0

    for index, person_box in enumerate(person_boxes):
        iou = _box_iou(detection_box, person_box)

        if iou > best_iou:
            best_iou = iou
            best_index = index

    # Require a small amount of overlap.
    if best_index is not None and best_iou >= 0.01:
        return best_index

    return None


# =========================================================
# YOLO DETECTION
# =========================================================

def _run_person_detection(bgr):
    """
    Detect actual people using YOLO11n.
    """

    model = _load_person_model()

    results = model.predict(
        source=bgr,
        conf=0.25,
        iou=0.45,
        verbose=False,
    )

    person_boxes = []
    person_confidences = []

    if not results:
        return person_boxes, person_confidences

    result = results[0]

    if result.boxes is None:
        return person_boxes, person_confidences

    names = result.names

    for box in result.boxes:
        cls_id = int(box.cls[0])
        confidence = float(box.conf[0])

        class_name = str(names.get(cls_id, "")).lower()

        if class_name == "person":

            coordinates = box.xyxy[0].cpu().numpy().tolist()

            person_boxes.append(coordinates)
            person_confidences.append(confidence)

    return person_boxes, person_confidences


def _run_ppe_detection(bgr):
    """
    Detect PPE and construction hazards using the Hexmon model.
    """

    model = _load_ppe_model()

    results = model.predict(
        source=bgr,
        conf=0.20,
        iou=0.45,
        verbose=False,
    )

    detections = []

    if not results:
        return detections

    result = results[0]

    if result.boxes is None:
        return detections

    names = result.names

    for box in result.boxes:

        cls_id = int(box.cls[0])
        confidence = float(box.conf[0])

        class_name = str(
            names.get(cls_id, "")
        )

        coordinates = (
            box.xyxy[0]
            .cpu()
            .numpy()
            .tolist()
        )

        detections.append(
            {
                "class": class_name,
                "confidence": confidence,
                "box": coordinates,
            }
        )

    return detections


# =========================================================
# ANNOTATION
# =========================================================

def _draw_annotations(
    bgr,
    person_boxes,
    person_status,
    ppe_detections,
):
    """
    Draw workers and PPE detections on the image.
    """

    cv2, _, _ = _require_cv_dependencies()

    annotated = bgr.copy()

    # -----------------------------------------------------
    # Draw person boxes
    # -----------------------------------------------------

    for index, person_box in enumerate(person_boxes):

        x1, y1, x2, y2 = map(int, person_box)

        status = person_status.get(
            index,
            {
                "hardhat": False,
                "vest": False,
            },
        )

        hardhat_ok = status.get("hardhat", False)
        vest_ok = status.get("vest", False)

        if hardhat_ok and vest_ok:
            color = (0, 230, 118)  # green
            label = f"Worker {index + 1} - COMPLIANT"

        elif hardhat_ok or vest_ok:
            color = (0, 171, 255)  # orange
            label = f"Worker {index + 1} - PARTIAL"

        else:
            color = (82, 82, 255)  # red
            label = f"Worker {index + 1} - ACTION REQUIRED"

        cv2.rectangle(
            annotated,
            (x1, y1),
            (x2, y2),
            color,
            3,
        )

        label_y = max(25, y1 - 8)

        cv2.putText(
            annotated,
            label,
            (x1, label_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            color,
            2,
            cv2.LINE_AA,
        )

    # -----------------------------------------------------
    # Draw PPE / hazard boxes
    # -----------------------------------------------------

    for detection in ppe_detections:

        class_name = detection["class"]
        confidence = detection["confidence"]
        box = detection["box"]

        x1, y1, x2, y2 = map(int, box)

        normalized = class_name.lower()

        # Positive PPE
        if normalized in {
            "hardhat",
            "safety vest",
            "gloves",
            "goggles",
            "mask",
        }:
            color = (0, 230, 118)

        # Negative PPE
        elif normalized.startswith("no-"):
            color = (82, 82, 255)

        # Hazards
        elif normalized in {
            "fall-detected",
            "ladder",
        }:
            color = (0, 165, 255)

        else:
            color = (255, 200, 0)

        cv2.rectangle(
            annotated,
            (x1, y1),
            (x2, y2),
            color,
            2,
        )

        label = f"{class_name} {confidence:.2f}"

        text_y = max(20, y1 - 5)

        cv2.putText(
            annotated,
            label,
            (x1, text_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            color,
            2,
            cv2.LINE_AA,
        )

    return annotated


def _draw_summary(
    image,
    overall_score,
    personnel,
    status,
):
    """
    Add a readable summary panel to the annotated image.
    """

    cv2, _, _ = _require_cv_dependencies()

    height, width = image.shape[:2]

    panel_height = 125

    panel = image.copy()

    # Dark transparent panel
    overlay = panel.copy()

    cv2.rectangle(
        overlay,
        (0, 0),
        (width, panel_height),
        (10, 15, 25),
        -1,
    )

    cv2.addWeighted(
        overlay,
        0.82,
        panel,
        0.18,
        0,
        panel,
    )

    # Score
    cv2.putText(
        panel,
        f"PPE Score: {overall_score:.1f}%",
        (20, 38),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (0, 229, 255),
        3,
        cv2.LINE_AA,
    )

    # Personnel
    cv2.putText(
        panel,
        f"Personnel detected: {personnel}",
        (20, 72),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (240, 246, 252),
        2,
        cv2.LINE_AA,
    )

    # Status
    if status == "COMPLIANT":
        status_color = (0, 230, 118)
    elif status == "MINOR ISSUES":
        status_color = (0, 171, 255)
    else:
        status_color = (82, 82, 255)

    cv2.putText(
        panel,
        f"Status: {status}",
        (20, 106),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        status_color,
        2,
        cv2.LINE_AA,
    )

    return panel


# =========================================================
# MAIN ANALYSIS
# =========================================================

def analyze_site_image(image) -> CVAnalysisResult:
    """
    Analyze a construction site image.

    Uses:
        YOLO11n -> personnel detection
        Hexmon -> PPE and hazard detection

    Args:
        image:
            PIL Image or numpy BGR image.

    Returns:
        CVAnalysisResult
    """

    # -----------------------------------------------------
    # Convert input
    # -----------------------------------------------------

    if not hasattr(image, "shape"):
        bgr = _pil_to_bgr(image)
    else:
        bgr = image.copy()

    # -----------------------------------------------------
    # Run PERSON detector
    # -----------------------------------------------------

    person_boxes, person_confidences = _run_person_detection(bgr)

    personnel = len(person_boxes)

    # -----------------------------------------------------
    # Run PPE detector
    # -----------------------------------------------------

    ppe_detections = _run_ppe_detection(bgr)

    # -----------------------------------------------------
    # Detection counters
    # -----------------------------------------------------

    positive_counts = {
        "Hardhat": 0,
        "Safety Vest": 0,
        "Gloves": 0,
        "Goggles": 0,
        "Mask": 0,
    }

    negative_counts = {
        "NO-Hardhat": 0,
        "NO-Safety Vest": 0,
        "NO-Gloves": 0,
        "NO-Goggles": 0,
        "NO-Mask": 0,
    }

    fall_count = 0
    ladder_count = 0
    cone_count = 0

    # Each worker gets a PPE status.
    person_status = {}

    for index in range(personnel):
        person_status[index] = {
            "hardhat": False,
            "vest": False,
            "gloves": False,
            "goggles": False,
            "mask": False,
        }

    # -----------------------------------------------------
    # Match PPE detections to workers
    # -----------------------------------------------------

    for detection in ppe_detections:

        class_name = detection["class"]
        normalized = class_name.lower()

        # ---------------------------------------------
        # Positive PPE
        # ---------------------------------------------

        if class_name in positive_counts:
            positive_counts[class_name] += 1

            if personnel > 0:

                person_index = _match_detection_to_person(
                    detection["box"],
                    person_boxes,
                )

                if person_index is not None:

                    if class_name == "Hardhat":
                        person_status[person_index]["hardhat"] = True

                    elif class_name == "Safety Vest":
                        person_status[person_index]["vest"] = True

                    elif class_name == "Gloves":
                        person_status[person_index]["gloves"] = True

                    elif class_name == "Goggles":
                        person_status[person_index]["goggles"] = True

                    elif class_name == "Mask":
                        person_status[person_index]["mask"] = True

        # ---------------------------------------------
        # Negative PPE
        # ---------------------------------------------

        elif class_name in negative_counts:
            negative_counts[class_name] += 1

            if personnel > 0:

                person_index = _match_detection_to_person(
                    detection["box"],
                    person_boxes,
                )

                if person_index is not None:

                    if class_name == "NO-Hardhat":
                        person_status[person_index]["hardhat"] = False

                    elif class_name == "NO-Safety Vest":
                        person_status[person_index]["vest"] = False

                    elif class_name == "NO-Gloves":
                        person_status[person_index]["gloves"] = False

                    elif class_name == "NO-Goggles":
                        person_status[person_index]["goggles"] = False

                    elif class_name == "NO-Mask":
                        person_status[person_index]["mask"] = False

        # ---------------------------------------------
        # Construction hazards
        # ---------------------------------------------

        elif normalized == "fall-detected":
            fall_count += 1

        elif normalized == "ladder":
            ladder_count += 1

        elif normalized == "safety cone":
            cone_count += 1

    # =====================================================
    # COMPLIANCE CALCULATIONS
    # =====================================================

    if personnel == 0:

        hardhat_pct = 0.0
        vest_pct = 0.0
        gloves_pct = 0.0
        goggles_pct = 0.0
        mask_pct = 0.0

    else:

        hardhat_ok = sum(
            1
            for status in person_status.values()
            if status["hardhat"]
        )

        vest_ok = sum(
            1
            for status in person_status.values()
            if status["vest"]
        )

        gloves_ok = sum(
            1
            for status in person_status.values()
            if status["gloves"]
        )

        goggles_ok = sum(
            1
            for status in person_status.values()
            if status["goggles"]
        )

        mask_ok = sum(
            1
            for status in person_status.values()
            if status["mask"]
        )

        hardhat_pct = (hardhat_ok / personnel) * 100
        vest_pct = (vest_ok / personnel) * 100
        gloves_pct = (gloves_ok / personnel) * 100
        goggles_pct = (goggles_ok / personnel) * 100
        mask_pct = (mask_ok / personnel) * 100

    # -----------------------------------------------------
    # Overall score
    #
    # Primary construction PPE:
    #   Hardhat = 50%
    #   Safety Vest = 50%
    #
    # Additional hazards are penalties.
    # -----------------------------------------------------

    if personnel == 0:
        overall = 0.0

    else:
        overall = (
            hardhat_pct * 0.50
            + vest_pct * 0.50
        )

        # Falls are serious hazards.
        if fall_count > 0:
            overall -= min(30, fall_count * 15)

        # Explicit PPE violations.
        violation_count = (
            negative_counts["NO-Hardhat"]
            + negative_counts["NO-Safety Vest"]
        )

        overall -= min(
            20,
            violation_count * 5,
        )

        overall = float(
            np.clip(overall, 0, 100)
        )

    # =====================================================
    # STATUS
    # =====================================================

    if personnel == 0:

        status = "NO PERSONNEL DETECTED"
        status_color = "#FFAB00"

    elif overall >= 90 and fall_count == 0:

        status = "COMPLIANT"
        status_color = "#00E676"

    elif overall >= 75:

        status = "MINOR ISSUES"
        status_color = "#FFAB00"

    else:

        status = "ACTION REQUIRED"
        status_color = "#FF5252"

    # =====================================================
    # FINDINGS
    # =====================================================

    findings: list[CVFinding] = []

    # -----------------------------------------------------
    # Personnel
    # -----------------------------------------------------

    if personnel > 0:

        findings.append(
            CVFinding(
                title="Personnel Detection",
                severity="pass",
                message=(
                    f"{personnel} worker(s) detected by YOLO11n "
                    f"with average detection confidence of "
                    f"{np.mean(person_confidences) * 100:.1f}%."
                ),
                score=np.mean(person_confidences) * 100,
            )
        )

    else:

        findings.append(
            CVFinding(
                title="Personnel Detection",
                severity="warning",
                message=(
                    "No personnel were detected by the person "
                    "detection model. PPE compliance cannot "
                    "be reliably evaluated."
                ),
                score=0,
            )
        )

    # -----------------------------------------------------
    # Hardhat
    # -----------------------------------------------------

    if personnel > 0:

        if hardhat_pct >= 90:

            severity = "pass"

        elif hardhat_pct >= 75:

            severity = "warning"

        else:

            severity = "danger"

        findings.append(
            CVFinding(
                title="Hardhat Verification",
                severity=severity,
                message=(
                    f"{sum(1 for s in person_status.values() if s['hardhat'])} "
                    f"of {personnel} detected workers appear to be "
                    f"wearing hardhats. "
                    f"Hardhat compliance: {hardhat_pct:.1f}%."
                ),
                score=hardhat_pct,
            )
        )

    # -----------------------------------------------------
    # Safety Vest
    # -----------------------------------------------------

    if personnel > 0:

        if vest_pct >= 90:

            severity = "pass"

        elif vest_pct >= 75:

            severity = "warning"

        else:

            severity = "danger"

        findings.append(
            CVFinding(
                title="High-Visibility Gear",
                severity=severity,
                message=(
                    f"{sum(1 for s in person_status.values() if s['vest'])} "
                    f"of {personnel} detected workers appear to be "
                    f"wearing safety vests. "
                    f"Safety vest compliance: {vest_pct:.1f}%."
                ),
                score=vest_pct,
            )
        )

    # -----------------------------------------------------
    # Explicit violations
    # -----------------------------------------------------

    if negative_counts["NO-Hardhat"] > 0:

        findings.append(
            CVFinding(
                title="Hardhat Violation",
                severity="danger",
                message=(
                    f"{negative_counts['NO-Hardhat']} "
                    "personnel/object region(s) were explicitly "
                    "detected without a hardhat."
                ),
                score=0,
            )
        )

    if negative_counts["NO-Safety Vest"] > 0:

        findings.append(
            CVFinding(
                title="Safety Vest Violation",
                severity="danger",
                message=(
                    f"{negative_counts['NO-Safety Vest']} "
                    "personnel/object region(s) were explicitly "
                    "detected without a safety vest."
                ),
                score=0,
            )
        )

    # -----------------------------------------------------
    # Fall detection
    # -----------------------------------------------------

    if fall_count > 0:

        findings.append(
            CVFinding(
                title="Fall Detection",
                severity="danger",
                message=(
                    f"{fall_count} potential fall event(s) "
                    "were detected in the uploaded image."
                ),
                score=0,
            )
        )

    else:

        findings.append(
            CVFinding(
                title="Fall Detection",
                severity="pass",
                message="No fall event was detected in the uploaded image.",
                score=100,
            )
        )

    # -----------------------------------------------------
    # Ladder
    # -----------------------------------------------------

    if ladder_count > 0:

        findings.append(
            CVFinding(
                title="Ladder Detection",
                severity="warning",
                message=(
                    f"{ladder_count} ladder detection(s) "
                    "were found. Verify safe positioning and usage."
                ),
                score=0,
            )
        )

    # -----------------------------------------------------
    # Safety cones
    # -----------------------------------------------------

    if cone_count > 0:

        findings.append(
            CVFinding(
                title="Safety Cone Detection",
                severity="pass",
                message=(
                    f"{cone_count} safety cone(s) detected "
                    "in the inspected image."
                ),
                score=100,
            )
        )

    # =====================================================
    # DRAW ANNOTATED IMAGE
    # =====================================================

    annotated = _draw_annotations(
        bgr=bgr,
        person_boxes=person_boxes,
        person_status=person_status,
        ppe_detections=ppe_detections,
    )

    annotated = _draw_summary(
        image=annotated,
        overall_score=overall,
        personnel=personnel,
        status=status,
    )

    # =====================================================
    # RETURN RESULT
    # =====================================================

    return CVAnalysisResult(
        hardhat_compliance_pct=round(hardhat_pct, 1),
        vest_compliance_pct=round(vest_pct, 1),
        overall_score=round(overall, 1),
        status=status,
        status_color=status_color,
        estimated_personnel=personnel,
        findings=findings,
        annotated_image=annotated,

        gloves_compliance_pct=round(gloves_pct, 1),
        goggles_compliance_pct=round(goggles_pct, 1),
        mask_compliance_pct=round(mask_pct, 1),

        fall_detected=fall_count,
        ladders_detected=ladder_count,
        safety_cones_detected=cone_count,
    )