# scoring/classifier.py

import math
import re
from collections import Counter

class NaiveBayesClassifier:
    """
    Phân loại văn bản bằng thuật toán Multinomial Naïve Bayes sử dụng kỹ thuật
    Làm mịn Laplace (Laplace Smoothing) để tránh hiện tượng xác suất bằng 0.
    """
    def __init__(self, smoothing: float = 1.0):
        self.smoothing = smoothing
        self.classes = []
        self.priors = {}
        self.feature_counts = {}
        self.totals = {}
        self.vocab = set()

    def _tokenize(self, text: str) -> list[str]:
        """Tiền xử lý văn bản, chuẩn hóa regex và lọc token nhiễu."""
        if not text:
            return []
        normalized = re.sub(r"[^0-9a-zA-Z\u00C0-\u017F]+", " ", text.lower())
        return [token for token in normalized.split() if len(token) > 1]

    def fit(self, train_data: list[dict]):
        """ Huấn luyện mô hình (Tính toán các tham số Prior và Likelihood) """
        total_docs = len(train_data)
        self.classes = list(set(item["label"] for item in train_data))
        class_counts = Counter(item["label"] for item in train_data)
        
        for c in self.classes:
            self.priors[c] = class_counts[c] / total_docs
            self.feature_counts[c] = Counter()
            self.totals[c] = 0
            
        for item in train_data:
            c = item["label"]
            tokens = self._tokenize(" ".join(item["skills"]))
            self.feature_counts[c].update(tokens)
            self.vocab.update(tokens)
            
        for c in self.classes:
            self.totals[c] = sum(self.feature_counts[c].values())

    def _score_class(self, skills: list[str], c: str) -> float:
        """ Tính điểm Log-Likelihood để tránh lỗi tràn số dưới (Arithmetic Underflow) """
        tokens = self._tokenize(" ".join(skills))
        if not tokens:
            return float("-inf")

        score = math.log(self.priors.get(c, 1e-9))
        vocab_size = max(1, len(self.vocab))
        total_tokens_in_class = self.totals.get(c, 0) + self.smoothing * vocab_size

        for token in tokens:
            count = self.feature_counts.get(c, Counter()).get(token, 0) + self.smoothing
            score += math.log(count / total_tokens_in_class)

        return score

    def predict(self, skills: list[str]) -> str:
        """ Dự đoán nhãn phân lớp có xác suất hậu nghiệm (Posterior) cao nhất """
        return max(self.classes, key=lambda c: self._score_class(skills, c))