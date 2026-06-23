"""
Unit Tests for Skill-Gap Analysis Module

Tests the analyze_skill_gap() function with comprehensive coverage:
- Happy path: Perfect match, partial match, no match
- Edge cases: Empty lists, None values, duplicates
- Data normalization: Whitespace, case-insensitivity, special characters
- Output validation: Type checking, range validation

Run: python -m unittest scoring.test_skill_gap -v
Or:  python -m unittest scoring.test_skill_gap.TestSkillGap -v
Or:  python scoring/test_skill_gap.py
"""

import unittest
from scoring.skill_gap import analyze_skill_gap


class TestSkillGap(unittest.TestCase):
    """Unit tests for analyze_skill_gap function."""
    
    # ========================================================================
    # GROUP 1: Happy Path Tests
    # ========================================================================
    
    def test_perfect_match_all_skills(self):
        """Test when CV has all required skills (100% coverage)."""
        result = analyze_skill_gap(
            cv_skills=["Python", "SQL", "Docker"],
            job_skills=["Python", "SQL", "Docker"]
        )
        self.assertEqual(result["gap_percentage"], 0.0)
        self.assertEqual(result["matched_percentage"], 100.0)
        self.assertEqual(result["coverage_percentage"], 100.0)
        self.assertEqual(result["gap_count"], 0)
        self.assertEqual(result["matched_count"], 3)
        self.assertEqual(sorted(result["matched_skills"]), ["docker", "python", "sql"])
        self.assertEqual(result["missing_skills"], [])
        self.assertEqual(result["additional_skills"], [])
    
    def test_partial_match_half_coverage(self):
        """Test when CV has 50% of required skills."""
        result = analyze_skill_gap(
            cv_skills=["Python", "SQL", "Git", "Docker"],
            job_skills=["Python", "SQL", "AWS", "Kubernetes"]
        )
        self.assertEqual(result["gap_count"], 2)
        self.assertEqual(result["matched_count"], 2)
        self.assertEqual(result["job_skills_total"], 4)
        self.assertEqual(result["gap_percentage"], 50.0)
        self.assertEqual(result["matched_percentage"], 50.0)
        self.assertEqual(result["coverage_percentage"], 50.0)
        self.assertEqual(sorted(result["matched_skills"]), ["python", "sql"])
        self.assertEqual(sorted(result["missing_skills"]), ["aws", "kubernetes"])
        self.assertEqual(sorted(result["additional_skills"]), ["docker", "git"])
    
    def test_no_match_zero_coverage(self):
        """Test when CV has no required skills (0% coverage)."""
        result = analyze_skill_gap(
            cv_skills=["Java", "Kotlin", "Gradle"],
            job_skills=["Python", "SQL", "Docker"]
        )
        self.assertEqual(result["gap_percentage"], 100.0)
        self.assertEqual(result["matched_percentage"], 0.0)
        self.assertEqual(result["coverage_percentage"], 0.0)
        self.assertEqual(result["gap_count"], 3)
        self.assertEqual(result["matched_count"], 0)
        self.assertEqual(result["matched_skills"], [])
        self.assertEqual(sorted(result["missing_skills"]), ["docker", "python", "sql"])
        self.assertEqual(sorted(result["additional_skills"]), ["gradle", "java", "kotlin"])
    
    def test_over_qualified_additional_skills(self):
        """Test when candidate has more skills than required."""
        result = analyze_skill_gap(
            cv_skills=["Python", "SQL", "Docker", "Kubernetes", "AWS", "GCP"],
            job_skills=["Python", "SQL"]
        )
        self.assertEqual(result["gap_percentage"], 0.0)
        self.assertEqual(result["matched_percentage"], 100.0)
        self.assertEqual(result["gap_count"], 0)
        self.assertEqual(result["matched_count"], 2)
        self.assertEqual(sorted(result["matched_skills"]), ["python", "sql"])
        self.assertEqual(sorted(result["additional_skills"]), ["aws", "docker", "gcp", "kubernetes"])
    
    # ========================================================================
    # GROUP 2: Edge Cases - Empty/None Inputs
    # ========================================================================
    
    def test_empty_cv_skills(self):
        """Test when CV skills list is empty (candidate has no skills)."""
        result = analyze_skill_gap(
            cv_skills=[],
            job_skills=["Python", "SQL", "AWS"]
        )
        self.assertEqual(result["gap_percentage"], 100.0)
        self.assertEqual(result["matched_percentage"], 0.0)
        self.assertEqual(result["gap_count"], 3)
        self.assertEqual(result["matched_count"], 0)
        self.assertEqual(result["matched_skills"], [])
        self.assertEqual(sorted(result["missing_skills"]), ["aws", "python", "sql"])
        self.assertEqual(result["additional_skills"], [])
    
    def test_empty_job_skills(self):
        """Test when job skills list is empty (no requirements)."""
        result = analyze_skill_gap(
            cv_skills=["Python", "SQL"],
            job_skills=[]
        )
        self.assertEqual(result["gap_percentage"], 0.0)
        self.assertEqual(result["matched_percentage"], 100.0)
        self.assertEqual(result["coverage_percentage"], 100.0)
        self.assertEqual(result["gap_count"], 0)
        self.assertEqual(result["matched_count"], 0)
        self.assertEqual(result["job_skills_total"], 0)
        self.assertEqual(result["matched_skills"], [])
        self.assertEqual(result["missing_skills"], [])
        self.assertEqual(sorted(result["additional_skills"]), ["python", "sql"])
    
    def test_both_empty(self):
        """Test when both CV and job skills are empty."""
        result = analyze_skill_gap(
            cv_skills=[],
            job_skills=[]
        )
        self.assertEqual(result["gap_percentage"], 0.0)
        self.assertEqual(result["matched_percentage"], 100.0)
        self.assertEqual(result["coverage_percentage"], 100.0)
        self.assertEqual(result["gap_count"], 0)
        self.assertEqual(result["matched_count"], 0)
        self.assertEqual(result["job_skills_total"], 0)
        self.assertEqual(result["matched_skills"], [])
        self.assertEqual(result["missing_skills"], [])
        self.assertEqual(result["additional_skills"], [])
    
    def test_none_cv_skills(self):
        """Test when CV skills is None."""
        result = analyze_skill_gap(
            cv_skills=None,
            job_skills=["Python", "SQL"]
        )
        self.assertEqual(result["gap_percentage"], 100.0)
        self.assertEqual(result["gap_count"], 2)
    
    def test_none_job_skills(self):
        """Test when job skills is None."""
        result = analyze_skill_gap(
            cv_skills=["Python", "SQL"],
            job_skills=None
        )
        self.assertEqual(result["gap_count"], 0)
        self.assertEqual(result["job_skills_total"], 0)
        self.assertEqual(result["matched_percentage"], 100.0)
        self.assertEqual(result["coverage_percentage"], 100.0)
    
    def test_both_none(self):
        """Test when both CV and job skills are None."""
        result = analyze_skill_gap(
            cv_skills=None,
            job_skills=None
        )
        self.assertEqual(result["gap_count"], 0)
        self.assertEqual(result["matched_count"], 0)
        self.assertEqual(result["matched_percentage"], 100.0)
        self.assertEqual(result["coverage_percentage"], 100.0)
    
    # ========================================================================
    # GROUP 3: Normalization Tests
    # ========================================================================
    
    def test_case_insensitive_matching(self):
        """Test that comparison is case-insensitive."""
        result = analyze_skill_gap(
            cv_skills=["PYTHON", "SQL"],
            job_skills=["python", "sql"]
        )
        self.assertEqual(result["gap_percentage"], 0.0)
        self.assertEqual(result["matched_percentage"], 100.0)
        self.assertEqual(sorted(result["matched_skills"]), ["python", "sql"])
    
    def test_whitespace_trimming(self):
        """Test that leading/trailing whitespace is trimmed."""
        result = analyze_skill_gap(
            cv_skills=[" Python ", "  SQL  "],
            job_skills=["Python", "SQL"]
        )
        self.assertEqual(result["gap_percentage"], 0.0)
        self.assertEqual(result["matched_percentage"], 100.0)
    
    def test_combined_case_and_whitespace(self):
        """Test case-insensitive and whitespace handling combined."""
        result = analyze_skill_gap(
            cv_skills=[" PYTHON ", "  SQL  "],
            job_skills=["python", " sql "]
        )
        self.assertEqual(result["gap_percentage"], 0.0)
        self.assertEqual(result["matched_count"], 2)
    
    def test_duplicate_deduplication(self):
        """Test that duplicate skills are deduplicated."""
        result = analyze_skill_gap(
            cv_skills=["Python", "python", "PYTHON", "Python"],
            job_skills=["Python"]
        )
        self.assertEqual(result["matched_count"], 1)
        self.assertEqual(result["additional_skills"], [])
        self.assertEqual(len(result["matched_skills"]), 1)
    
    def test_duplicate_in_job_skills(self):
        """Test that duplicate job skills are deduplicated."""
        result = analyze_skill_gap(
            cv_skills=["Python"],
            job_skills=["Python", "python", "PYTHON"]
        )
        self.assertEqual(result["matched_count"], 1)
        self.assertEqual(result["missing_skills"], [])
    
    def test_special_characters_in_skill_names(self):
        """Test that special characters are preserved in skill names."""
        result = analyze_skill_gap(
            cv_skills=["C++", "C#", "Node.js"],
            job_skills=["c++", "c#", "node.js"]
        )
        self.assertEqual(result["gap_percentage"], 0.0)
        self.assertEqual(result["matched_percentage"], 100.0)
        self.assertEqual(sorted(result["matched_skills"]), ["c#", "c++", "node.js"])
    
    # ========================================================================
    # GROUP 4: Null/Non-String Handling
    # ========================================================================
    
    def test_none_values_in_cv_skills(self):
        """Test that None values in CV skills are filtered out."""
        result = analyze_skill_gap(
            cv_skills=["Python", None, "SQL"],
            job_skills=["Python", "SQL"]
        )
        self.assertEqual(result["gap_percentage"], 0.0)
        self.assertEqual(result["matched_percentage"], 100.0)
    
    def test_none_values_in_job_skills(self):
        """Test that None values in job skills are filtered out."""
        result = analyze_skill_gap(
            cv_skills=["Python", "SQL"],
            job_skills=["Python", None, "SQL"]
        )
        self.assertEqual(result["gap_percentage"], 0.0)
    
    def test_non_string_values_filtered(self):
        """Test that non-string values are filtered out."""
        result = analyze_skill_gap(
            cv_skills=["Python", 123, "SQL", 45.6, True],
            job_skills=["Python", "SQL"]
        )
        self.assertEqual(result["gap_percentage"], 0.0)
        self.assertEqual(result["matched_percentage"], 100.0)
    
    # ========================================================================
    # GROUP 5: Output Format & Type Validation
    # ========================================================================
    
    def test_output_structure(self):
        """Test that output has all required keys."""
        result = analyze_skill_gap(
            cv_skills=["Python"],
            job_skills=["Python"]
        )
        required_keys = {
            "matched_skills", "missing_skills", "additional_skills",
            "gap_count", "matched_count", "job_skills_total",
            "gap_percentage", "matched_percentage", "coverage_percentage",
            "skill_gap_score", "recommendations", "extra_skills",
            "matched_skills_display", "missing_skills_display", "additional_skills_display",
        }
        self.assertEqual(set(result.keys()), required_keys)
    
    def test_output_types(self):
        """Test that output values have correct types."""
        result = analyze_skill_gap(
            cv_skills=["Python", "SQL"],
            job_skills=["Python", "SQL", "AWS"]
        )
        self.assertIsInstance(result["matched_skills"], list)
        self.assertIsInstance(result["missing_skills"], list)
        self.assertIsInstance(result["additional_skills"], list)
        self.assertIsInstance(result["gap_count"], int)
        self.assertIsInstance(result["matched_count"], int)
        self.assertIsInstance(result["job_skills_total"], int)
        self.assertIsInstance(result["gap_percentage"], float)
        self.assertIsInstance(result["matched_percentage"], float)
        self.assertIsInstance(result["coverage_percentage"], float)
    
    def test_list_items_are_strings(self):
        """Test that all items in output lists are strings."""
        result = analyze_skill_gap(
            cv_skills=["Python", "SQL"],
            job_skills=["Python", "AWS"]
        )
        for skill in result["matched_skills"] + result["missing_skills"] + result["additional_skills"]:
            self.assertIsInstance(skill, str)
    
    def test_output_lists_are_sorted(self):
        """Test that output skill lists are sorted alphabetically."""
        result = analyze_skill_gap(
            cv_skills=["Zebra", "Alpha", "Bravo"],
            job_skills=["Zebra", "Alpha", "Bravo", "Charlie"]
        )
        self.assertEqual(
            result["matched_skills"],
            sorted(result["matched_skills"])
        )
        self.assertEqual(
            result["missing_skills"],
            sorted(result["missing_skills"])
        )
        self.assertEqual(
            result["additional_skills"],
            sorted(result["additional_skills"])
        )
    
    # ========================================================================
    # GROUP 6: Metrics Validation
    # ========================================================================
    
    def test_percentages_range_0_to_100(self):
        """Test that percentages are always between 0 and 100."""
        test_cases = [
            ([], []),
            (["Python"], []),
            ([], ["Python"]),
            (["Python"], ["Python"]),
            (["Python", "SQL"], ["Python", "SQL", "AWS"]),
        ]
        for cv, job in test_cases:
            result = analyze_skill_gap(cv_skills=cv, job_skills=job)
            self.assertGreaterEqual(result["gap_percentage"], 0.0)
            self.assertLessEqual(result["gap_percentage"], 100.0)
            self.assertGreaterEqual(result["matched_percentage"], 0.0)
            self.assertLessEqual(result["matched_percentage"], 100.0)
            self.assertGreaterEqual(result["coverage_percentage"], 0.0)
            self.assertLessEqual(result["coverage_percentage"], 100.0)
    
    def test_coverage_equals_100_minus_gap(self):
        """Test that coverage_percentage = 100 - gap_percentage."""
        result = analyze_skill_gap(
            cv_skills=["Python", "SQL"],
            job_skills=["Python", "SQL", "AWS", "Docker"]
        )
        expected_coverage = 100 - result["gap_percentage"]
        self.assertEqual(result["coverage_percentage"], expected_coverage)
    
    def test_matched_plus_gap_equals_100(self):
        """Test that matched_percentage + gap_percentage = 100."""
        result = analyze_skill_gap(
            cv_skills=["Python"],
            job_skills=["Python", "SQL", "AWS"]
        )
        total = result["matched_percentage"] + result["gap_percentage"]
        self.assertAlmostEqual(total, 100.0, places=1)
    
    def test_counts_match_list_lengths(self):
        """Test that counts match the lengths of corresponding lists."""
        result = analyze_skill_gap(
            cv_skills=["Python", "SQL", "Docker"],
            job_skills=["Python", "AWS", "Kubernetes"]
        )
        self.assertEqual(result["matched_count"], len(result["matched_skills"]))
        self.assertEqual(result["gap_count"], len(result["missing_skills"]))
        self.assertEqual(result["job_skills_total"], 
                        len(result["matched_skills"]) + len(result["missing_skills"]))
    
    def test_percentages_rounded_to_2_decimals(self):
        """Test that percentages are rounded to 2 decimal places."""
        result = analyze_skill_gap(
            cv_skills=["Python"],
            job_skills=["Python", "SQL", "AWS"]
        )
        # Check that rounding is correct (33.33%, not 33.333...)
        self.assertEqual(result["matched_percentage"], 33.33)
        self.assertEqual(result["gap_percentage"], 66.67)
    
    # ========================================================================
    # GROUP 7: Mathematical Properties
    # ========================================================================
    
    def test_matched_plus_missing_plus_additional_property(self):
        """Test mathematical consistency of skill categorization."""
        cv_skills_input = ["Python", "SQL", "Docker", "Git"]
        job_skills_input = ["Python", "SQL", "AWS"]
        
        result = analyze_skill_gap(cv_skills=cv_skills_input, job_skills=job_skills_input)
        
        # All CV skills should be in either matched or additional
        all_cv_skills_normalized = set(s.lower().strip() for s in cv_skills_input)
        categorized_skills = set(result["matched_skills"]) | set(result["additional_skills"])
        self.assertEqual(all_cv_skills_normalized, categorized_skills)
    
    def test_job_skills_coverage_sum(self):
        """Test that job skills are covered by matched + missing."""
        cv_skills_input = ["Python", "SQL"]
        job_skills_input = ["Python", "SQL", "AWS"]
        
        result = analyze_skill_gap(cv_skills=cv_skills_input, job_skills=job_skills_input)
        
        job_normalized = set(s.lower().strip() for s in job_skills_input)
        covered_skills = set(result["matched_skills"]) | set(result["missing_skills"])
        self.assertEqual(job_normalized, covered_skills)
    
    # ========================================================================
    # GROUP 8: Boundary Tests
    # ========================================================================
    
    def test_single_skill_match(self):
        """Test with single skill lists."""
        result = analyze_skill_gap(
            cv_skills=["Python"],
            job_skills=["Python"]
        )
        self.assertEqual(result["gap_percentage"], 0.0)
        self.assertEqual(result["matched_percentage"], 100.0)
    
    def test_single_skill_no_match(self):
        """Test with single skill, no match."""
        result = analyze_skill_gap(
            cv_skills=["Java"],
            job_skills=["Python"]
        )
        self.assertEqual(result["gap_percentage"], 100.0)
        self.assertEqual(result["matched_percentage"], 0.0)
    
    def test_large_skill_lists(self):
        """Test with large numbers of skills."""
        cv_skills = [f"Skill_{i}" for i in range(100)]
        job_skills = [f"Skill_{i}" for i in range(50, 150)]
        
        result = analyze_skill_gap(cv_skills=cv_skills, job_skills=job_skills)
        
        # CV has skills 0-99, Job needs 50-149
        # Matched: 50-99 (50 skills)
        # Missing: 100-149 (50 skills)
        self.assertEqual(result["matched_count"], 50)
        self.assertEqual(result["gap_count"], 50)
        self.assertEqual(result["matched_percentage"], 50.0)
        self.assertEqual(result["gap_percentage"], 50.0)


