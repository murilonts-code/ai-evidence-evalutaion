from typing import Optional
from PyPDF2 import PdfReader
from PIL import Image
import pytesseract
import os
import io


def extract_text(file_path: str) -> Optional[str]:
    try:
        # Extract file extension
        _, file_extension = os.path.splitext(file_path)
        file_extension = file_extension.lower()

        # Handle PDF files
        if file_extension == '.pdf':
            content = []
            with open(file_path, 'rb') as pdf_file:
                reader = PdfReader(pdf_file)
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        content.append(text)
            return "\n".join(content)

        # Handle image files
        elif file_extension in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
            with open(file_path, 'rb') as img_file:
                image = Image.open(io.BytesIO(img_file.read()))
                text = pytesseract.image_to_string(image)
            return text

        else:
            print(f"Unsupported file type: {file_extension}")
            return None

    except Exception as e:
        print(file_path)
        print(f"Error extracting text: {e}")
        return None