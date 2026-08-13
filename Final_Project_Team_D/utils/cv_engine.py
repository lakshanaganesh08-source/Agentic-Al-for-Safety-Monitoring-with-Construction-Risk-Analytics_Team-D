from pathlib import Path
from collections import Counter

import cv2
import numpy as np
from PIL import Image
from ultralytics import YOLO


# ============================================================
# MODEL CONFIGURATION
# ============================================================

MODEL_ID = "hf://Hexmon/vyra-yolo-ppe-detection/best.pt"

CONFIDENCE_THRESHOLD = 0.35
IOU_THRESHOLD = 0.50
IMAGE_SIZE = 640


# ============================================================
# LOAD MODEL
# ============================================================

_MODEL = None


def load_model():
    """
    Load the PPE detection YOLO model only once.
    """

    global _MODEL

    if _MODEL is None:
        _MODEL = YOLO(MODEL_ID)

    return _MODEL


# ============================================================
# IMAGE CONVERSION
# ============================================================

def pil_to_bgr(image: Image.Image) -> np.ndarray:
    """
    Convert PIL image to OpenCV BGR format.
    """

    rgb = np.array(image.convert("RGB"))

    return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)


def bgr_to_rgb(image: np.ndarray) -> np.ndarray:
    """
    Convert OpenCV BGR image to RGB.
    """

    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


# ============================================================
# RUN DETECTION
# ============================================================

def analyze_image(image: Image.Image):
    """
    Run actual YOLO PPE detection on the uploaded image.

    Returns:
        annotated_image
        detections
        summary
    """

    model = load_model()

    image_bgr = pil_to_bgr(image)

    results = model.predict(
        source=image_bgr,
        conf=CONFIDENCE_THRESHOLD,
        iou=IOU_THRESHOLD,
        imgsz=IMAGE_SIZE,
        verbose=False,
    )

    result = results[0]

    detections = []

    if result.boxes is not None:

        boxes = result.boxes

        for i in range(len(boxes)):

            class_id = int(boxes.cls[i].item())
            confidence = float(boxes.conf[i].item())

            class_name = result.names[class_id]

            xyxy = boxes.xyxy[i].cpu().numpy().astype(int)

            x1, y1, x2, y2 = xyxy.tolist()

            detections.append(
                {
                    "class": class_name,
                    "confidence": confidence,
                    "bbox": [x1, y1, x2, y2],
                }
            )

    # ========================================================
    # ANNOTATED IMAGE
    # ========================================================

    annotated = result.plot(
        conf=True,
        labels=True,
        boxes=True,
    )

    annotated_rgb = bgr_to_rgb(annotated)

    # ========================================================
    # SUMMARY
    # ========================================================

    summary = build_summary(detections)

    return annotated_rgb, detections, summary


# ============================================================
# BUILD SAFETY SUMMARY
# ============================================================

def build_summary(detections):

    classes = [
        detection["class"].lower()
        for detection in detections
    ]

    counts = Counter(classes)

    # --------------------------------------------------------
    # PEOPLE
    # --------------------------------------------------------

    persons = counts.get("person", 0)

    # --------------------------------------------------------
    # HARDHAT
    # --------------------------------------------------------

    hardhat = (
        counts.get("hardhat", 0)
        + counts.get("hat", 0)
    )

    no_hardhat = (
        counts.get("no-hardhat", 0)
        + counts.get("nohat", 0)
    )

    hardhat_total = hardhat + no_hardhat

    if hardhat_total > 0:
        hardhat_compliance = (
            hardhat / hardhat_total
        ) * 100
    else:
        hardhat_compliance = None

    # --------------------------------------------------------
    # SAFETY VEST
    # --------------------------------------------------------

    vest = counts.get("safety vest", 0) + counts.get("vest", 0)

    no_vest = (
        counts.get("no-safety vest", 0)
        + counts.get("novest", 0)
    )

    vest_total = vest + no_vest

    if vest_total > 0:
        vest_compliance = (
            vest / vest_total
        ) * 100
    else:
        vest_compliance = None

    # --------------------------------------------------------
    # MASK
    # --------------------------------------------------------

    mask = counts.get("mask", 0)

    no_mask = counts.get("no-mask", 0)

    mask_total = mask + no_mask

    if mask_total > 0:
        mask_compliance = (
            mask / mask_total
        ) * 100
    else:
        mask_compliance = None

    # --------------------------------------------------------
    # GLOVES
    # --------------------------------------------------------

    gloves = counts.get("gloves", 0)

    no_gloves = counts.get("no-gloves", 0)

    gloves_total = gloves + no_gloves

    if gloves_total > 0:
        gloves_compliance = (
            gloves / gloves_total
        ) * 100
    else:
        gloves_compliance = None

    # --------------------------------------------------------
    # GOGGLES
    # --------------------------------------------------------

    goggles = counts.get("goggles", 0)

    no_goggles = counts.get("no-goggles", 0)

    goggles_total = goggles + no_goggles

    if goggles_total > 0:
        goggles_compliance = (
            goggles / goggles_total
        ) * 100
    else:
        goggles_compliance = None

    # --------------------------------------------------------
    # HAZARDS
    # --------------------------------------------------------

    fall_detected = (
        counts.get("fall-detected", 0)
        + counts.get("fall detected", 0)
    )

    ladders = counts.get("ladder", 0)

    safety_cones = (
        counts.get("safety cone", 0)
        + counts.get("cone", 0)
    )

    # --------------------------------------------------------
    # PPE VIOLATIONS
    # --------------------------------------------------------

    violations = (
        no_hardhat
        + no_vest
        + no_mask
        + no_gloves
        + no_goggles
    )

    # --------------------------------------------------------
    # OVERALL PPE SCORE
    # --------------------------------------------------------

    compliance_values = []

    for value in [
        hardhat_compliance,
        vest_compliance,
        mask_compliance,
        gloves_compliance,
        goggles_compliance,
    ]:

        if value is not None:
            compliance_values.append(value)

    if compliance_values:

        overall_score = sum(
            compliance_values
        ) / len(compliance_values)

    else:

        overall_score = None

    # --------------------------------------------------------
    # RISK LEVEL
    # --------------------------------------------------------

    critical_hazards = fall_detected

    if critical_hazards > 0:

        risk_level = "CRITICAL"

    elif violations >= 3:

        risk_level = "HIGH"

    elif violations > 0:

        risk_level = "MODERATE"

    else:

        risk_level = "LOW"

    # --------------------------------------------------------
    # RETURN
    # --------------------------------------------------------

    return {
        "persons": persons,

        "hardhat": hardhat,
        "no_hardhat": no_hardhat,
        "hardhat_compliance": hardhat_compliance,

        "vest": vest,
        "no_vest": no_vest,
        "vest_compliance": vest_compliance,

        "mask": mask,
        "no_mask": no_mask,
        "mask_compliance": mask_compliance,

        "gloves": gloves,
        "no_gloves": no_gloves,
        "gloves_compliance": gloves_compliance,

        "goggles": goggles,
        "no_goggles": no_goggles,
        "goggles_compliance": goggles_compliance,

        "fall_detected": fall_detected,
        "ladders": ladders,
        "safety_cones": safety_cones,

        "violations": violations,

        "overall_score": overall_score,

        "risk_level": risk_level,

        "detection_counts": dict(counts),
    }