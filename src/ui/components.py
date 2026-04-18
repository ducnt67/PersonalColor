import streamlit as st

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
    st.markdown("""
    <div class="hero-box">
        <div class="hero-title">🌸 Personal Color Prosedure</div>
        <div class="hero-subtitle">
            Khám phá mùa sắc cá nhân, undertone và gợi ý phong cách phù hợp từ ảnh khuôn mặt
            kết hợp cùng thông số cơ thể. Giao diện được tối giản theo phong cách trắng - hồng nhẹ,
            chữ đen rõ ràng và dễ nhìn hơn.
        </div>
        <div class="pill-row">
            <div class="pill">AI Facial Analysis</div>
            <div class="pill">Personal Color Season</div>
            <div class="pill">Body Shape Styling</div>
            <div class="pill">Beauty Suggestions</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def load_css(file_name):
    with open(file_name, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
