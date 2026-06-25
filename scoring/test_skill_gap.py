import unittest

from parsing.skill_extractor import extract_skills
from scoring.rule_based_scorer import score_skills
from scoring.skill_gap import analyze_skill_gap, normalize_skills


class TestSkillGap(unittest.TestCase):
    def assertCoverage(self, result, expected):
        self.assertEqual(result["coverage_score"], expected)
        self.assertEqual(result["skill_gap_score"], expected)
        self.assertEqual(result["coverage_percentage"], expected)

    def test_exact_match(self):
        result = analyze_skill_gap(
            ["Python", "SQL", "Docker", "Git", "Pandas"],
            ["Python", "SQL", "Docker", "Git", "Pandas"],
        )

        self.assertCoverage(result, 100.0)
        self.assertEqual(result["missing_skills"], [])
        self.assertEqual(result["matched_count"], 5)

    def test_case_insensitive_and_whitespace(self):
        result = analyze_skill_gap([" python ", "SQL", "git"], ["PYTHON", " sql ", "Git"])

        self.assertCoverage(result, 100.0)
        self.assertEqual(result["matched_skills"], ["Python", "SQL", "Git"])

    def test_front_end_aliases(self):
        result = analyze_skill_gap(["HTML5", "CSS3", "wordpress"], ["HTML", "CSS", "WordPress"])

        self.assertCoverage(result, 100.0)
        self.assertEqual(result["matched_skills"], ["HTML", "CSS", "WordPress"])
        self.assertEqual(result["missing_skills"], [])

    def test_other_required_aliases(self):
        result = analyze_skill_gap(
            ["NodeJS", "Fast API", "SpringBoot", "sklearn"],
            ["Node.js", "FastAPI", "Spring Boot", "scikit-learn"],
        )

        self.assertCoverage(result, 100.0)
        self.assertEqual(result["matched_skills"], ["Node.js", "FastAPI", "Spring Boot", "scikit-learn"])

    def test_partial_match(self):
        result = analyze_skill_gap(["Python", "SQL"], ["Python", "SQL", "Docker", "Git"])

        self.assertCoverage(result, 50.0)
        self.assertEqual(result["missing_skills"], ["Docker", "Git"])
        self.assertEqual(result["missing_percent"], 50.0)

    def test_duplicates_are_removed(self):
        result = analyze_skill_gap(["Python", "Python", "SQL"], ["Python", "SQL", "SQL"])

        self.assertCoverage(result, 100.0)
        self.assertEqual(result["job_skills_total"], 2)
        self.assertEqual(result["cv_skills_normalized"], ["Python", "SQL"])
        self.assertEqual(result["job_skills_normalized"], ["Python", "SQL"])

    def test_java_does_not_match_javascript(self):
        result = analyze_skill_gap(["Java"], ["JavaScript"])

        self.assertCoverage(result, 0.0)
        self.assertEqual(result["matched_skills"], [])
        self.assertEqual(result["missing_skills"], ["JavaScript"])
        self.assertEqual(result["extra_skills"], ["Java"])

    def test_empty_and_none_inputs_do_not_crash(self):
        result = analyze_skill_gap(None, ["Python", "SQL"])

        self.assertCoverage(result, 0.0)
        self.assertEqual(result["matched_skills"], [])
        self.assertEqual(result["missing_skills"], ["Python", "SQL"])
        self.assertEqual(result["cv_skills_normalized"], [])
        self.assertEqual(result["status"], "ok")

    def test_empty_job_has_documented_status(self):
        result = analyze_skill_gap(["Python"], [])

        self.assertCoverage(result, 100.0)
        self.assertEqual(result["missing_percent"], 0.0)
        self.assertEqual(result["job_skills_total"], 0)
        self.assertEqual(result["recommendations"], [])
        self.assertEqual(result["status"], "no_job_skills")
        self.assertIn("coverage", result["note"])

    def test_cv_text_enrichment(self):
        result = analyze_skill_gap(
            cv_skills=[],
            job_skills=["HTML", "CSS", "WordPress"],
            cv_text="Đã xây dựng website bằng HTML5, CSS3 và WordPress.",
        )

        self.assertCoverage(result, 100.0)
        self.assertEqual(result["cv_skills_normalized"], ["HTML", "CSS", "WordPress"])

    def test_job_text_enrichment(self):
        result = analyze_skill_gap(
            cv_skills=["Python", "Docker"],
            job_skills=[],
            job_text="Ứng viên cần Python và Docker.",
        )

        self.assertCoverage(result, 100.0)
        self.assertEqual(result["job_skills_normalized"], ["Python", "Docker"])
        self.assertEqual(result["status"], "ok")

    def test_recommendations_only_for_missing_skills(self):
        result = analyze_skill_gap(["Python"], ["Python", "Docker", "Git"])

        self.assertEqual([item["skill"] for item in result["recommendations"]], ["Docker", "Git"])
        self.assertEqual(len(result["recommendations"]), 2)
        for item in result["recommendations"]:
            self.assertEqual(item["priority"], "high")
            self.assertTrue(item["recommendation"])
            self.assertTrue(item["suggested_evidence"])

    def test_output_schema_contains_old_and_new_keys(self):
        result = analyze_skill_gap(["HTML5"], ["HTML"])
        required_keys = {
            "matched_skills",
            "missing_skills",
            "extra_skills",
            "additional_skills",
            "matched_skills_display",
            "missing_skills_display",
            "additional_skills_display",
            "matched_count",
            "gap_count",
            "job_skills_total",
            "skill_gap_score",
            "coverage_score",
            "coverage_percentage",
            "matched_percentage",
            "missing_percent",
            "gap_percentage",
            "recommendations",
            "cv_skills_normalized",
            "job_skills_normalized",
            "status",
            "note",
        }
        self.assertTrue(required_keys.issubset(result.keys()))

    def test_normalize_skills_keeps_first_reasonable_order(self):
        self.assertEqual(
            normalize_skills([" HTML5 ", "html", "CSS3", "Word Press"]),
            ["HTML", "CSS", "WordPress"],
        )

    def test_parser_uses_safe_boundaries_and_aliases(self):
        skills = extract_skills("Frontend: HTML5, CSS3, Word Press. Backend: JavaScript.")

        self.assertIn("HTML", skills)
        self.assertIn("CSS", skills)
        self.assertIn("WordPress", skills)
        self.assertIn("JavaScript", skills)
        self.assertNotIn("Java", skills)

    def test_rule_based_skill_score_uses_same_normalization(self):
        score = score_skills(
            ["Python", "SQL", "Docker", "Git", "Pandas"],
            ["python", "sql", "docker", "git", "pandas"],
        )

        self.assertEqual(score, 50.0)

    def test_legacy_no_match_zero_coverage(self):
        result = analyze_skill_gap(["Java", "Kotlin", "Gradle"], ["Python", "SQL", "Docker"])

        self.assertCoverage(result, 0.0)
        self.assertEqual(result["missing_percent"], 100.0)
        self.assertEqual(result["gap_count"], 3)
        self.assertEqual(result["matched_count"], 0)
        self.assertEqual(result["matched_skills"], [])
        self.assertEqual(result["missing_skills"], ["Python", "SQL", "Docker"])
        self.assertEqual(result["additional_skills"], ["Java", "Kotlin", "Gradle"])

    def test_legacy_over_qualified_extra_skills_do_not_reduce_score(self):
        result = analyze_skill_gap(
            ["Python", "SQL", "Docker", "Kubernetes", "AWS", "GCP"],
            ["Python", "SQL"],
        )

        self.assertCoverage(result, 100.0)
        self.assertEqual(result["gap_count"], 0)
        self.assertEqual(result["matched_count"], 2)
        self.assertEqual(result["extra_skills"], ["Docker", "Kubernetes", "AWS", "GCP"])

    def test_legacy_both_empty_and_both_none(self):
        for cv_skills, job_skills in [([], []), (None, None)]:
            result = analyze_skill_gap(cv_skills, job_skills)
            self.assertCoverage(result, 100.0)
            self.assertEqual(result["gap_count"], 0)
            self.assertEqual(result["matched_count"], 0)
            self.assertEqual(result["job_skills_total"], 0)
            self.assertEqual(result["matched_skills"], [])
            self.assertEqual(result["missing_skills"], [])
            self.assertEqual(result["additional_skills"], [])

    def test_legacy_none_and_non_string_values_are_filtered(self):
        result = analyze_skill_gap(["Python", None, "SQL", 123, 45.6, True], ["Python", None, "SQL"])

        self.assertCoverage(result, 100.0)
        self.assertEqual(result["matched_skills"], ["Python", "SQL"])
        self.assertEqual(result["cv_skills_normalized"], ["Python", "SQL"])
        self.assertEqual(result["job_skills_normalized"], ["Python", "SQL"])

    def test_legacy_special_characters_in_unknown_skill_names(self):
        result = analyze_skill_gap(["C++", "C#", "Node.js"], ["c++", "c#", "node.js"])

        self.assertCoverage(result, 100.0)
        self.assertEqual(result["matched_count"], 3)
        self.assertEqual({skill.casefold() for skill in result["matched_skills"]}, {"c++", "c#", "node.js"})

    def test_legacy_percentage_math_and_rounding(self):
        result = analyze_skill_gap(["Python"], ["Python", "SQL", "AWS"])

        self.assertCoverage(result, 33.33)
        self.assertEqual(result["missing_percent"], 66.67)
        self.assertAlmostEqual(result["coverage_percentage"] + result["gap_percentage"], 100.0, places=1)

    def test_legacy_counts_match_list_lengths(self):
        result = analyze_skill_gap(["Python", "SQL", "Docker"], ["Python", "AWS", "Kubernetes"])

        self.assertEqual(result["matched_count"], len(result["matched_skills"]))
        self.assertEqual(result["gap_count"], len(result["missing_skills"]))
        self.assertEqual(
            result["job_skills_total"],
            len(result["matched_skills"]) + len(result["missing_skills"]),
        )

    def test_legacy_large_skill_lists(self):
        cv_skills = [f"Skill_{index}" for index in range(100)]
        job_skills = [f"Skill_{index}" for index in range(50, 150)]

        result = analyze_skill_gap(cv_skills, job_skills)

        self.assertEqual(result["matched_count"], 50)
        self.assertEqual(result["gap_count"], 50)
        self.assertCoverage(result, 50.0)

    def test_legacy_realistic_junior_developer_scenario(self):
        result = analyze_skill_gap(
            ["Python", "Git", "HTML", "CSS", "SQL"],
            ["Python", "JavaScript", "React", "Node.js", "SQL", "Docker", "AWS"],
        )

        self.assertEqual(result["matched_count"], 2)
        self.assertEqual(result["gap_count"], 5)
        self.assertCoverage(result, 28.57)

    def test_legacy_realistic_senior_developer_scenario(self):
        result = analyze_skill_gap(
            ["Python", "SQL", "Docker", "Kubernetes", "AWS", "Git", "FastAPI", "PostgreSQL", "CI/CD", "Terraform"],
            ["Python", "SQL", "Docker", "Kubernetes", "AWS", "FastAPI"],
        )

        self.assertCoverage(result, 100.0)
        self.assertEqual(result["matched_count"], 6)
        self.assertEqual(result["gap_count"], 0)

    def test_legacy_recommendation_fallback_for_unmapped_skill(self):
        result = analyze_skill_gap([], ["Elasticsearch"])

        self.assertEqual(result["gap_count"], 1)
        self.assertEqual(len(result["recommendations"]), 1)
        self.assertEqual(result["recommendations"][0]["skill"], "Elasticsearch")
        self.assertIn("Elasticsearch", result["recommendations"][0]["recommendation"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
