from dataclasses import dataclass, field
from sentence_transformers import SentenceTransformer
from werkzeug.datastructures import FileStorage
from src.config import config

model = SentenceTransformer(config.MODEL)

@dataclass
class Doc:
    doc_format: str
    text: str

class Classifier:
    def __init__(self):
        self.reference_sentences = config.REFERENCE_SENTENCES

    def add_sentence(self, label: str, sentence: str):
        self.reference_sentences[label] = sentence

    def classify(self, parsed_doc: str):
        results = {}
        doc_class = 'unknown'
        reference_embeddings = model.encode(list(self.reference_sentences.values()))
        check_embedding = model.encode([parsed_doc])
        for label, embedding in zip([self.reference_sentences.keys(), reference_embeddings]):
            similarity = model.similarity(check_embedding, embedding)
            results[label] = similarity
        results = results[]
        print(results)
        if results[0] > config.MIN_CONFIDENCE:
            doc_class = 

        return similarities
