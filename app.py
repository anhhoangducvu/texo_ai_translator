import streamlit as st
import os
import time
import zipfile
import io
from core.translator_engine import translate_docx, AI_READY

# --- CONFIG ---
st.set_page_config(page_title="TEXO AI Master Translator", page_icon="🔠", layout="wide")

# --- STYLE PREMIUM ---
st.markdown("""
<style>
    /* --- TỐI ƯU HÓA CSS THÍCH ỨNG (ADAPTIVE THEME V2.0) --- */
    
    .main-header { 
        background: linear-gradient(90deg, #1e3a8a, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800; 
        font-size: 38px; 
        text-align: center; 
        padding-bottom: 5px; 
        margin-bottom: 25px;
    }

    .stButton>button { 
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%) !important; 
        color: white !important; 
        border: none !important; 
        border-radius: 12px; 
        font-weight: bold; 
        padding: 0.6rem 1rem;
        width: 100%;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.2);
    }
    
    .stButton>button:hover { 
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.3);
    }

    /* File Status Card: Thỏa hiệp giữa 2 chế độ */
    .file-card {
        background: var(--secondary-background-color) !important;
        border: 1px solid rgba(59, 130, 246, 0.2) !important;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }

    .status-badge {
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 800;
        text-transform: uppercase;
    }
    
    /* Màu Badge tối ưu cho độ tương phản */
    .status-pending { background: #94a3b8; color: #ffffff !important; }
    .status-running { background: #3b82f6; color: #ffffff !important; }
    .status-success { background: #10b981; color: #ffffff !important; }
    .status-error { background: #ef4444; color: #ffffff !important; }

    .footer { text-align: center; color: #64748b; font-size: 11px; margin-top: 40px; border-top: 1px solid rgba(59, 130, 246, 0.1); padding-top: 20px; }
    
    /* Sidebar styling: Thích ứng tinh tế */
    .sidebar-section {
        background: rgba(59, 130, 246, 0.05);
        padding: 18px;
        border-radius: 12px;
        margin-bottom: 20px;
        border-left: 4px solid #3b82f6;
    }
    .sidebar-title { color: #1e40af; font-weight: 800; margin-bottom: 12px; display: block; font-size: 14px; }
    
    /* Quay lại màu sáng cho Title trong Dark Mode */
    @media (prefers-color-scheme: dark) {
        .sidebar-title { color: #60a5fa; }
    }
</style>
""", unsafe_allow_html=True)

# --- AUTH ---
def check_password():
    if "authenticated" not in st.session_state: st.session_state.authenticated = False
    if st.session_state.authenticated: return True
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h2 style='text-align: center; color: #FFD700; margin-top: 100px;'>🏦 TEXO TRANSLATOR AUTH</h2>", unsafe_allow_html=True)
        pwd = st.text_input("Mật khẩu truy cập hệ thống AI:", type="password")
        if st.button("XÁC THỰC"):
            if pwd == "texo2026":
                st.session_state.authenticated = True
                st.rerun()
            else: st.error("❌ Mật khẩu không chính xác.")
    return False

if not check_password(): st.stop()

# --- INITIALIZE STATE ---
if "processed_files" not in st.session_state:
    st.session_state.processed_files = {} # {filename: {"status": "pending", "out_path": None, "data": None}}

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<div class='sidebar-section'><span class='sidebar-title'>📘 HƯỚNG DẪN SỬ DỤNG</span>"
                "1. <b>Tải file:</b> Bạn có thể chọn nhiều file Word (.docx) cùng lúc hoặc kéo thả cả thư mục (nếu trình duyệt hỗ trợ).<br><br>"
                "2. <b>Cấu hình:</b> Chọn ngôn ngữ đích và chế độ Song ngữ (mặc định mở).<br><br>"
                "3. <b>Thực hiện:</b> Nhấn nút 'CHẠY DỊCH THUẬT' để AI bắt đầu xử lý.<br><br>"
                "4. <b>Chờ đợi:</b> Hệ thống dịch tuần tự từng file. Bạn có thể tải ngay file đã dịch xong mà không cần chờ toàn bộ."
                "</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='sidebar-section'><span class='sidebar-title'>⏳ THỜI GIAN DỰ KIẾN</span>"
                "Dựa trên khối lượng tài liệu kỹ thuật, thời gian trung bình:<br>"
                "- 1 file (10-20 trang): ~1-2 phút.<br>"
                "- File nhiều bảng biểu sẽ lâu hơn do cấu trúc phức tạp."
                "</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='sidebar-section'><span class='sidebar-title'>⚠️ LƯU Ý</span>"
                "- Chỉ hỗ trợ <b>.docx</b> (Word hiện đại).<br>"
                "- File dịch xong được đặt tên theo mẫu: <i>Dich_[Tên_file].docx</i><br>"
                "- Hãy kiểm tra lại các từ khóa chuyên ngành hiếm gặp sau khi tải về."
                "</div>", unsafe_allow_html=True)
    
    if st.button("♻️ LÀM MỚI DANH SÁCH"):
        st.session_state.processed_files = {}
        st.rerun()

# --- MAIN UI ---
st.markdown("<div class='main-header'>TEXO AI MASTER TRANSLATOR</div>", unsafe_allow_html=True)

col_cfg, col_proc = st.columns([1, 1.5], gap="large")

