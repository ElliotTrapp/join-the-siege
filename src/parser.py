import logging
import re
import easyocr
import magic
from io import BytesIO
from PIL import Image
from werkzeug.datastructures import FileStorage
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from pypdf import PdfReader
from docx import Document

# Download stopwords if not already available
nltk.download("wordnet")
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))
# Create WordNetLemmatizer object
wnl = WordNetLemmatizer()
ocr_reader = easyocr.Reader(['en']) # this needs to run only once to load the model into memory

def get_doc_format(doc: FileStorage):
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
    img = Image.open(doc.stream)
    doc = Document(img)
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
    raw_text = doc.stream.read()
    return raw_text


VALID_DOC_FORMATS = {
    'application/pdf': parse_pdf,
    'image/tiff': parse_img,
    'image/jpeg': parse_img,
    'image/png': parse_img,
    'doc/txt': parse_txt,
    'doc/docx': parse_docx,
    #'doc/xlsx': parse_xlsx,
    #'doc/csv': parse_csv,
}

class Parser:
    def __init__(self):
        pass

    def clean_data(self, data):
        """
        Clean text by lowercasing, removing punctuation, lemmatizing, and removing stopwords.
        """
        try:
            data = data.lower()
            data = re.sub(r'[^a-zA-Z\s]', '', data)  # Remove punctuation and numbers
            tokens = data.split()
            # I could do all these in one line but I think this makes it more readable
            # Drop short words
            tokens = [token for token in tokens if len(token) > 2]
            # Drop stop words
            tokens = [token for token in tokens if token not in stop_words]
            # Lemmatize rest of words
            tokens = [wnl.lemmatize(token) for token in tokens]
            # Remake the string
            return " ".join(tokens)
        except Exception as e:
            raise Exception(f"Error during data cleaning: {e}")

    def parse(self, doc: FileStorage, doc_format: str):
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
                cleaned_data = self.clean_data(raw_data)
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
