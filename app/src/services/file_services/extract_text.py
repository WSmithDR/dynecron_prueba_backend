import io
import PyPDF2

def extract_text_from_pdf(content: bytes) -> str:
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
        text_parts = []
        
        for page in pdf_reader.pages:
            try:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
            except Exception as e:
                print(f"Warning: Error extracting text from a page: {str(e)}")
                continue
        
        return "\n\n".join(text_parts).strip()
        
    except Exception as e:
        error_msg = f"Error extracting text from PDF: {str(e)}"
        print(error_msg)
        raise Exception(error_msg)
