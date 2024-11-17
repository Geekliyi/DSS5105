from PyPDF2 import PdfReader
from docx import Document
import re

def clean_text(text):
    return re.sub(r'[\x00-\x1F\x7F]', '', text)

def pdf_to_word(pdf_path, word_path):
    try:
        pdf_reader = PdfReader(pdf_path)
        word_document = Document()

        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text = page.extract_text()

            if text:
                cleaned_text = clean_text(text)
                word_document.add_paragraph(cleaned_text)

        word_document.save(word_path)
        print(f"PDF 文件已成功转换为 Word 文件：{word_path}")

    except FileNotFoundError:
        print(f"错误：找不到文件 {pdf_path}，请检查文件路径。")
    except Exception as e:
        print(f"发生错误：{e}")

