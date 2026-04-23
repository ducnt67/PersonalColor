import streamlit as st
import base64
from pathlib import Path

def render_metric_card(label, value, sub=""):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-sub">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
def render_hero():
    banner_path = Path(__file__).resolve().parent.parent.parent / "assets" / "images" / "hero_watermark.png"
    banner_html = ""
    if banner_path.exists():
        with open(banner_path, "rb") as image_file:
            encoded_banner = base64.b64encode(image_file.read()).decode()
        banner_html = f'''
        <div class="hero-watermark-wrapper">
            <img src="data:image/png;base64,{encoded_banner}" alt="Hero Banner Watermark">
        </div>
        '''

    st.markdown(f"""
    {banner_html}
    <div class="hero-box">
        <div class="hero-content">
            <h1 class="hero-title">Khai Phá Vẻ Đẹp Độc Bản</h1>
            <p class="hero-subtitle">
                Hệ thống nhận diện AI chuyên sâu sẽ phân tích sắc tố da, tìm ra nhóm mùa của bạn và thiết kế cẩm nang làm đẹp mang tính cá nhân hóa tuyệt đối.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_badge(text, background="var(--color-primary)", color="#fff"):
    return f"""<span style="background:{background}; color:{color}; padding:4px 12px; border-radius:12px; font-size:0.85em; font-weight:600;">{text}</span>"""

def load_css(file_name):
    try:
        with open(file_name, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"Failed to load CSS: {e}")
