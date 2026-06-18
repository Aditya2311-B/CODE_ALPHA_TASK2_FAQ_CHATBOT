import string
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer, PorterStemmer

class TextPreprocessor:
    def __init__(self, use_stemming=False):
        self.lemmatizer = WordNetLemmatizer()
        self.stemmer = PorterStemmer()
        self.use_stemming = use_stemming
        
        # Load stopwords safely
        try:
            self.stop_words = set(stopwords.words('english'))
        except Exception:
            self.stop_words = set()

    def clean_text(self, text):
        """
        Cleans input text by lowercasing and removing punctuation/special characters.
        """
        if not text:
            return ""
        
        # Lowercase
        text = text.lower()
        
        # Remove punctuation and special characters (keep words and spaces)
        text = re.sub(r'[^\w\s-]', '', text)
        
        # Replace dashes or underscores with spaces
        text = text.replace('-', ' ').replace('_', ' ')
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

    def preprocess(self, text):
        """
        Performs full preprocessing: clean -> tokenize -> remove stopwords -> lemmatize/stem.
        Returns a list of tokens.
        """
        cleaned = self.clean_text(text)
        if not cleaned:
            return []
        
        # Tokenize
        try:
            tokens = word_tokenize(cleaned)
        except Exception:
            # Simple whitespace fallback if NLTK tokenizer fails
            tokens = cleaned.split()
        
        # Remove stopwords and short words (length < 2, except single letters if they are key)
        tokens = [word for word in tokens if word not in self.stop_words and len(word) >= 2]
        
        # Lemmatization
        tokens = [self.lemmatizer.lemmatize(word) for word in tokens]
        
        # Optional Stemming
        if self.use_stemming:
            tokens = [self.stemmer.stem(word) for word in tokens]
            
        return tokens

    def preprocess_to_string(self, text):
        """
        Returns the preprocessed tokens joined back into a string, suitable for TF-IDF.
        """
        tokens = self.preprocess(text)
        return " ".join(tokens)
