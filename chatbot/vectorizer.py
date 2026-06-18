import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from chatbot.preprocessing import TextPreprocessor

class FAQVectorizer:
    def __init__(self):
        self.preprocessor = TextPreprocessor()
        # Custom token_pattern to keep words that are 2+ letters (already filtered by preprocessor)
        self.vectorizer = TfidfVectorizer(token_pattern=r'(?u)\b\w+\b')
        self.tfidf_matrix = None
        self.faq_ids = []
        self.faqs = []

    def fit_faqs(self, faqs):
        """
        Fits the TF-IDF vectorizer on the preprocessed questions from the database/list.
        faqs: List of dicts or SQLAlchemy models with 'id', 'question', and 'answer'.
        """
        if not faqs:
            self.tfidf_matrix = None
            self.faq_ids = []
            self.faqs = []
            return

        self.faqs = faqs
        self.faq_ids = [faq.id if hasattr(faq, 'id') else faq.get('id') for faq in faqs]
        
        # Gather preprocessed questions
        preprocessed_corpus = []
        for faq in faqs:
            q = faq.question if hasattr(faq, 'question') else faq.get('question', '')
            preprocessed_corpus.append(self.preprocessor.preprocess_to_string(q))
            
        # Fit vectorizer and build tfidf matrix
        self.tfidf_matrix = self.vectorizer.fit_transform(preprocessed_corpus)

    def transform_query(self, query):
        """
        Transforms a user query into a TF-IDF vector.
        """
        if self.tfidf_matrix is None:
            # Return empty / None or raise error. Let's return None to handle gracefully.
            return None
            
        preprocessed_q = self.preprocessor.preprocess_to_string(query)
        return self.vectorizer.transform([preprocessed_q])

    def get_feature_names(self):
        """
        Returns feature names (vocabulary) of the TF-IDF vectorizer.
        """
        if self.vectorizer and hasattr(self.vectorizer, 'get_feature_names_out'):
            return self.vectorizer.get_feature_names_out()
        return []
