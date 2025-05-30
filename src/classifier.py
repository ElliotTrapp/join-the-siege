import logging
import os
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from openai import OpenAI
from src.config import config
from src.util.clean_data import clean_data

model = SentenceTransformer(config.MODEL)

class Classifier:
    def __init__(self):
        self.reference_embeddings = config.REFERENCE_EMBEDDINGS

    def get_labels(self):
        return list(self.reference_embeddings.keys())

    def get_embeddings(self):
        return self.reference_embeddings

    def get_embedding_from_llm(self, label: str):
        """Query LLM for a new embedding"""
        # loading variables from .env file
        load_dotenv()
        if not os.environ.get('OPENAI_API_KEY'):
            raise Exception(f'OPENAI_API_KEY environment variable needs to be set to query LLM')
        client = OpenAI()

        prompt = f"""
        List the top 20 common terms and keywords typically uniquely found in a {label} document. Provide the list as a space-separated list.
        Do not number the list in anyway. All terms should be lowercase. Do not include any newline characters. List each term only once.
        Do not include words that are generic and not specific to a {label} document context.
        """

        response = client.responses.create(
            model="gpt-3.5-turbo",
            input=prompt
        )

        embedding = response.output_text
        logging.info(f'created embedding {embedding} for label {label}')
        return embedding

    def add_label(self, label: str, embedding: str = None):
        if not embedding:
            try:
                embedding = self.get_embedding_from_llm(label)
            except Exception as e:
                raise Exception(f'failed to generate a new embedding from OpenAI, {e}')
        self.reference_embeddings[label] = clean_data(embedding)

    def remove_label(self, label: str):
        try:
            self.reference_embeddings.pop[label]
        except Exception as e:
            raise Exception(f'failed to remove {label} from config, {e}')

    def classify(self, parsed_doc: str):
        results = []
        confidence = 1.0
        doc_class = 'unknown'
        reference_embeddings = model.encode(list(self.reference_embeddings.values()))
        check_embedding = model.encode([parsed_doc])
        for label, embedding in zip(self.reference_embeddings.keys(), reference_embeddings):
            logging.info(f'comparing {len(check_embedding)} long embedding with {len(embedding)} long embedding to see if doc is a {label}')
            similarity = model.similarity(check_embedding, embedding).item()
            result = (similarity, label)
            results.append(result)
        results.sort(key=lambda result: result[0], reverse=True)
        logging.info(f'all results: {results}')
        top_result = results[0]
        if top_result[0] > config.MIN_CONFIDENCE:
            confidence, doc_class = top_result
            logging.info(f'doc was identified as a {doc_class} with confidence of {confidence}')
        return doc_class, confidence
