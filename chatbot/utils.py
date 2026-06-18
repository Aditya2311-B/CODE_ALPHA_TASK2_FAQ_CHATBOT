import ssl
import nltk
import logging

logger = logging.getLogger(__name__)

# Bypassing SSL verification for macOS environments where Python certificates aren't installed
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

def download_nltk_resources():
    """
    Safely download NLTK datasets required for preprocessing.
    Checks if resources exist before downloading to optimize start times.
    """
    resources = {
        'tokenizers/punkt': 'punkt',
        'corpora/stopwords': 'stopwords',
        'corpora/wordnet': 'wordnet',
        'corpora/omw-1.4': 'omw-1.4'
    }
    
    for path, name in resources.items():
        try:
            nltk.data.find(path)
            logger.info(f"NLTK resource '{name}' already exists.")
        except LookupError:
            logger.info(f"Downloading NLTK resource '{name}'...")
            try:
                nltk.download(name, quiet=True)
            except Exception as e:
                logger.error(f"Failed to download NLTK resource '{name}': {e}")
                # Try downloading anyway as fallback
                try:
                    nltk.download(name)
                except Exception:
                    pass
