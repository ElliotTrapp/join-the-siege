import logging
import heapq
from dataclasses import dataclass, field
from sentence_transformers import SentenceTransformer
from werkzeug.datastructures import FileStorage
from src.config import config

model = SentenceTransformer(config.MODEL)

class Classifier:
    def __init__(self):
        self.reference_sentences = config.REFERENCE_SENTENCES

    def add_sentence(self, label: str, sentence: str):
        self.reference_sentences[label] = sentence

    def classify(self, parsed_doc: str):
        results = []
        confidence = 1.0
        doc_class = 'unknown'
        reference_embeddings = model.encode(list(self.reference_sentences.values()))
        check_embedding = model.encode([parsed_doc])
        for label, embedding in zip(self.reference_sentences.keys(), reference_embeddings):
            logging.info(f'comparing {len(check_embedding)} long embedding with {len(embedding)} long embedding to see if doc is a {label}')
            similarity = model.similarity(check_embedding, embedding).item()
            result = (similarity, label)
            results.append(result)
        results.sort(key=lambda result: result[0], reverse=True)
        logging.info(f'all results: {results}')
        top_result = results[0]
        if top_result[0] > config.MIN_CONFIDENCE:
            doc_class, confidence = top_result
            logging.info(f'doc was identified as a {doc_class} with confidence of {confidence}')
        return doc_class, confidence
