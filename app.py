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
from src.ui.components import render_metric_card, render_hero, render_badge, load_css

# =========================================================
# 1. CẤU HÌNH TRANG TỔNG QUAN & XÓA NAV MẶC ĐỊNH
# =========================================================
st.set_page_config(
    page_title="HueMe - Personal Color & Beauty Tech",
    page_icon="✨",
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
# HEADER TOP NAV (NEW)
# =========================================================

import base64

logo_path = BASE_DIR / "assets" / "images" / "logo.png"
logo_html = "<h2 class='app-logo'>✨ HueMe</h2>"

if logo_path.exists():
    with open(logo_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    logo_html = f'<div class="logo-container"><img src="data:image/png;base64,{encoded_string}" alt="HueMe Logo"></div>'

st.markdown(f"""
<div class="fixed-header">
    {logo_html}
    <div class="app-nav">
        <span class="active">Trang Chủ</span>
        <span>Phân Tích</span>
        <span>Bảng Màu</span>
        <span>Cẩm Nang</span>
    </div>
</div>
""", unsafe_allow_html=True)

# =========================================================
# HEADER CHUYÊN NGHIỆP
# =========================================================
render_hero()

# =========================================================
# 2. XỬ LÝ DỮ LIỆU
# =========================================================
_, profile_df = load_fashion_data()

# =========================================================
# 3. MAIN UI - CUNG CẤP ẢNH
# =========================================================

st.markdown("<div class='section-title'>Khởi tạo Hồ sơ Sắc đẹp</div>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: var(--color-accent); margin-bottom: 30px; font-weight: 400; max-width: 600px; margin-inline: auto;'>Hãy cung cấp ảnh chụp chân dung chân thực nhất. Ánh sáng tự nhiên và khuôn mặt mộc sẽ mang lại kết quả phân tích chính xác nhất từ hệ thống AI của chúng tôi.</p>", unsafe_allow_html=True)

img_file = None
upload_method = None

# Chuyển đổi trạng thái input
if 'upload_mode' not in st.session_state:
    st.session_state.upload_mode = 'upload'

st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)
col_space1, col1, col2, col_space2 = st.columns([1, 1.5, 1.5, 1])

with col1:
    if st.button("📁 Tải Ảnh Từ Thiết Bị", use_container_width=True):
        st.session_state.upload_mode = 'upload'
with col2:
    if st.button("📸 Mở Camera Trực Tiếp", use_container_width=True):
        st.session_state.upload_mode = 'camera'

st.markdown("<div style='margin-bottom: 32px;'></div>", unsafe_allow_html=True)

_, col_main, _ = st.columns([1, 2, 1])
with col_main:
    if st.session_state.upload_mode == 'upload':
        upl_file = st.file_uploader("Kéo thả ảnh chân dung vào đây", type=["jpg", "jpeg", "png", "webp", "bmp", "tiff"], label_visibility="collapsed")
        if upl_file:
            img_file = upl_file
            upload_method = "Tải ảnh lên"
    else:
        st.markdown("""
        <div class='beauty-tip' style='padding: 12px; margin-bottom: 20px; font-size: 0.95rem; text-align: center;'>
            <b>Lưu ý:</b> Đảm bảo môi trường sáng, nhìn thẳng vào ống kính và khuôn mặt rõ trong khung. Không dùng filter để có kết quả màu chuẩn nhất.
        </div>""", unsafe_allow_html=True)
        cam_file = st.camera_input("Mở Camera", key="camera_2", label_visibility="collapsed")
        if cam_file:
            img_file = cam_file
            upload_method = "Webcam"

# =========================================================
# 5. KẾT QUẢ VÀ HIỂN THỊ
# =========================================================
if img_file is None:
    st.markdown(
        """
        <div class="result-banner" style="justify-content: center; color: var(--color-accent); border-left: none; border-top: 4px solid var(--color-primary); border-radius: 16px; background: #fff;">
            Hệ thống AI đang chờ ảnh chân dung của bạn để bắt đầu phân tích... ✨
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    image = Image.open(img_file).convert("RGB")
    
    # Lật ngược ảnh lại cho chuẩn với webcam (bỏ hiệu ứng kính gương)
    if upload_method == "Webcam":
        from PIL import ImageOps
        image = ImageOps.mirror(image)
        
    # Tiền xử lý
    from src.utils.image_processing import process_face_image
    
    with st.spinner("✨ AI đang phân tích đường nét và sắc tố da của bạn..."):
        image = process_face_image(image)

    st.markdown("<div class='section-title'>Hồ Sơ Sắc Đẹp Của Bạn</div>", unsafe_allow_html=True)
    img_col, info_col = st.columns([0.9, 1.1], gap="large")

    with img_col:
        st.markdown("<div class='soft-card' style='padding:16px; display:flex; flex-direction:column; align-items:center;'>", unsafe_allow_html=True)
        st.markdown("<div class='result-image-wrapper'>", unsafe_allow_html=True)
        st.image(image, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div style='margin-top: 16px; font-size: 0.9rem; color: var(--color-accent); font-weight: 500;'>Ảnh chân dung đã được số hóa</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with info_col:
        with st.spinner("✨ Đang trích xuất dữ liệu mùa màu sắc..."):
            fitz, under, season = predict(image)
        
        season_badge = render_badge("Premium Match", "#E96BA2", "#fff")

        st.markdown(
            f"""
            <div class="result-banner">
                <div>
                   <h3 style="margin:0 0 12px 0; font-size:1.5rem; color:var(--color-foreground);">Nhóm mùa hiện tại: <span style="color:var(--color-primary);">{season}</span> {season_badge}</h3>
                   <span style="font-size:1.05rem; color:var(--color-accent); line-height: 1.6; display: inline-block;">
                        Thông qua phân tích cấu trúc sắc tố da, hệ thống xác nhận bạn thuộc nhóm <b>{season}</b>, mức độ Fitzpatrick là <b>{fitz}</b> với undertone cơ bản là <b>{under}</b>.
                   </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        m1, m2, m3 = st.columns(3)
        with m1:
            render_metric_card("Tone Da", fitz, "Fitzpatrick")
        with m2:
            render_metric_card("Sắc Độ Da", under, "Undertone")
        with m3:
            render_metric_card("Mùa Sắc", season, "Season Match")

    # -----------------------------------------------------
    # CẨM NANG LIÊN TỤC (BỎ CHIA CỘT VÀ TABS)
    # -----------------------------------------------------
    st.markdown("<div style='margin-top:48px;'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Cẩm Nang Cá Nhân Hóa</div>", unsafe_allow_html=True)
    
    st.markdown(
        f"""
        <div class="soft-card" style="margin-bottom:32px;">
            <div class="sub-title" style="color: var(--color-primary);">Bảng Màu Đề Xuất Của {season}</div>
            <div class="small-muted" style="font-size: 1.05rem;">{SEASON_DESC.get(season, "Một mùa màu rực rỡ và đặc biệt phù hợp với tone da của bạn.")}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Load palette
    palette_file = os.path.join(PALETTES_DIR, f"{season.lower()}_palette.csv")
    if os.path.exists(palette_file):
        try:
            palette_df = pd.read_csv(palette_file)
            st.markdown(build_palette_html(palette_df, max_items=12), unsafe_allow_html=True)
        except Exception as e:
            st.warning(f"Không đọc được file {palette_file}: {e}")
            
    st.markdown("<div style='margin-top:40px;'></div>", unsafe_allow_html=True)
    
    st.markdown(
        f"""
        <div class="soft-card" style="margin-bottom:24px;">
            <div class="sub-title" style="color: var(--color-primary);">Quy Tắc Làm Đẹp Dành Riêng Cho {season}</div>
            <div class="small-muted" style="font-size: 1.05rem;">
                Dựa trên đặc điểm nền da của bạn, chúng tôi đã biên soạn những nguyên tắc vàng để giúp bạn luôn xuất hiện rạng rỡ và thanh lịch nhất.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div class='styling-block'>", unsafe_allow_html=True)
    for tip in SEASON_STYLE_TIPS.get(season, []):
        st.markdown(f"<div class='beauty-tip'>✨ {tip}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='sub-title' style='margin-bottom:16px;'>Lựa Chọn Trang Sức & Phụ Kiện</div>", unsafe_allow_html=True)
    st.markdown("<div class='styling-block'>", unsafe_allow_html=True)
    if "Lạnh" in under or "Cool" in under:
        st.markdown("<div class='beauty-tip'>Ưu tiên bạch kim, viền bạc, vàng trắng hoặc ngọc trai biển tinh khiết để làm sáng và tôn lên sự thanh tao của sắc da lạnh.</div>", unsafe_allow_html=True)
    elif "Ấm" in under or "Warm" in under:
        st.markdown("<div class='beauty-tip'>Cộng hưởng hoàn hảo với tone da ấm nhờ các thiết kế từ vàng nguyên bản, rose gold, đồng bóng hoặc ngọc trai mang tông kem ngọt ngào.</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='beauty-tip'>Tone da trung tính cho phép bạn linh hoạt mix & match vô hạn giữa sự thanh lịch của ánh bạc và nét ấm áp của vàng.</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='sub-title' style='margin-bottom:16px;'>Nguyên Tắc Phối Hợp Màu Sắc Tủ Đồ</div>", unsafe_allow_html=True)
    st.markdown("<div class='styling-block'>", unsafe_allow_html=True)
    st.markdown(f"<div class='beauty-tip'>Xây dựng một <b>Capsule Wardrobe (Tủ Đồ Tối Giản)</b> ưu tiên sử dụng các màu cốt lõi thuộc chuỗi màu của <b>{season}</b>. Màu sắc càng gần mặt (áo lót, khăn, dây chuyền) càng cần tuân thủ bảng màu chuẩn.</div>", unsafe_allow_html=True)
    st.markdown("<div class='beauty-tip'>Nếu bạn muốn dùng một màu trái ngược với bảng màu khuyến nghị, hãy cân chỉnh bằng cách đưa màu đó ra xa vùng chân dung (như quần dài, váy vạt dưới, giày, hoặc túi xách chân).</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# FOOTER CHUYÊN NGHIỆP
st.markdown("""
<div class="fixed-footer">
    <span><strong>HueMe</strong> &copy; 2026. Empower Your True Colors.</span>
    <span>•</span>
    <span>Designed with <span style="font-size:1.05rem; color: var(--color-primary);">&hearts;</span> for your confidence. All rights reserved.</span>
</div>
""", unsafe_allow_html=True)
