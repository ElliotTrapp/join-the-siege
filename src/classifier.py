import logging
import os
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from openai import OpenAI
from src.config import config
from src.util.clean_data import clean_data

model = SentenceTransformer(config.MODEL)

class Classifier:
    """
    Class to hold all the logic and data relating to translating 
    clean data in the form of a str to a document class + confidence level
    """
    def __init__(self):
        """
        Initialize the classifier and pull the initial set of reference
        embeddings from the config
        """
        self.reference_embeddings = config.REFERENCE_EMBEDDINGS

    def get_labels(self) -> list:
        """Return just the labels"""
        return list(self.reference_embeddings.keys())

    def get_embeddings(self) -> dict:
        """Return the labels and their embeddings"""
        return self.reference_embeddings

    def get_embedding_from_llm(self, label: str) -> str:
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

    def add_label(self, label: str, embedding: str = None) -> None:
        """
        Add a new label. If an embedding is provided, associate it with the label,
        otherwise, ask OpenAI for an embedding
        """
        if not embedding:
            try:
                embedding = self.get_embedding_from_llm(label)
            except Exception as e:
                raise Exception(f'failed to generate a new embedding from OpenAI, {e}')
        self.reference_embeddings[label] = clean_data(embedding)

    def remove_label(self, label: str) -> None:
        """Remove a label and its embedding"""
        try:
            self.reference_embeddings.pop[label]
        except Exception as e:
            raise Exception(f'failed to remove {label} from config, {e}')

    def classify(self, parsed_doc: str) -> tuple[str, float]:
        """Classify a parsed doc in the form of a str"""
        results = []
        # Set the default confidence to 1.0 and class to `unknown`
        # if we can't find a match we're "certain" that we don't know
        confidence = 1.0
        doc_class = 'unknown'
        # The embeddings to test against
        reference_embeddings = model.encode(list(self.reference_embeddings.values()))
        # Convert the document to an embedding
        check_embedding = model.encode([parsed_doc])
        # Compare each pair and add their cosine similarities to the results
        for label, embedding in zip(self.reference_embeddings.keys(), reference_embeddings):
            logging.info(f'comparing {len(check_embedding)} long embedding with {len(embedding)} long embedding to see if doc is a {label}')
            # model.similarity uses cosine similarity under the hood, which ignores length/normalizes for us
            similarity = model.similarity(check_embedding, embedding).item()
            result = (label, similarity)
            results.append(result)
        # Sort the results in descending confidence order
        results.sort(key=lambda result: result[0], reverse=True)
        logging.info(f'all results: {results}')
        top_result = results[0]
        # If our best result isn't at least config.MIN_CONFIDENCE good, we aren't sure
        if top_result[0] > config.MIN_CONFIDENCE:
            doc_class, confidence = top_result
            logging.info(f'doc was identified as a {doc_class} with confidence of {confidence}')
        return doc_class, confidence
