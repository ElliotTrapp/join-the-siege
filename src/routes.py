from flask import Blueprint, request, jsonify
import os
import logging
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.datastructures import FileStorage
from src.classifier import Classifier
from src.parser import Parser, get_doc_format, VALID_DOC_FORMATS
from src.config import config

api = Blueprint("api", __name__)

# Create these now so we can use them across requests
parser = Parser()
classifier = Classifier()

def is_valid_input_doc_format(doc_format):
  return doc_format in VALID_DOC_FORMATS.keys()

def is_valid_doc_size(doc: FileStorage):
  doc.seek(0, os.SEEK_END)
  size = doc.tell()
  doc.stream.seek(0)  # rewind to the start of the stream
  return size < config.MAX_DOC_BYTES

@api.route('/list_file_labels', methods=['GET'])
def list_file_labels():
    return jsonify({"labels": classifier.get_labels()})

@api.route('/list_file_embeddings', methods=['GET'])
def list_file_embeddings():
    return jsonify({"embeddings": classifier.get_embeddings()})

@api.route('/remove_file_label', methods=['POST'])
def remove_file_label():
    data = request.get_json()
    if not data:
        logging.error("no body in request")
        return jsonify({"error": "missing JSON body"}), 400

    label = data.get("label")
    if not label or not isinstance(label, str):
        logging.error("missing or invalid 'label' parameter")
        return jsonify({"error": "missing or invalid 'label' parameter"}), 400
    
    if label not in classifier.reference_embeddings:
      return jsonify({"error": f"{label} not found in current labels"})
    
    try:
      classifier.remove_label(label)
    except Exception as e:
        return jsonify({"error": f"failed to remove {label}, {e}"}), 500
    
    return jsonify({"labels": classifier.get_labels()})


@api.route('/add_file_label', methods=['POST'])
def add_file_label():
    data = request.get_json()
    if not data:
        logging.error("no body in request")
        return jsonify({"error": "missing JSON body"}), 400

    label = data.get("label")
    if not label or not isinstance(label, str):
        logging.error("missing or invalid 'label' parameter")
        return jsonify({"error": "missing or invalid 'label' parameter"}), 400

    embedding = data.get("embedding")
    if embedding is not None and not isinstance(embedding, str):
        logging.error("'embedding' parameter must be a string if provided")
        return jsonify({"error": "'embedding' parameter must be a string if provided"}), 400

    # At this point, 'label' is a string and 'words' is either None or a string
    try:
      classifier.add_label(label, embedding)
    except Exception as e:
        return jsonify({"error": f"failed to add label {label}, {e}"}), 500

    return jsonify({"labels": classifier.get_labels()})


@api.route('/classify_file', methods=['POST'])
def classify_file_route():
    if "file" not in request.files or not request.files["file"].filename:
        logging.error("no document in request")
        return jsonify({"error": "no document provided in request"}), 400

    # There is a doc, get it and it's format
    doc = request.files['file']
    doc_format = get_doc_format(doc)

    if not is_valid_doc_size(doc):
        return jsonify({"error": f"doc exceeds {config.MAX_DOC_BYTES} MB max doc size"}), 400

    if not is_valid_input_doc_format(doc_format):
        return jsonify({"error": f"{doc_format} is not a valid format. Valid formats are: {VALID_DOC_FORMATS.keys()}"}), 415

    logging.info(f'parsing {doc} as a {doc_format}')
    parsed_doc = parser.parse(doc, doc_format)
    logging.info(f'successfully parsed {doc}: parsed data:{parsed_doc[:500]}')
    doc_class, confidence = classifier.classify(parsed_doc)
    logging.info(f'successfully classified {doc}: doc class:{doc_class}')
    return jsonify({"doc_class": doc_class, "confidence": confidence}), 200

@api.route('/classify_files', methods=['POST'])
def classify_files_route():
    if "files[]" not in request.files or not request.files.getlist("files[]"):
        logging.error("no documents in request")
        return jsonify({"error": "no documents provided in request"}), 400

    docs = request.files.getlist("files[]")
    results = []

    for doc in docs:
      # There is a doc, get it and it's format
      doc_format = get_doc_format(doc)

      if not is_valid_doc_size(doc):
          results.append({"file": doc.filename, "error": f"doc exceeds {config.MAX_DOC_BYTES} MB max doc size"})
          continue

      if not is_valid_input_doc_format(doc_format):
          results.append({"file": doc.filename, "error": f"{doc_format} is not a valid format: {VALID_DOC_FORMATS.keys()}"})
          continue

      logging.info(f'parsing {doc} as a {doc_format}')
      parsed_doc = parser.parse(doc, doc_format)
      logging.info(f'successfully parsed {doc}: parsed data:{parsed_doc[:500]}')
      doc_class, confidence = classifier.classify(parsed_doc)
      results.append({"file": doc.filename, "result": {"doc_class": doc_class, "confidence": confidence}})

    return jsonify(results)
