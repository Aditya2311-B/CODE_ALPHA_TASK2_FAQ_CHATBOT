import pytest
from chatbot.preprocessing import TextPreprocessor

@pytest.fixture
def preprocessor():
    return TextPreprocessor()

def test_clean_text(preprocessor):
    raw_text = "What IS Deep-Learning?"
    cleaned = preprocessor.clean_text(raw_text)
    # Check lowercasing and punctuation removal, keeping words and spaces
    assert cleaned == "what is deep learning"

def test_preprocess(preprocessor):
    raw_text = "What is Machine Learning?"
    tokens = preprocessor.preprocess(raw_text)
    # Check stopword removal (what, is) and lemmatization/cleanup
    assert "machine" in tokens
    assert "learning" in tokens
    assert "is" not in tokens
    assert "what" not in tokens

def test_preprocess_to_string(preprocessor):
    raw_text = "Python is the best!"
    processed_string = preprocessor.preprocess_to_string(raw_text)
    assert processed_string == "python best"

def test_empty_input(preprocessor):
    assert preprocessor.clean_text("") == ""
    assert preprocessor.preprocess("") == []
    assert preprocessor.preprocess_to_string(None) == ""
