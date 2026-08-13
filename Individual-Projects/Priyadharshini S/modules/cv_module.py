import cv2
import numpy as np
import plotly.graph_objects as go
import streamlit as st
from PIL import Image

from utils.styling import hero, section_label

AMBER = "#F59E0B"
TEXT = "#E7ECF5"


def _to_cv(img: Image.Image):
    arr = np.array(img.convert("RGB"))
    return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)


def _ppe_hivis_mask(bgr):
    """Detect high-visibility PPE (orange / yellow-green vests & helmets) via HSV color masking."""
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    orange_lo, orange_hi = np.array([5, 120, 120]), np.array([25, 255, 255])
    yellow_lo, yellow_hi = np.array([25, 100, 120]), np.array([45, 255, 255])
    mask_o = cv2.inRange(hsv, orange_lo, orange_hi)
    mask_y = cv2.inRange(hsv, yellow_lo, yellow_hi)
    mask = cv2.bitwise_or(mask_o, mask_y)
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    coverage = mask.sum() / 255 / (mask.shape[0] * mask.shape[1])
    return mask, coverage


def _helmet_like_blobs(mask):
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    blobs = [c for c in contours if cv2.contourArea(c) > 150]
    return blobs


def _edge_crack_analysis(bgr):
    """Canny edge detection + contour density as a proxy for structural crack / defect indicators."""
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(gray, 60, 160)
    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    long_thin = [c for c in contours if cv2.arcLength(c, False) > 60 and cv2.contourArea(c) < 400]
    density = edges.sum() / 255 / (edges.shape[0] * edges.shape[1])
    return edges, density, len(long_thin)


def _blur_score(bgr):
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    return cv2.Laplacian(gray, cv2.CV_64F).var()


