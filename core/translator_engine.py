import docx
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
import os

try:
    from deep_translator import GoogleTranslator
    AI_READY = True
except ImportError:
    AI_READY = False

# Ánh xạ ngôn ngữ ISO chính xác cho Deep Translator
LANG_MAP_ISO = {
    "vi": "vi", 
    "en": "en", 
    "zh-CN": "zh-CN", 
    "ko": "ko", 
    "ja": "ja",
    "cn": "zh-CN", 
    "kr": "ko", 
    "jp": "ja"
}

def translate_blocks_real_ai(texts, target="vi"):
    if AI_READY:
        try:
            from deep_translator import GoogleTranslator
            t = GoogleTranslator(source='auto', target=LANG_MAP_ISO.get(target, target))
            combined = " ||| ".join(texts)
            res = t.translate(combined)
            if res: return res.split(" ||| ")
        except: pass
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
                new_p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
                
                # Hoán đổi element để Gốc nằm trên - Dịch nằm dưới
                p_elt = p._element
                new_p_elt = new_p._element
                p_elt.addnext(new_p_elt)
            else:
                p.text = trans_text

        # Xử lý bảng biểu (Table)
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell.text.strip():
                        t_cell_list = translate_blocks_real_ai([cell.text], target_l)
                        if t_cell_list:
                            t_cell = t_cell_list[0]
                            if is_bi:
                                new_para = cell.add_paragraph(f"({t_cell})")
                                new_para.runs[0].italic = True
                                new_para.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
                            else:
                                cell.text = t_cell
                            
        doc.save(output_p)
        return True
    except Exception as e:
        print(f"Lỗi V823: {e}")
        return False

def translate_docx(i, o, lang="vi", bi=False):
    return translate_docx_v823(i, o, target_l=lang, is_bi=bi)