class TestSkillGapIntegration(unittest.TestCase):
    """Integration tests simulating real-world scenarios."""
    
    def test_realistic_junior_developer_scenario(self):
        """Test realistic junior developer CV vs mid-level job."""
        cv_skills = ["Python", "Git", "HTML", "CSS", "SQL"]
        job_skills = ["Python", "JavaScript", "React", "Node.js", "SQL", "Docker", "AWS"]
        
        result = analyze_skill_gap(cv_skills=cv_skills, job_skills=job_skills)
        
        # Expected: Python and SQL match, rest missing
        self.assertEqual(result["matched_count"], 2)
        self.assertEqual(result["gap_count"], 5)
        self.assertEqual(result["coverage_percentage"], 28.57)
    
    def test_realistic_senior_developer_scenario(self):
        """Test realistic senior developer CV vs senior job."""
        cv_skills = ["Python", "SQL", "Docker", "Kubernetes", "AWS", "Git", 
                     "FastAPI", "PostgreSQL", "CI/CD", "Terraform"]
        job_skills = ["Python", "SQL", "Docker", "Kubernetes", "AWS", "FastAPI"]
        
        result = analyze_skill_gap(cv_skills=cv_skills, job_skills=job_skills)
        
        # Expected: Perfect match on required skills + extra skills
        self.assertEqual(result["matched_count"], 6)
        self.assertEqual(result["gap_count"], 0)
        self.assertEqual(result["gap_percentage"], 0.0)
        self.assertEqual(result["coverage_percentage"], 100.0)
    
    def test_career_changer_scenario(self):
        """Test career changer with some relevant skills."""
        cv_skills = ["JavaScript", "React", "Git", "Agile", "SQL"]
        job_skills = ["Python", "Django", "PostgreSQL", "Docker", "AWS"]
        
        result = analyze_skill_gap(cv_skills=cv_skills, job_skills=job_skills)
        
        # Expected: No exact matches (SQL != PostgreSQL), large gap
        self.assertEqual(result["matched_count"], 0)
        self.assertEqual(result["gap_count"], 5)
        self.assertEqual(result["gap_percentage"], 100.0)

    # ========================================================================
    # GROUP 9: Recommendation Tests
    # ========================================================================

    def test_recommendations_mapping_present(self):
        """Missing skill that exists in SKILL_RECOMMENDATIONS returns mapped recommendation."""
        result = analyze_skill_gap(cv_skills=[], job_skills=["Docker"])
        self.assertEqual(result["gap_count"], 1)
        self.assertTrue(isinstance(result["recommendations"], list))
        # Expect a mapped recommendation (not the fallback phrase)
        self.assertNotIn("Bổ sung kiến thức", result["recommendations"][0])

    def test_recommendations_fallback_when_unmapped(self):
        """If a missing skill is not in mapping, a fallback recommendation is returned."""
        result = analyze_skill_gap(cv_skills=[], job_skills=["Elasticsearch"])
        self.assertEqual(result["gap_count"], 1)
        self.assertEqual(len(result["recommendations"]), 1)
        self.assertIn("Bổ sung kiến thức", result["recommendations"][0])

    def test_jd_empty_semantics(self):
        """When job_skills is empty, skill_gap_score must be 100.0 and recommendations empty."""
        result = analyze_skill_gap(cv_skills=["Python"], job_skills=[])
        self.assertEqual(result["job_skills_total"], 0)
        self.assertEqual(result["skill_gap_score"], 100.0)
        self.assertEqual(result["recommendations"], [])
        self.assertEqual(result["matched_percentage"], 100.0)
        self.assertEqual(result["coverage_percentage"], 100.0)


# ============================================================================
# TEST EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)
