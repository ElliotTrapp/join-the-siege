
import re
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords

nltk.download("wordnet")
nltk.download("stopwords")

stop_words = set(stopwords.words('english'))
wnl = WordNetLemmatizer()

def clean_data(data: str) -> str:
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