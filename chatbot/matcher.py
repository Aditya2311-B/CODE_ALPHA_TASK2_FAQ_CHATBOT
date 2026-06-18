import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from chatbot.preprocessing import TextPreprocessor

class FAQMatcher:
    def __init__(self, vectorizer, threshold=0.35):
        """
        FAQMatcher compares query vectors with cached FAQ vectors.
        vectorizer: An instance of FAQVectorizer containing fitted TF-IDF matrix.
        threshold: Minimum cosine similarity score (default 0.35).
        """
        self.vectorizer = vectorizer
        self.preprocessor = TextPreprocessor()
        self.threshold = threshold

    def match(self, query):
        """
        Matches user query to the best FAQ and returns results.
        """
        # Fallback if no vectorizer matrix or empty database
        if not query or self.vectorizer.tfidf_matrix is None or self.vectorizer.tfidf_matrix.shape[0] == 0:
            return {
                "matched": False,
                "id": None,
                "question": None,
                "answer": "Sorry, I couldn't find any FAQs in the database.",
                "confidence": 0.0,
                "matched_keywords": [],
                "suggestions": []
            }

        # Transform query to vector
        query_vector = self.vectorizer.transform_query(query)
        if query_vector is None:
            return {
                "matched": False,
                "id": None,
                "question": None,
                "answer": "Sorry, I couldn't process your question.",
                "confidence": 0.0,
                "matched_keywords": [],
                "suggestions": []
            }

        # Calculate cosine similarities
        similarities = cosine_similarity(query_vector, self.vectorizer.tfidf_matrix).flatten()
        
        # Sort indices descending
        sorted_indices = np.argsort(similarities)[::-1]
        best_idx = sorted_indices[0]
        best_score = float(similarities[best_idx])
        
        # Get details of best match
        best_faq = self.vectorizer.faqs[best_idx]
        best_question = best_faq.question if hasattr(best_faq, 'question') else best_faq.get('question', '')
        best_answer = best_faq.answer if hasattr(best_faq, 'answer') else best_faq.get('answer', '')
        best_id = best_faq.id if hasattr(best_faq, 'id') else best_faq.get('id', None)
        
        # Extract matching keywords for frontend highlighting
        # We compare lowercase words to identify overlaps
        query_tokens = set(self.preprocessor.preprocess(query))
        faq_tokens = set(self.preprocessor.preprocess(best_question))
        matched_keywords = list(query_tokens.intersection(faq_tokens))

        # Collect top 3 suggestions (other candidates with similarity > 0.05)
        # If the best match is below threshold, suggestions are drawn from all indices
        # If the best match is accepted, suggestions are drawn from indices [1:]
        suggestions = []
        suggestion_candidates = sorted_indices if best_score < self.threshold else sorted_indices[1:]
        
        for idx in suggestion_candidates:
            if len(suggestions) >= 3:
                break
            score = float(similarities[idx])
            # Only suggest things with some small relevance
            if score > 0.05:
                faq_item = self.vectorizer.faqs[idx]
                q = faq_item.question if hasattr(faq_item, 'question') else faq_item.get('question', '')
                suggestions.append({
                    "id": faq_item.id if hasattr(faq_item, 'id') else faq_item.get('id', None),
                    "question": q,
                    "confidence": score
                })
        
        # Fallback if below threshold
        if best_score < self.threshold:
            return {
                "matched": False,
                "id": None,
                "question": None,
                "answer": "Sorry, I couldn't find an answer for that question.",
                "confidence": best_score,
                "matched_keywords": [],
                "suggestions": suggestions
            }

        return {
            "matched": True,
            "id": best_id,
            "question": best_question,
            "answer": best_answer,
            "confidence": best_score,
            "matched_keywords": matched_keywords,
            "suggestions": suggestions
        }
