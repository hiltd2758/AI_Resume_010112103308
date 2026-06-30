# run_evaluation.py

import time
from scoring.test_dataset import DATASET
from scoring.classifier import NaiveBayesClassifier
from scoring.metrics import ModelEvaluator

def main():
    print("=" * 70)
    print("  EVALUATION PIPELINE: MULTINOMIAL NAÏVE BAYES SYSTEM  ")
    print("=" * 70)
    
    start_time = time.time()
    
    # 1. Triển khai phân tách dữ liệu tầng cân bằng độc lập
    evaluator = ModelEvaluator()
    train_set, test_set = evaluator.stratified_split(DATASET, train_ratio=0.6)
    
    print(f"[*] Trạng thái dữ liệu: Gom cụm thành công 4 phân lớp nghề nghiệp.")
    print(f"[*] Tập Huấn luyện (Train): {len(train_set)} mẫu | Tập Kiểm thử (Test): {len(test_set)} mẫu.")
    
    # 2. Khởi tạo và Huấn luyện mô hình từ module phân tách
    classifier = NaiveBayesClassifier(smoothing=1.0)
    classifier.fit(train_set)
    print(f"[*] Không gian đặc trưng (Vocabulary Size): {len(classifier.vocab)} đặc trưng duy nhất.")
    
    # 3. Dự đoán trên tập dữ liệu Test độc lập
    y_true = [item["label"] for item in test_set]
    y_pred = [classifier.predict(item["skills"]) for item in test_set]
    
    # 4. Đánh giá hiệu năng toán học từ module đo lường
    accuracy, report = evaluator.evaluate(y_true, y_pred, classifier.classes)
    execution_time = (time.time() - start_time) * 1000
    
    # HIỂN THỊ BÁO CÁO KẾT QUẢ ĐỊNH DẠNG CHUYÊN NGHIỆP (ACADEMIC REPORT)
    print("\n" + "=" * 22 + " CLASSIFICATION REPORT " + "=" * 23)
    print(f"Độ chính xác toàn cục (Overall Accuracy): {accuracy * 100:.2f}%")
    print(f"Thời gian tính toán hệ thống (Latency): {execution_time:.2f} ms")
    print("-" * 68)
    print(f"{'Vị trí tuyển dụng':<18} | {'Precision':<10} | {'Recall':<10} | {'F1-Score':<10} | {'Support':<8}")
    print("-" * 68)
    
    macro_p, macro_r, macro_f = 0, 0, 0
    for cls in sorted(classifier.classes):
        metrics = report[cls]
        macro_p += metrics["precision"]
        macro_r += metrics["recall"]
        macro_f += metrics["f1"]
        print(f"{cls:<18} | {metrics['precision']*100:<9.2f}% | {metrics['recall']*100:<9.2f}% | {metrics['f1']*100:<9.2f}% | {metrics['support']:<8}")
        
    num_classes = len(classifier.classes)
    print("-" * 68)
    print(f"{'Macro Average':<18} | {(macro_p/num_classes)*100:<9.2f}% | {(macro_r/num_classes)*100:<9.2f}% | {(macro_f/num_classes)*100:<9.2f}% | {len(y_true):<8}")
    print("=" * 68)

if __name__ == "__main__":
    main()