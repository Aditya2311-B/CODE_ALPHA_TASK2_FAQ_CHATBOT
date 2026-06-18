import pytest
from chatbot.utils import download_nltk_resources

@pytest.fixture(scope="session", autouse=True)
def setup_nltk():
    """
    Session-scoped fixture to pre-download all NLTK requirements.
    Runs automatically before any tests start.
    """
    download_nltk_resources()
