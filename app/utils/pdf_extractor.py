import io
from typing import Optional
import PyPDF2


def extract_text_from_pdf(pdf_bytes: bytes) -> Optional[str]:
    """
    Извлекает текст из PDF файла.
    
    Args:
        pdf_bytes: Байты PDF файла
        
    Returns:
        Извлеченный текст или None в случае ошибки
    """
    try:
        # Создаем BytesIO объект из байтов
        pdf_file = io.BytesIO(pdf_bytes)
        
        # Создаем PDF reader
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        # Извлекаем текст со всех страниц
        text_parts = []
        for page_num, page in enumerate(pdf_reader.pages, start=1):
            try:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
            except Exception as page_err:
                print(f"Warning: Could not extract text from page {page_num}: {page_err}")
                continue
        
        # Объединяем текст со всех страниц
        full_text = "\n\n".join(text_parts)
        
        print(f"✅ Successfully extracted {len(full_text)} characters from PDF ({len(pdf_reader.pages)} pages)")
        
        return full_text if full_text.strip() else None
        
    except Exception as e:
        print(f"❌ Error extracting text from PDF: {e}")
        import traceback
        print(traceback.format_exc())
        return None