with col_cfg:
    st.markdown("### 🌐 Cấu hình & Tải lên")
    langs = {
        "Tiếng Việt (🇻🇳)": "vi", 
        "Tiếng Anh (🇺🇸)": "en", 
        "Tiếng Trung (🇨🇳)": "zh-CN", 
        "Tiếng Hàn (🇰🇷)": "ko", 
        "Tiếng Nhật (🇯🇵)": "ja"
    }
    target_lang = st.selectbox("Ngôn ngữ đích:", list(langs.keys()))
    is_bilingual = st.checkbox("Dịch Song ngữ (Gốc + Dịch)", value=True)
    
    uploaded_files = st.file_uploader("Tải hồ sơ Word (Chọn nhiều file)", type=["docx"], accept_multiple_files=True)
    
    if uploaded_files:
        st.write(f"📁 Đã tải lên: **{len(uploaded_files)}** file")
        if st.button("🚀 CHẠY DỊCH THUẬT HÀNG LOẠT"):
            # Prepare state
            for f in uploaded_files:
                if f.name not in st.session_state.processed_files:
                    st.session_state.processed_files[f.name] = {"status": "pending", "out_path": None, "data": None}
            
            # Progress tracking
            total_files = len(uploaded_files)
            # Simple heuristic: 1min per file base + size factor
            est_total_seconds = sum([max(30, int(f.size / 1024 / 10)) for f in uploaded_files])
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            timer_text = st.empty()
            
            start_time = time.time()
            
            for i, doc_file in enumerate(uploaded_files):
                if st.session_state.processed_files[doc_file.name]["status"] == "success":
                    continue # Skip already done
                    
                st.session_state.processed_files[doc_file.name]["status"] = "running"
                status_text.write(f"⏳ Đang xử lý file ({i+1}/{total_files}): **{doc_file.name}**...")
                
                # Update Timer
                elapsed = time.time() - start_time
                remaining = max(0, est_total_seconds - (elapsed / (i+1 or 1) * total_files)) if i > 0 else est_total_seconds
                timer_text.markdown(f"⏱️ **Thời gian dự kiến còn lại:** {int(remaining//60)} phút {int(remaining%60)} giây")
                
                try:
                    in_path = f"temp_{doc_file.name}"
                    out_path = f"Dich_{doc_file.name}"
                    
                    with open(in_path, "wb") as f:
                        f.write(doc_file.getbuffer())
                    
                    success = translate_docx(in_path, out_path, langs[target_lang], is_bilingual)
                    
                    if success:
                        with open(out_path, "rb") as f_o:
                            file_data = f_o.read()
                        st.session_state.processed_files[doc_file.name] = {
                            "status": "success", 
                            "out_path": out_path,
                            "data": file_data
                        }
                    else:
                        st.session_state.processed_files[doc_file.name]["status"] = "error"
                    
                    # Cleanup temp in
                    if os.path.exists(in_path): os.remove(in_path)
                    if os.path.exists(out_path): os.remove(out_path)
                except Exception as e:
                    st.session_state.processed_files[doc_file.name]["status"] = "error"
                    st.error(f"Lỗi file {doc_file.name}: {e}")
                
                progress_bar.progress((i + 1) / total_files)
            
            status_text.success(f"✅ Hoàn tất dịch thuật {total_files} file!")
            timer_text.empty()
            st.balloons()

with col_proc:
    st.markdown("### 📦 Trạng thái & Tải về")
    
    if not st.session_state.processed_files:
        st.markdown("<div style='height: 200px; border: 2px dashed #444; border-radius: 12px; display: flex; align-items: center; justify-content: center; color: #666;'>Chờ tải file và thực thi...</div>", unsafe_allow_html=True)
    else:
        # Check if all successful for bulk download
        success_files = [f for f in st.session_state.processed_files.values() if f["status"] == "success"]
        
        if len(success_files) > 1:
            # Create ZIP
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                for fname, fmeta in st.session_state.processed_files.items():
                    if fmeta["status"] == "success" and fmeta["data"]:
                        zip_file.writestr(fmeta["out_path"], fmeta["data"])
            
            st.download_button(
                label="📥 TẢI XUỐNG TẤT CẢ (ZIP)",
                data=zip_buffer.getvalue(),
                file_name="TEXO_Dich_HàngLoạt.zip",
                mime="application/zip",
                use_container_width=True
            )
            st.divider()

        # Individual File List
        for fname, fmeta in st.session_state.processed_files.items():
            status = fmeta["status"]
            
            badge_class = f"status-{status}"
            status_label = "Chờ xử lý" if status == "pending" else "Đang dịch..." if status == "running" else "Hoàn tất" if status == "success" else "Lỗi"
            
            with st.container():
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.markdown(f"**{fname}**")
                    st.markdown(f"<span class='status-badge {badge_class}'>{status_label}</span>", unsafe_allow_html=True)
                with c2:
                    if status == "success":
                        st.download_button(
                            label="📥 Tải về",
                            data=fmeta["data"],
                            file_name=fmeta["out_path"],
                            key=f"dl_{fname}"
                        )
                    elif status == "error":
                        st.markdown("❌")
                st.markdown("---")

st.markdown("<div class='footer'>TEXO Engineering Department | AI Master Engine | Hoàng Đức Vũ</div>", unsafe_allow_html=True)
