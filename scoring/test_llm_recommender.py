import unittest

from scoring.llm_recommender import (
    _extract_json_text,
    _normalize_llm_result,
    build_prompt,
)


class TestLlmRecommender(unittest.TestCase):
    def test_extract_json_text_removes_code_fence(self):
        raw = '```json\n{"final_score": 85, "pros": "Good", "cons": "None"}\n```'
        self.assertEqual(
            _extract_json_text(raw),
            '{"final_score": 85, "pros": "Good", "cons": "None"}',
        )

    def test_extract_json_text_extracts_json_from_extra_text(self):
        raw = 'Response:\n```json\n{"final_score": 90}\n```\nThank you.'
        self.assertEqual(_extract_json_text(raw), '{"final_score": 90}')

    def test_normalize_llm_result_fallbacks_to_rule_score(self):
        result = _normalize_llm_result({"final_score": None}, 72.5)
        self.assertEqual(result["final_score"], 72.5)
        self.assertEqual(result["recommendation"], "Sử dụng điểm rule-based do LLM chưa trả về score hợp lệ.")
        self.assertEqual(result["interview_questions"], [])

    def test_normalize_llm_result_converts_interview_questions_string(self):
        result = _normalize_llm_result(
            {"final_score": 80, "interview_questions": "Hỏi về Python."},
            50,
        )
        self.assertEqual(result["final_score"], 80)
        self.assertEqual(result["interview_questions"], ["Hỏi về Python."])

    def test_build_prompt_serializes_cv_skills_list(self):
        prompt = build_prompt(
            job_description="Build web app",
            cv_skills=["Python", "Django"],
            cv_years=3,
            cv_text="Candidate has 3 years of backend experience.",
            rule_score=85,
        )
        self.assertIn("Python, Django", prompt)
        self.assertIn("3 năm", prompt)
        self.assertIn("Build web app", prompt)


if __name__ == "__main__":
    unittest.main()
