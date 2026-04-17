import streamlit as st
import cv2
import numpy as np
from PIL import Image

# ---------------- UI ----------------
st.title("🚧 Smart Road Reflectivity Monitoring System")
st.write("Upload road sign / lane marking / road stud image")

# ---------------- Blur Detection Function ----------------
def is_blurry(gray):
    return cv2.Laplacian(gray, cv2.CV_64F).var()

# ---------------- Upload ----------------
uploaded_file = st.file_uploader("Choose image", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:

    # Read image
    image = Image.open(uploaded_file)
    img = np.array(image)

    st.image(img, caption="Uploaded Image", use_column_width=True)

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # ---------------- Blur Check ----------------
    blur_score = is_blurry(gray)
    st.write(f"📷 Image Sharpness Score: {blur_score:.2f}")

    # If image is too blurry, stop processing
    if blur_score < 100:
        st.error("⚠️ Image too blurry for reliable reflectivity analysis")
        st.stop()

    # ---------------- Reflectivity Calculation ----------------
    brightness = np.mean(gray)
    contrast = gray.std()

    score = ((brightness * 0.6) + (contrast * 0.4)) / 255 * 100

    # Clamp score
    score = max(0, min(100, score))

    # ---------------- Output ----------------
    st.write(f"### Reflectivity Score: {score:.2f} / 100")

    if score > 65:
        st.success("🟢 GOOD: Road infrastructure is safe")
    elif score > 40:
        st.warning("🟡 MODERATE: Maintenance recommended")
    else:
        st.error("🔴 CRITICAL: Immediate action required")

    # ---------------- Explanation ----------------
    st.write("## Interpretation")

    if score > 65:
        st.info("Reflectivity is sufficient for night visibility.")
    elif score > 40:
        st.info("Reflectivity is degrading and needs monitoring.")
    else:
        st.info("Low reflectivity poses safety risks.")

    # ---------------- Visualization ----------------
    st.write("## Score Visualization")
    st.bar_chart([score])

    # ---------------- Context ----------------
    st.write("📍 System: Smart Road Infrastructure Monitoring Prototype")
    st.write("🛣️ Use Case: Detect faded road signs, markings, and studs for maintenance planning")