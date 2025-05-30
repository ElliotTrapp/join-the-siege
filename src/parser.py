import logging
import easyocr
import magic
from PIL import Image
from werkzeug.datastructures import FileStorage
from pypdf import PdfReader
from docx import Document

from src.util.clean_data import clean_data

# this needs to run only once to load the model into memory
ocr_reader = easyocr.Reader(['en']) 

def get_doc_format(doc: FileStorage) -> str:
    """
    Get the doc_format from magic library
    the formats we support are in VALID_DOC_FORMATS below
    """
    doc_format = magic.from_buffer(doc.stream.read(), mime=True)
    logging.info(f'{doc.filename} is a {doc_format}')
    return doc_format


def parse_pdf(doc: FileStorage) -> str:
    """Extract text from a PDF file."""
    full_text = ""
    reader = PdfReader(doc.stream)
    for page in reader.pages:
        # Don't do any cleaning yet, we'll do it all at once
        page_text = page.extract_text()
        full_text += f" {page_text}"
    return full_text


def parse_docx(doc: FileStorage) -> str:
    """Extract text from a DOCX file."""
    #img = Image.open(doc.stream)
    doc = Document(doc.stream)
    full_text = ""
    for para in doc.paragraphs:
        full_text += para.text
    return full_text


def parse_img(doc: FileStorage) -> str:
    """Extract text from JPG/PNG/TIFF with OCR"""
    img = Image.open(doc.stream)
    return " ".join(ocr_reader.readtext(img, detail=0))


def parse_txt(doc: FileStorage) -> str:
    """Extract text from a plain text file."""
    raw_bytes = doc.stream.read()
    raw_text = raw_bytes.decode('utf-8')
    return raw_text


VALID_DOC_FORMATS = {
    "application/pdf": parse_pdf,
    "image/tiff": parse_img,
    "image/jpeg": parse_img,
    "image/png": parse_img,
    "text/rtf": parse_txt,
    "text/plain": parse_txt,
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": parse_docx,
}

class Parser:
    """
    Contains all the logic and data relating to converts any file to a
    string of text ready for classification
    """
    def __init__(self):
        pass

    def parse(self, doc: FileStorage, doc_format: str) -> str:
        """
        Full pipeline for extracting and cleaning text from a single PDF file.
        Hash each file to avoid redundant processing if content hasn't changed.
        """
        try:
            try:
                raw_data = VALID_DOC_FORMATS[doc_format](doc)
            except Exception as e:
                raise Exception(f'failed to extract raw data from {doc.filename} which is a {doc_format}, {e}')
            if not raw_data:
                raise Exception(
                    f"{doc.filename} which is a {doc_format} gave empty raw data!"
                )
            logging.info(f"raw data: {raw_data[:500]}")
            try:
                cleaned_data = clean_data(raw_data)
            except Exception as e:
                raise Exception(f'failed to clean data from {doc.filename} which is a {doc_format}, {e}')
            if not cleaned_data:
                raise Exception(
                    f"{doc.filename} which is a {doc_format} gave empty clean data!"
                )
            logging.info(f"clean data: {cleaned_data[:500]}")
            return cleaned_data
        except Exception as e:
            raise Exception(f"Error processing file {doc.filename}: {e}")
