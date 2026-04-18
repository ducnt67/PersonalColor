import os
import sys
import textwrap
import streamlit as st
from PIL import Image
import pandas as pd
from pathlib import Path

# Add project root to sys path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

from src.config import STYLE_CSS_PATH, PALETTES_DIR, SEASON_DESC, SEASON_STYLE_TIPS
from src.utils.file_loader import load_fashion_data, safe_get_unique
from src.services.color_service import predict
from src.services.palette_service import build_palette_html
from src.services.recommendation_service import render_profile_info
from src.ui.components import render_metric_card, render_hero, load_css

# =========================================================
# 1. CẤU HÌNH TRANG TỔNG QUAN & XÓA NAV MẶC ĐỊNH
# =========================================================
st.set_page_config(
    page_title="BeautyTone AI - Dashboard",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide Streamlit Nav, Header, Footer
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# Load CSS
if os.path.exists(STYLE_CSS_PATH):
    load_css(STYLE_CSS_PATH)

# =========================================================
# HEADER CHUYÊN NGHIỆP
# =========================================================
render_hero()

# =========================================================
# 2. XỬ LÝ DỮ LIỆU
# =========================================================
_, profile_df = load_fashion_data()

# =========================================================
# 3. MAIN UI - KÉO THẢ TỆP VÀ CHỤP ẢNH
# =========================================================

# Khối upload chính - Thiết kế như một vùng DropZone lớn
st.markdown("<div class='section-title' style='text-align: center; margin-top: 20px;'>Tải Lên Ảnh Của Bạn</div>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: var(--color-foreground); opacity: 0.8; margin-bottom: 25px;'>Kéo thả trực tiếp tệp hình ảnh vào bên dưới hoặc nhấp để chọn tệp. Hệ thống sẽ tự động bắt đầu phân tích.</p>", unsafe_allow_html=True)

img_file = None
upload_method = None

# Đặt toàn bộ phần upload và camera vào cột giữa để nhỏ gọn
col_space1, col_main, col_space2 = st.columns([1, 2, 1])

with col_main:
    upl_file = st.file_uploader("Kéo thả ảnh chân dung vào đây", type=["jpg", "jpeg", "png", "webp", "bmp", "tiff"], label_visibility="collapsed")
    if upl_file:
        img_file = upl_file
        upload_method = "Tải ảnh lên"

    st.markdown("<div style='text-align:center; margin: 15px 0;'><b>Hoặc</b></div>", unsafe_allow_html=True)

    # Khối Webcam - Tính năng phụ nhỏ hơn
    with st.expander("📸 Mở Camera", expanded=False):
        st.markdown("""<div class='beauty-tip' style='font-size: 0.9em; padding: 10px; margin-bottom: 10px;'>
            <b>Hướng dẫn:</b> Đưa chân dung lọt lưới elip và nhấn <b>Take Photo</b>
        </div>""", unsafe_allow_html=True)
        cam_file = st.camera_input("Mở Camera", key="camera_2", label_visibility="collapsed")
        if cam_file:
            img_file = cam_file
            upload_method = "Webcam"

st.markdown("<br><br>", unsafe_allow_html=True)
# =========================================================
# 5. KẾT QUẢ VÀ HIỂN THỊ
# =========================================================
if img_file is None:
    st.markdown(
        """
        <div class="result-banner">
            Chưa có ảnh đầu vào. Hãy tải ảnh hoặc chụp ảnh để bắt đầu phân tích.
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    image = Image.open(img_file).convert("RGB")
    
    # Ảnh webcam sẽ giữ nguyên, không lật hướng theo như yêu cầu
    pass

    # Thay vì chỉ adjust sáng, ta áp dụng quy trình crop nền trắng cho mặt
    from src.utils.image_processing import process_face_image
    
    with st.spinner("Đang tách nền và đóng khung khuôn mặt..."):
        image = process_face_image(image)

    st.markdown("<div class='section-title'>Ảnh đầu vào sau khi tiền xử lý</div>", unsafe_allow_html=True)
    img_col, info_col = st.columns([0.95, 1.05], gap="large")

    with img_col:
        st.image(image, use_container_width=True, caption="Ảnh dùng để phân tích")

    with info_col:
        with st.spinner("AI đang phân tích..."):
            fitz, under, season = predict(image)

        st.markdown(
            f"""
            <div class="result-banner">
                Phân tích hoàn tất. Hệ thống nhận diện bạn thuộc nhóm <b>{season}</b>
                với undertone <b>{under}</b>.
            </div>
            """,
            unsafe_allow_html=True
        )

        m1, m2, m3 = st.columns(3)
        with m1:
            render_metric_card("Fitzpatrick", fitz, "Đặc điểm sắc tố da")
        with m2:
            render_metric_card("Undertone", under, "Sắc độ nền da")
        with m3:
            render_metric_card("Season", season, "Mùa màu cá nhân")

    st.markdown("<div class='section-title'>Hồ sơ tư vấn cá nhân hóa</div>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs([
        "🎨 Bảng màu cá nhân",
        "💄 Beauty & Phụ kiện"
    ])

    # -----------------------------------------------------
    # TAB 1 - PALETTE
    # -----------------------------------------------------
    with tab1:
        st.markdown(
            f"""
            <div class="soft-card">
                <div class="sub-title">Mùa sắc của bạn: {season}</div>
                <div class="small-muted">{SEASON_DESC.get(season, "")}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Load palette dynamically from data folder
        palette_file = os.path.join(PALETTES_DIR, f"{season.lower()}_palette.csv")
        if os.path.exists(palette_file):
            try:
                palette_df = pd.read_csv(palette_file)
                st.markdown("<div class='section-title'>Các màu phù hợp với bạn</div>", unsafe_allow_html=True)
                st.markdown(build_palette_html(palette_df, max_items=12), unsafe_allow_html=True)
            except Exception as e:
                st.warning(f"Không đọc được file {palette_file}: {e}")
        else:
            st.warning(f"Chưa tìm thấy file {palette_file}")



    # -----------------------------------------------------
    # TAB 2 - STYLE TIPS
    # -----------------------------------------------------
    with tab2:
        st.markdown(
            f"""
            <div class="soft-card">
                <div class="sub-title">Beauty notes cho nhóm {season}</div>
                <div class="small-muted">
                    Những gợi ý dưới đây giúp giao diện trực quan hơn và giống một sản phẩm tư vấn thật hơn.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        for tip in SEASON_STYLE_TIPS.get(season, []):
            st.markdown(
                f"""
                <div class="beauty-tip">{tip}</div>
                """,
                unsafe_allow_html=True
            )

        c1, c2 = st.columns(2)

        with c1:
            st.markdown("<div class='section-title'>Trang sức phù hợp</div>", unsafe_allow_html=True)
            if "Lạnh" in under or "Cool" in under:
                st.markdown("<div class='beauty-tip'>Ưu tiên bạc, platinum, vàng trắng hoặc ngọc trai tông lạnh.</div>", unsafe_allow_html=True)
            elif "Ấm" in under or "Warm" in under:
                st.markdown("<div class='beauty-tip'>Ưu tiên vàng, rose gold, bronze hoặc phụ kiện tông ấm.</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='beauty-tip'>Bạn khá linh hoạt, có thể phối cả bạc và vàng tùy outfit.</div>", unsafe_allow_html=True)

            st.markdown("<div class='beauty-tip'>Hãy ưu tiên phụ kiện thanh lịch, ít chi tiết rối để tổng thể tinh tế hơn.</div>", unsafe_allow_html=True)

        with c2:
            st.markdown("<div class='section-title'>Gợi ý styling nhanh</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='beauty-tip'>Outfit nên ưu tiên bảng màu thuộc nhóm <b>{season}</b>.</div>", unsafe_allow_html=True)

# FOOTER CHUYÊN NGHIỆP
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: var(--color-foreground); opacity: 0.7; font-size: 0.9em; padding: 20px;">
    &copy; 2026 BeautyTone AI Studio. Sản phẩm giúp định hướng phong cách sống và làm đẹp.<br>
    Được thiết kế hiện đại, thông minh với <span style="color: var(--color-primary);">&hearts;</span> cho cộng đồng làm đẹp.
</div>
""", unsafe_allow_html=True)
