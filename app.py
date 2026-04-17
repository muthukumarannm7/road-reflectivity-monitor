import streamlit as st
import cv2
import numpy as np
from PIL import Image
import base64
from datetime import datetime

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Smart Road Reflectivity Monitoring",
    page_icon="🚧",
    layout="wide"
)

# ---------------- OPTIONAL BACKGROUND IMAGE ----------------
# Place a file named 'background.jpg' in the same folder as app.py
# If you don't have one yet, the app will still work with the default dark theme.

def set_bg_image(image_file):
    try:
        with open(image_file, "rb") as img:
            encoded = base64.b64encode(img.read()).decode()

        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: linear-gradient(rgba(10,15,25,0.88), rgba(10,15,25,0.92)),
                                  url("data:image/jpg;base64,{encoded}");
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
            }}
            </style>
            """,
            unsafe_allow_html=True,
        )
    except FileNotFoundError:
        pass

set_bg_image("background.jpg")

# ---------------- CUSTOM CSS ----------------
st.markdown(
    """
    <style>
    .main-title {
        text-align: center;
        color: #00D4FF;
        font-size: 42px;
        font-weight: bold;
        margin-bottom: 10px;
    }

    .sub-title {
        text-align: center;
        color: #D6EAF8;
        font-size: 18px;
        margin-bottom: 25px;
    }

    .card {
        background-color: rgba(20, 28, 40, 0.88);
        padding: 20px;
        border-radius: 18px;
        border: 1px solid rgba(255,255,255,0.08);
        margin-bottom: 18px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.35);
    }

    .score-box {
        background: linear-gradient(90deg, #00D4FF, #1ABC9C);
        color: black;
        padding: 20px;
        border-radius: 16px;
        text-align: center;
        font-size: 30px;
        font-weight: bold;
        margin-top: 10px;
        margin-bottom: 15px;
    }

    .footer {
        text-align: center;
        color: #AEB6BF;
        margin-top: 30px;
        font-size: 14px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------- SIDEBAR ----------------
st.sidebar.title("🚧 Project Dashboard")
st.sidebar.markdown("### Smart Road Reflectivity Monitoring")
st.sidebar.write("Developed for highway safety and infrastructure monitoring.")

asset_type = st.sidebar.selectbox(
    "Select Asset Type",
    ["Road Sign", "Pavement Marking", "Road Stud / Delineator"]
)

location = st.sidebar.text_input("Road / Highway Location", "Chennai Highway Segment")

st.sidebar.markdown("---")
st.sidebar.write("### Analysis Modules")
st.sidebar.write("✅ Blur Detection")
st.sidebar.write("✅ Brightness Analysis")
st.sidebar.write("✅ Contrast Analysis")
st.sidebar.write("✅ Maintenance Priority")

# ---------------- TITLE ----------------
st.markdown('<div class="main-title">🚧 Smart Road Reflectivity Monitoring System</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">Upload a road image to evaluate visibility, retroreflectivity and maintenance priority.</div>',
    unsafe_allow_html=True,
)

# ---------------- FUNCTIONS ----------------
def blur_score(gray):
    return cv2.Laplacian(gray, cv2.CV_64F).var()

# ---------------- IMAGE SOURCE ----------------
st.write("### Choose Input Method")
input_method = st.radio(
    "Select image source",
    ["Upload Image", "Use Camera"],
    horizontal=True
)

uploaded_file = None
captured_photo = None
image = None

if input_method == "Upload Image":
    uploaded_file = st.file_uploader(
        "Upload image of road sign, pavement marking or road stud",
        type=["jpg", "jpeg", "png"]
    )

    if uploaded_file is not None:
        image = Image.open(uploaded_file)

elif input_method == "Use Camera":
    captured_photo = st.camera_input("Capture live image from camera")

    if captured_photo is not None:
        import io
        image = Image.open(io.BytesIO(captured_photo.getvalue()))

if image is not None:

    img = np.array(image)

    # Convert RGBA to RGB if needed
    if len(img.shape) == 3 and img.shape[2] == 4:
        img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)

    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    # ---------------- IMAGE QUALITY CHECK ----------------
    sharpness = blur_score(gray)

    col1, col2 = st.columns([1.2, 1])

    with col1:
        st.image(img, caption="Uploaded Road Image", use_container_width=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.write("### Image Quality")
        st.write(f"Sharpness Score: {sharpness:.2f}")

        if sharpness < 30:
            st.error("⚠️ Image is too blurry for reliable analysis.")
            st.stop()

        elif sharpness < 100:
            st.warning("⚠️ Image is slightly blurry. Results may be less accurate.")

        else:
            st.success("✅ Image quality is suitable for analysis")
        st.markdown('</div>', unsafe_allow_html=True)

    # ---------------- DIRECT LIGHT CHECK ----------------
    white_pixels = np.sum(gray > 240) / gray.size

    if white_pixels > 0.40:
        st.error("⚠️ Too much direct light detected. Please capture the image without flashlight or strong external light.")
        st.stop()

    # ---------------- REFLECTIVITY ANALYSIS ----------------
    brightness = np.mean(gray)
    contrast = np.std(gray)

    reflectivity_score = ((brightness * 0.6) + (contrast * 0.4)) / 255 * 100
    reflectivity_score = max(0, min(100, reflectivity_score))

    # ---------------- PRIORITY ----------------
    if reflectivity_score > 65:
        condition = "GOOD"
        priority = "LOW"
        color_msg = "🟢 Infrastructure is clearly visible and safe."
    elif reflectivity_score > 40:
        condition = "MODERATE"
        priority = "MEDIUM"
        color_msg = "🟡 Reflectivity is degrading. Maintenance recommended soon."
    else:
        condition = "CRITICAL"
        priority = "HIGH"
        color_msg = "🔴 Poor visibility detected. Immediate maintenance required."

    # ---------------- RESULT CARDS ----------------
    st.markdown(
        f'<div class="score-box">Reflectivity Score: {reflectivity_score:.2f} / 100</div>',
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Condition", condition)

    with c2:
        st.metric("Maintenance Priority", priority)

    with c3:
        st.metric("Asset Type", asset_type)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.write("### Interpretation")
    st.write(color_msg)
    st.write(f"Location: {location}")
    st.write(f"Inspection Time: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
    st.markdown('</div>', unsafe_allow_html=True)

    # ---------------- GRAPH ----------------
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.write("### Reflectivity Visualization")
    st.progress(int(reflectivity_score))
    st.bar_chart([reflectivity_score])
    st.markdown('</div>', unsafe_allow_html=True)

    # ---------------- EXTRA DETAILS ----------------
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.write("### Technical Details")
    st.write(f"Brightness Value: {brightness:.2f}")
    st.write(f"Contrast Value: {contrast:.2f}")
    st.write(f"Sharpness Value: {sharpness:.2f}")
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- FOOTER ----------------
st.markdown(
    '<div class="footer">Prototype for highway safety monitoring • Built using Streamlit, OpenCV and NumPy</div>',
    unsafe_allow_html=True,
)



