
"""Skill-Gap Analysis Module

Analyzes the gap between a candidate's CV skills and job requirements.
Provides metrics on matched skills, missing skills, and gap percentages
and builds simple, rule-based recommendations for missing skills.

Role: Hai (Backend Developer)
Dependencies: Only `core.config.SKILL_RECOMMENDATIONS` for mapping (pure Python)
"""

from core.config import SKILL_RECOMMENDATIONS


def build_recommendations(missing_skills, display_map=None):
    """Build recommendation strings for missing skills.

    Args:
        missing_skills (list[str]): Missing skills, typically normalized keys.
        display_map (dict | None): Optional mapping normalized -> display text.

    Returns:
        list[str]: list of recommendation strings in the same order
    """
    if display_map is None:
        display_map = {}

    recs = []
    for s in missing_skills:
        display = display_map.get(s, s)
        if s in SKILL_RECOMMENDATIONS:
            recs.append(SKILL_RECOMMENDATIONS[s])
        else:
            # Fallback recommendation in Vietnamese (short actionable sentence)
            recs.append(f"Bổ sung kiến thức và một project minh chứng cho kỹ năng: {display}.")
    return recs


def analyze_skill_gap(cv_skills, job_skills):
    """
    Analyze skill gap between CV and job requirements.
    
    Compares two lists of skills (CV vs. Job) and identifies:
    - Matched skills: Present in both
    - Missing skills: Required by job but NOT in CV
    - Additional skills: In CV but NOT required by job
    
    Args:
        cv_skills (list[str] or None): 
            List of skills extracted from candidate's CV.
            Example: ["Python", "SQL", "Docker"]
            Can be None or empty.
        
        job_skills (list[str] or None): 
            List of skills required by the job posting.
            Example: ["Python", "AWS", "Docker"]
            Can be None or empty.
    
    Returns:
        dict: Result dictionary with the following keys:
            - matched_skills (list[str]): Skills present in both CV and job
            - missing_skills (list[str]): Skills required but NOT in CV
            - additional_skills (list[str]): Skills in CV but NOT required by job
            - gap_count (int): Number of missing skills
            - matched_count (int): Number of matched skills
            - job_skills_total (int): Total number of required skills
            - gap_percentage (float): (missing / total_required) * 100, rounded to 2 decimals
            - matched_percentage (float): (matched / total_required) * 100, rounded to 2 decimals
            - coverage_percentage (float): 100 - gap_percentage, rounded to 2 decimals
    
    Notes:
        - All string comparisons are case-insensitive and whitespace-trimmed
        - Duplicate skills are automatically deduplicated
        - None or non-string values are filtered out
        - Output lists are sorted alphabetically for deterministic behavior
                - If job_skills_total is 0, the job has no requirements:
                    missing_skills = [], skill_gap_score = 100.0,
                    matched_percentage = 100.0, coverage_percentage = 100.0.
    
    Examples:
        >>> result = analyze_skill_gap(
        ...     ["Python", "SQL"], 
        ...     ["Python", "SQL", "AWS"]
        ... )
        >>> result["gap_count"]
        1
        >>> result["gap_percentage"]
        33.33
        >>> result["matched_skills"]
        ['python', 'sql']
        
        >>> result = analyze_skill_gap(
        ...     ["PYTHON", "python", " Python "],  # Duplicates and case variations
        ...     ["python"]
        ... )
        >>> result["matched_percentage"]
        100.0
        >>> len(result["matched_skills"])
        1
    """
    
    # ============================================================================
    # STEP 1: Input Validation & Normalization
    # ============================================================================
    
    # Handle None inputs
    if cv_skills is None:
        cv_skills = []
    if job_skills is None:
        job_skills = []
    
    # Filter out None and non-string values
    cv_skills = [
        s for s in cv_skills 
        if s is not None and isinstance(s, str)
    ]
    job_skills = [
        s for s in job_skills 
        if s is not None and isinstance(s, str)
    ]
    
    # ============================================================================
    # STEP 2: Normalize Skills (lowercase, strip whitespace, deduplicate)
    # ============================================================================
    
    # Build first-occurrence display maps (normalized -> original casing)
    cv_display = {}
    for s in cv_skills:
        if s is None or not isinstance(s, str):
            continue
        key = s.lower().strip()
        if key not in cv_display:
            cv_display[key] = s.strip()

    job_display = {}
    for s in job_skills:
        if s is None or not isinstance(s, str):
            continue
        key = s.lower().strip()
        if key not in job_display:
            job_display[key] = s.strip()

    cv_normalized = set(cv_display.keys())
    job_normalized = set(job_display.keys())
    
    # ============================================================================
    # STEP 3: Set Operations (intersection, difference)
    # ============================================================================
    
    matched_norm = sorted(list(cv_normalized & job_normalized))
    missing_norm = sorted(list(job_normalized - cv_normalized))
    additional_norm = sorted(list(cv_normalized - job_normalized))

    # Keep canonical (backwards-compatible) normalized lists (lowercased)
    matched_skills = matched_norm
    missing_skills = missing_norm
    additional_skills = additional_norm

    # Map normalized names back to display casing for UI consumption
    def map_display(norm_list, preferred_map, fallback_map):
        display_list = []
        for k in norm_list:
            if k in preferred_map:
                display_list.append(preferred_map[k])
            elif k in fallback_map:
                display_list.append(fallback_map[k])
            else:
                display_list.append(k)
        return display_list

    matched_skills_display = map_display(matched_norm, job_display, cv_display)
    missing_skills_display = map_display(missing_norm, job_display, cv_display)
    additional_skills_display = map_display(additional_norm, cv_display, job_display)
    
    # ============================================================================
    # STEP 4: Calculate Metrics
    # ============================================================================
    
    gap_count = len(missing_norm)
    matched_count = len(matched_norm)
    job_skills_total = len(job_normalized)
    
    # Calculate percentages (handle division by zero)
    if job_skills_total == 0:
        gap_percentage = 0.0
        matched_percentage = 100.0
        coverage_percentage = 100.0
    else:
        gap_percentage = (gap_count / job_skills_total) * 100
        matched_percentage = (matched_count / job_skills_total) * 100
        coverage_percentage = 100 - gap_percentage

    # Skill gap score: matched / required * 100; special-case when no job skills
    if job_skills_total == 0:
        skill_gap_score = 100.0
    else:
        skill_gap_score = round((matched_count / job_skills_total) * 100, 2)
    
    # ============================================================================
    # STEP 5: Assemble Result Dictionary
    # ============================================================================
    
    # Build recommendations (empty when job has no skills)
    if job_skills_total == 0:
        recommendations = []
    else:
        recommendations = build_recommendations(missing_norm, job_display)

    result = {
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "additional_skills": additional_skills,
        # convenience alias (normalized form)
        "extra_skills": additional_skills,
        # Display-friendly versions (original casing where available)
        "matched_skills_display": matched_skills_display,
        "missing_skills_display": missing_skills_display,
        "additional_skills_display": additional_skills_display,
        "gap_count": gap_count,
        "matched_count": matched_count,
        "job_skills_total": job_skills_total,
        "gap_percentage": round(gap_percentage, 2),
        "matched_percentage": round(matched_percentage, 2),
        "coverage_percentage": round(coverage_percentage, 2),
        "skill_gap_score": skill_gap_score,
        "recommendations": recommendations,
    }
    
    return result


