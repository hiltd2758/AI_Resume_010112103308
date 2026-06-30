# scoring/metrics.py

from collections import defaultdict

class ModelEvaluator:
    """Bộ công cụ phân tách dữ liệu và tính toán chỉ số đánh giá Machine Learning chuyên sâu."""
    
    @staticmethod
    def stratified_split(dataset: list[dict], train_ratio: float = 0.6):
        """Phân tách dữ liệu cân bằng theo phân lớp (Stratified Train/Test Split)"""
        dataset_by_label = defaultdict(list)
        for item in dataset:
            dataset_by_label[item["label"]].append(item)
            
        train_set, test_set = [], []
        for label, items in dataset_by_label.items():
            split_idx = int(len(items) * train_ratio)
            train_set.extend(items[:split_idx])
            test_set.extend(items[split_idx:])
        return train_set, test_set

    @staticmethod
    def evaluate(y_true, y_pred, classes):
        """Tính toán ma trận chỉ số: Accuracy, Precision, Recall, F1-Score"""
        report = {}
        correct = sum(1 for t, p in zip(y_true, y_pred) if t == p)
        accuracy = correct / len(y_true) if y_true else 0
        
        for c in classes:
            tp = sum(1 for t, p in zip(y_true, y_pred) if t == c and p == c)
            fp = sum(1 for t, p in zip(y_true, y_pred) if t != c and p == c)
            fn = sum(1 for t, p in zip(y_true, y_pred) if t == c and p != c)
            
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            
            report[c] = {"precision": precision, "recall": recall, "f1": f1, "support": y_true.count(c)}
            
        return accuracy, report