def render():
    hero(
        "Computer Vision — Site Safety Scanner",
        "Upload a construction site photograph. OpenCV-based image processing estimates "
        "PPE (high-visibility gear) coverage, surface crack indicators, and image quality.",
        badge="COMPUTER VISION",
    )

    st.markdown(
        "This module applies classical computer vision techniques — **HSV color "
        "segmentation** for high-visibility PPE detection, **Canny edge detection** for "
        "structural crack indicators, and the **Laplacian variance** method for blur / "
        "image quality assessment."
    )

    uploaded = st.file_uploader("Upload site photo (JPG / PNG)", type=["jpg", "jpeg", "png"])

    demo_col1, demo_col2 = st.columns([1, 3])
    with demo_col1:
        use_demo = st.button("🖼️ Use synthetic demo image")

    img = None
    if uploaded is not None:
        img = Image.open(uploaded)
    elif use_demo:
        img = _make_synthetic_site_image()

    if img is None:
        st.info("Upload an image, or click **Use synthetic demo image** to try the scanner instantly.")
        return

    bgr = _to_cv(img)
    mask, coverage = _ppe_hivis_mask(bgr)
    blobs = _helmet_like_blobs(mask)
    edges, crack_density, crack_segments = _edge_crack_analysis(bgr)
    blur = _blur_score(bgr)

    st.write("")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.image(img, caption="Original Image", use_container_width=True)
    with c2:
        st.image(mask, caption=f"PPE High-Vis Mask ({coverage*100:.1f}% coverage)",
                  use_container_width=True, clamp=True)
    with c3:
        st.image(edges, caption=f"Edge / Crack Map ({crack_segments} segments)",
                  use_container_width=True, clamp=True)

    st.write("")
    section_label("AI SCAN RESULTS")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("PPE Coverage", f"{coverage*100:.1f}%")
    m2.metric("Detected Hi-Vis Blobs", len(blobs))
    m3.metric("Crack Risk Segments", crack_segments)
    m4.metric("Image Sharpness", f"{blur:.0f}", "Blurry" if blur < 100 else "Clear",
              delta_color="inverse" if blur < 100 else "normal")

    st.write("")
    ppe_compliance_score = min(100, coverage * 400 + len(blobs) * 6)
    crack_risk_score = min(100, crack_segments * 1.6 + crack_density * 120)

    g1, g2 = st.columns(2)
    with g1:
        fig = go.Figure(go.Indicator(
            mode="gauge+number", value=ppe_compliance_score,
            title={"text": "Estimated PPE Compliance Score", "font": {"color": TEXT, "size": 14}},
            number={"suffix": "%", "font": {"color": TEXT}},
            gauge={"axis": {"range": [0, 100]}, "bar": {"color": AMBER},
                   "steps": [{"range": [0, 40], "color": "#3a1414"},
                             {"range": [40, 70], "color": "#3a2c0d"},
                             {"range": [70, 100], "color": "#123322"}]},
        ))
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color=TEXT, height=280)
        st.plotly_chart(fig, use_container_width=True)
    with g2:
        fig = go.Figure(go.Indicator(
            mode="gauge+number", value=crack_risk_score,
            title={"text": "Structural Crack Risk Indicator", "font": {"color": TEXT, "size": 14}},
            number={"suffix": "%", "font": {"color": TEXT}},
            gauge={"axis": {"range": [0, 100]}, "bar": {"color": "#F87171"},
                   "steps": [{"range": [0, 40], "color": "#123322"},
                             {"range": [40, 70], "color": "#3a2c0d"},
                             {"range": [70, 100], "color": "#3a1414"}]},
        ))
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color=TEXT, height=280)
        st.plotly_chart(fig, use_container_width=True)

    st.write("")
    if blur < 100:
        st.warning("📷 Image appears blurry — sharpness below the reliability threshold. "
                    "Results may be less accurate; consider re-capturing the photo.")
    if ppe_compliance_score < 40:
        st.error("🦺 Low estimated PPE presence detected. Flag this site for a manual safety inspection.")
    elif ppe_compliance_score < 70:
        st.warning("🦺 Moderate PPE presence detected — verify with an on-site walkthrough.")
    else:
        st.success("🦺 Strong high-visibility PPE presence detected in this image.")

    if crack_risk_score > 60:
        st.error("🧱 High density of fine linear edge segments detected — possible surface cracking. "
                  "Recommend structural inspection.")
    else:
        st.info("🧱 No significant crack-like patterns detected in this image sample.")

    st.caption(
        "Note: this is a classical image-processing demonstration (color + edge analysis), "
        "not a trained deep-learning detector. In production this module would be backed by "
        "a fine-tuned object detection model (e.g. YOLO) for PPE and defect detection."
    )


def _make_synthetic_site_image():
    """Generate a synthetic construction-site-like image for demo purposes (no external download)."""
    h, w = 420, 640
    img = np.full((h, w, 3), (110, 120, 130), dtype=np.uint8)
    rng = np.random.default_rng(11)

    for y in range(0, 90):
        img[y, :] = (200 - y, 160 - y // 2, 120)

    for x in range(40, w, 60):
        cv2.line(img, (x, 90), (x, h - 20), (70, 70, 75), 3)
    for y in range(120, h - 20, 70):
        cv2.line(img, (40, y), (w - 40, y), (70, 70, 75), 3)

    for _ in range(14):
        x0, y0 = rng.integers(50, w - 50), rng.integers(100, h - 40)
        pts = [(x0, y0)]
        for _ in range(5):
            x0 += rng.integers(-15, 15)
            y0 += rng.integers(5, 20)
            pts.append((x0, y0))
        for i in range(len(pts) - 1):
            cv2.line(img, pts[i], pts[i + 1], (40, 40, 40), 1)

    for _ in range(6):
        cx, cy = rng.integers(60, w - 60), rng.integers(150, h - 60)
        cv2.ellipse(img, (cx, cy), (16, 22), 0, 0, 360, (0, 100, 255), -1)
        cv2.circle(img, (cx, cy - 28), 10, (0, 220, 255), -1)

    return Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