# ============================================================================
# DEMO / EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("Skill-Gap Analysis Module - Demo")
    print("=" * 70)
    
    # Example 1: Partial Match (50% Coverage)
    print("\n[Example 1] Partial Match (50% Coverage)")
    print("-" * 70)
    result1 = analyze_skill_gap(
        cv_skills=["Python", "SQL", "Git", "Docker"],
        job_skills=["Python", "SQL", "AWS", "Kubernetes"]
    )
    print(f"CV Skills: {['Python', 'SQL', 'Git', 'Docker']}")
    print(f"Job Skills: {['Python', 'SQL', 'AWS', 'Kubernetes']}")
    print(f"\nMatched Skills: {result1['matched_skills']}")
    print(f"Missing Skills: {result1['missing_skills']}")
    print(f"Additional Skills: {result1['additional_skills']}")
    print(f"\nGap Count: {result1['gap_count']}")
    print(f"Matched Count: {result1['matched_count']}")
    print(f"Gap Percentage: {result1['gap_percentage']}%")
    print(f"Coverage Percentage: {result1['coverage_percentage']}%")
    
    # Example 2: Perfect Match (100% Coverage)
    print("\n[Example 2] Perfect Match (100% Coverage)")
    print("-" * 70)
    result2 = analyze_skill_gap(
        cv_skills=["Python", "SQL", "Docker"],
        job_skills=["Python", "SQL", "Docker"]
    )
    print(f"CV Skills: {['Python', 'SQL', 'Docker']}")
    print(f"Job Skills: {['Python', 'SQL', 'Docker']}")
    print(f"\nMatched Skills: {result2['matched_skills']}")
    print(f"Missing Skills: {result2['missing_skills']}")
    print(f"Gap Percentage: {result2['gap_percentage']}%")
    print(f"Coverage Percentage: {result2['coverage_percentage']}%")
    
    # Example 3: No Match (0% Coverage)
    print("\n[Example 3] No Match (0% Coverage)")
    print("-" * 70)
    result3 = analyze_skill_gap(
        cv_skills=["Java", "Kotlin", "Gradle"],
        job_skills=["Python", "SQL", "Docker"]
    )
    print(f"CV Skills: {['Java', 'Kotlin', 'Gradle']}")
    print(f"Job Skills: {['Python', 'SQL', 'Docker']}")
    print(f"\nMatched Skills: {result3['matched_skills']}")
    print(f"Missing Skills: {result3['missing_skills']}")
    print(f"Additional Skills: {result3['additional_skills']}")
    print(f"Gap Percentage: {result3['gap_percentage']}%")
    print(f"Coverage Percentage: {result3['coverage_percentage']}%")
    
    # Example 4: Case & Whitespace Normalization
    print("\n[Example 4] Case & Whitespace Normalization")
    print("-" * 70)
    result4 = analyze_skill_gap(
        cv_skills=["PYTHON", " Python ", "python"],
        job_skills=["Python"]
    )
    print(f"CV Skills: {['PYTHON', ' Python ', 'python']}")
    print(f"Job Skills: {['Python']}")
    print(f"\nMatched Skills: {result4['matched_skills']}")
    print(f"Matched Count: {result4['matched_count']} (deduplicated)")
    print(f"Gap Percentage: {result4['gap_percentage']}%")
    
    # Example 5: Empty CV (All Skills Missing)
    print("\n[Example 5] Empty CV (All Skills Missing)")
    print("-" * 70)
    result5 = analyze_skill_gap(
        cv_skills=[],
        job_skills=["Python", "AWS", "Docker"]
    )
    print(f"CV Skills: {[]}")
    print(f"Job Skills: {['Python', 'AWS', 'Docker']}")
    print(f"\nMatched Skills: {result5['matched_skills']}")
    print(f"Missing Skills: {result5['missing_skills']}")
    print(f"Gap Percentage: {result5['gap_percentage']}%")
    
    print("\n" + "=" * 70)
    print("Demo Complete")
    print("=" * 70)
