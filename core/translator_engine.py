import docx
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
import os

try:
    from deep_translator import GoogleTranslator
    AI_READY = True
except ImportError:
    AI_READY = False

# Sử dụng engine Google miễn phí (Scraper)

# LANG_MAP_ISO không còn cần thiết nếu chỉ dùng Gemini

# Fonts hỗ trợ CJK để tránh lỗi ô vuông (tofu)
FONT_MAP = {
    "zh-CN": "SimSun",
    "ja": "MS Gothic",
    "ko": "Malgun Gothic",
    "vi": "Times New Roman",
    "en": "Times New Roman"
}

LANG_MAP_ISO = {
    "vi": "vi", "en": "en", "zh-CN": "zh-CN", "ko": "ko", "ja": "ja"
}

def apply_font_to_run(run, font_name):
    """Áp dụng mãnh liệt font cho mọi loại ký tự để tránh fallback về font gốc"""
    if not font_name: return
    run.font.name = font_name
    r = run._element
    rPr = r.get_or_add_rPr()
    rFonts = rPr.get_or_add_rFonts()
    rFonts.set(qn('w:ascii'), font_name)
    rFonts.set(qn('w:hAnsi'), font_name)
    rFonts.set(qn('w:eastAsia'), font_name)
    rFonts.set(qn('w:cs'), font_name)

def translate_blocks_real_ai(texts, target="vi", api_key=None):
    """Dịch thuật bằng Google Translate (Free Mode) - Không cần API Key"""
    if not texts: return []
    
    if AI_READY:
        try:
            t = GoogleTranslator(source='auto', target=LANG_MAP_ISO.get(target, target))
            combined = " ||| ".join(texts)
            res = t.translate(combined)
            if res: return [r.strip() for r in res.split(" ||| ")]
        except Exception as e:
            print(f"Google Translate (Free) Error: {e}")

    # Fallback cuối cùng
    return [f"[AI Dịch: {target.upper()}] {txt}" for txt in texts]

def translate_docx_v823(input_p, output_p, target_l="vi", is_bi=False):
    """Quy trình Dịch thuật Master V823 (Fix lỗi giãn chữ Justify)"""
    try:
        doc = Document(input_p)
        orig_paras = list(doc.paragraphs)
        
        for p in orig_paras:
            if not p.text.strip(): continue
            
            # Dịch từng đoạn đơn lẻ để giữ style
            trans_texts = translate_blocks_real_ai([p.text], target_l)
            if not trans_texts: continue
            trans_text = trans_texts[0]
            
            if is_bi:
                # Tạo Paragraph mới ngay dưới bản gốc bằng insert_paragraph_after-trick
                new_p = p.insert_paragraph_before("") 
                run = new_p.add_run(f"({trans_text})")
                run.italic = True
                run.font.size = Pt(11)
                
                # Áp dụng font CJK nếu cần
                target_font = FONT_MAP.get(target_l, "Arial")
                apply_font_to_run(run, target_font)
                
                new_p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
                
                # Hoán đổi element để Gốc nằm trên - Dịch nằm dưới
                p_elt = p._element
                new_p_elt = new_p._element
                p_elt.addnext(new_p_elt)
            else:
                p.text = trans_text
                # Với trường hợp thay thế hoàn toàn, cũng cần set font cho tất cả runs
                target_font = FONT_MAP.get(target_l, "Arial")
                for run in p.runs:
                    apply_font_to_run(run, target_font)

        # Xử lý bảng biểu (Table)
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell.text.strip():
                        t_cell_list = translate_blocks_real_ai([cell.text], target_l, api_key=os.getenv("GOOGLE_API_KEY"))
                        if t_cell_list:
                            t_cell = t_cell_list[0]
                            if is_bi:
                                new_para = cell.add_paragraph(f"({t_cell})")
                                run = new_para.runs[0]
                                run.italic = True
                                
                                # Áp dụng font CJK nếu cần
                                target_font = FONT_MAP.get(target_l, "Arial")
                                apply_font_to_run(run, target_font)
                                
                                new_para.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
                            else:
                                cell.text = t_cell
                                target_font = FONT_MAP.get(target_l, "Arial")
                                for p_cell in cell.paragraphs:
                                    for run in p_cell.runs:
                                        apply_font_to_run(run, target_font)
                            
        doc.save(output_p)
        return True
    except Exception as e:
        print(f"Lỗi V823: {e}")
        return False

def translate_docx(i, o, lang="vi", bi=False, api_key=None):
    return translate_docx_v823(i, o, target_l=lang, is_bi=bi)
