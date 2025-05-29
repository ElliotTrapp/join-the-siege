from flask import Blueprint, request, jsonify
import os
import logging
import streamlit as st
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.datastructures import FileStorage
from src.classifier import Classifier
from src.parser import Parser, get_doc_format, VALID_DOC_FORMATS
from src.config import config

api = Blueprint("api", __name__)

def is_valid_input_doc_format(doc_format):
  return doc_format in VALID_DOC_FORMATS

def is_valid_doc_size(doc: FileStorage):
  doc.seek(0, os.SEEK_END)
  return doc.tell() < config.MAX_DOC_BYTES

@api.route('/heartbeat', methods=['GET'])
def heartbeat_route():
  pass

@api.route('/list_doc_types', methods=['GET'])
def list_doc_types():
  pass

@api.route('/remove_doc_type', methods=['POST'])
def remove_doc_type():
  pass

@api.route('/add_doc_type', methods=['POST'])
def add_doc_type():
  pass

@api.route('/classify_doc', methods=['POST'])
def classify_doc_route():
  if 'file' not in request.files:
    return jsonify({"error": "no document provided in request"}), 400
  if not request.files['file'].filename:
    return jsonify({"error": "document provided in request not named"}), 400
  
  # There is a doc, get it and it's format
  doc = request.files['file']
  doc_format = get_doc_format(doc)

  if not is_valid_doc_size(doc):
    return jsonify({"error": f"{doc} is too large. Max doc size is {config.MAX_DOC_SIZE}"}), 415
    
  if not is_valid_input_doc_format(doc_format):
    return jsonify({"error": f"{doc_format} is not a valid format. Valid formats are: {VALID_DOC_FORMATS}"}), 415

  logging.info(f'parsing {doc} and a {doc_format}')
  parsed_doc = Parser().parse(doc, doc_format)
  logging.info(f'successfully parsed {doc}: parsed data:{parsed_doc[:500]}')
  doc_class = Classifier().classify(parsed_doc)
  logging.info(f'successfully classified {doc}: doc class:{doc_class}')
  return jsonify({"doc_class": doc_class}), 200

@api.route('/classify_docs', methods=['POST'])
# TODO: finish
def classify_docs_route():
  if "files[]" not in request.files:
    logging.error("No files in request")
    return error_response("file_required")

  files = request.files.getlist("files[]")
  results = []

  if 'doc' not in request.docs:
    return jsonify({"error": "no document provided in request"}), 400
  if not request.docs['doc'].filename:
    return jsonify({"error": "document provided in request not named"}), 400
  
  # There is a doc, get it and it's format
  doc = request.docs['doc']
  doc_format = get_doc_format(doc)

  if not is_valid_input_doc_format(doc_format):
    return jsonify({"error": f"{doc_format} is not a valid format. Valid formats are: {VALID_DOC_FORMATS}"}), 415

  parsed_doc = Parser.parse(doc, doc_format)
  doc_class = Classifier.classify(parsed_doc)
  return jsonify({"doc_class": doc_class}), 200
