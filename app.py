import streamlit as st
import os
from core.translator_engine import translate_docx, AI_READY

# --- CONFIG ---
st.set_page_config(page_title="TEXO AI Translator", page_icon="🔠", layout="wide")

# --- STYLE PREMIUM ---
st.markdown("""
<style>
    .stApp { background-color: #050b18 !important; color: #ffffff !important; }
    h1, h2, h3, h4, h5, h6, p, span, div, li, label, .stMarkdown { color: #e0e6ed !important; }
    .main-header { 
        background: linear-gradient(90deg, #1e3a8a, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800; 
        font-size: 40px; 
        text-align: center; 
        padding-bottom: 10px; 
        margin-bottom: 20px;
    }
    .stButton>button { 
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%) !important; 
        color: white !important; 
        border: none !important; 
        border-radius: 12px; 
        font-weight: bold; 
        height: 3.5em; 
        width: 100%;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
    }
    .stButton>button:hover { 
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
        transition: 0.3s;
    }
    .stSelectbox div[data-baseweb="select"] { background-color: #111827 !important; color: white !important; border: 1px solid #374151 !important; }
    .preview-box {
        background: rgba(255, 255, 255, 0.03);
        border-left: 4px solid #3b82f6;
        padding: 15px;
        border-radius: 8px;
        margin-top: 10px;
        font-size: 14px;
        color: #cbd5e1;
        font-family: 'Inter', 'SimSun', 'MS Gothic', 'Malgun Gothic', sans-serif !important;
    }
    .footer { text-align: center; color: #4b5563; font-size: 12px; margin-top: 50px; border-top: 1px solid #1f2937; padding-top: 20px; }
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
st.markdown("<div class='main-header'>TEXO AI MASTER TRANSLATOR</div>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🛠 Hệ thống Dịch thuật")
    st.info("Hệ thống hỗ trợ dịch thuật hồ sơ kỹ thuật chuyên sâu với độ chính xác cao.")
    st.divider()
    st.caption("Engine: TEXO Master Engine (Zero-Config)")

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
                        
                        # Preview section
                        st.markdown("#### 👁 Xem trước kết quả")
                        from docx import Document
                        preview_doc = Document(out_path)
                        preview_count = 0
                        for p in preview_doc.paragraphs:
                            if p.text.strip() and preview_count < 3:
                                st.markdown(f"<div class='preview-box'>{p.text}</div>", unsafe_allow_html=True)
                                preview_count += 1
                        
                        with open(out_path, "rb") as f_o:
                            st.download_button("📥 TẢI HỒ SƠ DỊCH HOÀN CHỈNH", f_o, out_path)
                    
                    # Cleanup
                    if os.path.exists(in_path): os.remove(in_path)
                except Exception as e:
                    st.error(f"❌ Lỗi dịch thuật: {e}")
    else:
        st.markdown("<div style='height: 200px; border: 2px dashed #333; border-radius: 12px; display: flex; align-items: center; justify-content: center; color: #666;'>Tải lên tài liệu kỹ thuật để bắt đầu dịch thuật</div>", unsafe_allow_html=True)

st.markdown("<div class='footer'>TEXO Engineering Department | AI Master Engine | Hoàng Đức Vũ</div>", unsafe_allow_html=True)
