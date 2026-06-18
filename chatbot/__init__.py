from chatbot.preprocessing import TextPreprocessor
from chatbot.vectorizer import FAQVectorizer
from chatbot.matcher import FAQMatcher
from chatbot.utils import download_nltk_resources

# Singleton-style instances for global sharing
vectorizer = FAQVectorizer()
matcher = FAQMatcher(vectorizer)

def initialize_chatbot(db_faqs):
    """
    Called on startup to pre-download NLTK and fit/cache the vectors.
    """
    download_nltk_resources()
    vectorizer.fit_faqs(db_faqs)
