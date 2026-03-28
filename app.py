import streamlit as st
import os
from core.translator_engine import translate_docx, AI_READY

# --- CONFIG ---
st.set_page_config(page_title="TEXO AI Translator", page_icon="🔠", layout="wide")

# --- STYLE PREMIUM ---
st.markdown("""
<style>
    .stApp { background-color: #0A1931 !important; color: #ffffff !important; }
    h1, h2, h3, h4, h5, h6, p, span, div, li, label, .stMarkdown { color: #ffffff !important; }
    .main-header { color: #FFD700 !important; font-weight: 800; font-size: 32px; text-align: center; border-bottom: 2px solid #FFD700; padding-bottom: 10px; margin-bottom: 20px; }
    .stButton>button { background: #152A4A !important; color: #FFD700 !important; border: 1px solid #FFD700 !important; border-radius: 12px; font-weight: bold; height: 3.5em; width: 100%; }
    .stButton>button:hover { background: #FFD700 !important; color: #0A1931 !important; transform: scale(1.02); transition: 0.2s; }
    .stSelectbox div[data-baseweb="select"] { background-color: #152A4A !important; color: white !important; }
    .footer { text-align: center; color: #888; font-size: 12px; margin-top: 50px; }
</style>
""", unsafe_allow_html=True)

# --- AUTH ---
def check_password():
    if "authenticated" not in st.session_state: st.session_state.authenticated = False
    if st.session_state.authenticated: return True
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1: st.write("")
    with col2:
        st.markdown("<h2 style='text-align: center; color: #FFD700;'>🏦 TEXO AI TRANSLATOR</h2>", unsafe_allow_html=True)
        pwd = st.text_input("Mật khẩu:", type="password")
        if st.button("XÁC THỰC"):
            if pwd == "texo2026":
                st.session_state.authenticated = True
                st.rerun()
            else: st.error("❌ Truy cập thất bại.")
    return False

if not check_password(): st.stop()

# --- MAIN ---
st.markdown("<div class='main-header'>🔠 SIÊU DỊCH THUẬT MASTER POLYGLOT</div>", unsafe_allow_html=True)

if AI_READY:
    st.success("✨ Engine AI Cloud: **SẴN SÀNG**")
else:
    st.warning("🔄 Chế độ: **Hybrid dự phòng** (Tốc độ có thể chậm hơn)")

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("### 🌐 Cấu hình ngôn ngữ")
    langs = {
        "Tiếng Việt (🇻🇳)": "vi", 
        "Tiếng Anh (🇺🇸)": "en", 
        "Tiếng Trung (🇨🇳)": "zh-CN", 
        "Tiếng Hàn (🇰🇷)": "ko", 
        "Tiếng Nhật (🇯🇵)": "ja"
    }
    target_lang = st.selectbox("Ngôn ngữ đích:", list(langs.keys()))
    is_bilingual = st.checkbox("Dịch Song ngữ (Bilingual Mode)", value=True)
    
    doc_file = st.file_uploader("Tải hồ sơ Word (.docx)", type=["docx"])

with col2:
    st.markdown("### 🚀 Thực thi dịch thuật")
    if doc_file:
        st.info(f"Đã chọn: **{doc_file.name}**")
        if st.button("🚀 THỰC THI DỊCH THUẬT SIÊU TỐC"):
            with st.spinner("AI đang giải mã đa ngôn ngữ..."):
                try:
                    in_path = "temp_trans_in.docx"
                    out_path = f"Dich_{doc_file.name}"
                    
                    with open(in_path, "wb") as f:
                        f.write(doc_file.getbuffer())
                    
                    if translate_docx(in_path, out_path, langs[target_lang], is_bilingual):
                        st.success("🎉 Đã dịch xong hồ sơ.")
                        st.balloons()
                        with open(out_path, "rb") as f_o:
                            st.download_button("📥 TẢI HỒ SƠ DỊCH", f_o, out_path)
                    
                    # Cleanup
                    if os.path.exists(in_path): os.remove(in_path)
                except Exception as e:
                    st.error(f"❌ Lỗi dịch thuật: {e}")
    else:
        st.markdown("<div style='height: 200px; border: 2px dashed #333; border-radius: 12px; display: flex; align-items: center; justify-content: center; color: #666;'>Tải lên tài liệu kỹ thuật để bắt đầu dịch thuật</div>", unsafe_allow_html=True)

st.markdown("<div class='footer'>TEXO Engineering Department | AI Master Engine | Hoàng Đức Vũ</div>", unsafe_allow_html=True)
