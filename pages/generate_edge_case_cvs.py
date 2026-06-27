"""
generate_edge_case_cvs.py
Sinh CV PDF để test các edge case của cv-jd-matcher.
Chạy: python generate_edge_case_cvs.py
Output: thư mục test_edge_cvs/
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib import colors
import os

OUTPUT_DIR = "test_edge_cvs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

BODY = ParagraphStyle("Body", fontSize=10, fontName="Helvetica", leading=14, spaceAfter=6)
TITLE = ParagraphStyle("Title", fontSize=13, fontName="Helvetica-Bold", spaceAfter=4)


def make_pdf(filename: str, lines: list[str]):
    path = os.path.join(OUTPUT_DIR, filename)
    doc = SimpleDocTemplate(path, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    story = []
    for line in lines:
        if line.startswith("##"):
            story.append(Paragraph(line[2:].strip(), TITLE))
        elif line == "---":
            story.append(Spacer(1, 8))
        else:
            story.append(Paragraph(line or "&nbsp;", BODY))
    doc.build(story)
    print(f"Generated: {path}")


# ── Case 1: JavaScript không khớp nhầm Java ──────────────────────────────────
make_pdf("CASE1_javascript_not_java.pdf", [
    "## Tran Van JavaScript",
    "Email: jsdev@email.com | Ho Chi Minh City",
    "---",
    "## Summary",
    "Frontend developer specializing in JavaScript and TypeScript. No Java experience.",
    "---",
    "## Technical Skills",
    # Có JavaScript, TypeScript — KHÔNG có Java
    # Kỳ vọng: extractor KHÔNG detect Java, chỉ detect JavaScript
    "Languages: JavaScript, TypeScript, HTML, CSS",
    "Frontend: React, Next.js, Vue.js",
    "Tools: Git, GitHub, Webpack, Vite",
    "---",
    "## Experience",
    "Frontend Developer - WebAgency (2022 - Present) - 2 years of experience",
    "- Built single-page applications using JavaScript and React",
    "- Used TypeScript for type-safe component development",
    "---",
    "## Note for tester",
    "Expected: Java should NOT be detected. JavaScript SHOULD be detected.",
    "If Java appears in skill list -> word-boundary fix is broken.",
])

# ── Case 2: Kinh nghiệm ghi kiểu đa dạng ────────────────────────────────────
make_pdf("CASE2_experience_formats.pdf", [
    "## Nguyen Thi Formats",
    "Email: formats@email.com | Ha Noi",
    "---",
    "## Summary",
    # Ghi kinh nghiệm nhiều cách khác nhau — test regex có bắt được không
    "I have 3 years of experience in backend development.",
    "---",
    "## Experience",
    "Senior Developer - CompanyA (2021 - Present)",
    "- Over 3 years experience with Spring Boot and Java",
    "- 2+ years kinh nghiem lam viec voi MySQL va PostgreSQL",
    "- Tham gia du an lon voi hon 3 nam kinh nghiem thuc te",
    "---",
    "## Technical Skills",
    "Languages: Java, Python, SQL",
    "Backend: Spring Boot, REST API",
    "Database: MySQL, PostgreSQL",
    "Tools: Git, Docker",
    "---",
    "## Note for tester",
    "Expected: experience_years should be 3 (not 0, not inflated).",
    "Snippets shown should reference 'experience' context, not random numbers.",
])

# ── Case 3: Không ghi kinh nghiệm năm ────────────────────────────────────────
make_pdf("CASE3_no_experience_years.pdf", [
    "## Le Van Fresher",
    "Email: fresher@email.com | Da Nang",
    "---",
    "## Summary",
    "Recent graduate looking for first job in software development.",
    # Không có câu nào chứa "X years experience"
    "---",
    "## Education",
    "B.Sc. Computer Science - HCMUS (2020 - 2024) - GPA: 3.5/4.0",
    "---",
    "## Projects",
    "Todo App | React, Node.js, MongoDB (2024)",
    "- Built a full-stack todo application with user authentication",
    "- Deployed on Heroku with CI/CD via GitHub Actions",
    "---",
    "## Technical Skills",
    "Languages: JavaScript, Python, HTML, CSS",
    "Frontend: React",
    "Backend: Node.js",
    "Database: MongoDB",
    "Tools: Git, GitHub",
    "---",
    "## Note for tester",
    "Expected: experience_years = 0, no crash, no snippet shown.",
])

# ── Case 4: Skill ngoài whitelist (JD yêu cầu Kafka, Golang) ─────────────────
make_pdf("CASE4_skill_outside_whitelist.pdf", [
    "## Pham Van Kafka",
    "Email: kafka@email.com | Ho Chi Minh City",
    "---",
    "## Summary",
    "Backend engineer with 4 years of experience in distributed systems.",
    "Proficient in Golang, Kafka, and gRPC — skills not in default whitelist.",
    "---",
    "## Technical Skills",
    # Kafka, Golang, gRPC không có trong SKILL_KEYWORDS mặc định
    # Kỳ vọng: nếu JD yêu cầu Kafka/Golang, get_scan_skill_keywords() bổ sung vào
    # -> extractor detect được dù không có trong whitelist cứng
    "Languages: Go, Python, SQL",
    "Backend: Kafka, gRPC, REST API, Microservices",
    "Database: PostgreSQL, Redis, Cassandra",
    "DevOps: Docker, Kubernetes, Git",
    "---",
    "## Experience",
    "Backend Engineer - DistributedCo (2020 - Present) - 4 years of experience",
    "- Designed event-driven architecture using Kafka with 1M+ messages/day",
    "- Built high-performance services in Go (Golang) with gRPC communication",
    "- Managed PostgreSQL and Redis clusters for low-latency data access",
    "---",
    "## Note for tester",
    "Create a JD requiring 'Kafka' and 'Go' skills first.",
    "Expected: Kafka and Go detected IF JD skills are passed to extractor.",
    "If not detected -> get_scan_skill_keywords() integration is broken.",
])

# ── Case 5: Skill case mismatch ───────────────────────────────────────────────
make_pdf("CASE5_skill_case_mismatch.pdf", [
    "## Nguyen Van CaseMix",
    "Email: casemix@email.com | Ho Chi Minh City",
    "---",
    "## Summary",
    "Full-stack developer with 2 years of experience. Skills written in mixed case.",
    "---",
    "## Technical Skills",
    # Cố tình viết sai case để test normalize
    "Languages: python, JAVA, javascript, typescript",
    "Frontend: REACT, next.js, tailwind css",
    "Backend: spring boot, REST api, docker",
    "Database: mysql, POSTGRESQL, redis",
    "Tools: GIT, github, postman",
    "---",
    "## Experience",
    "Developer - MixedCaseCorp (2022 - Present) - 2 years of experience",
    "- Developed APIs using spring boot and python",
    "- Managed databases with mysql and POSTGRESQL",
    "---",
    "## Note for tester",
    "Expected: Python, Java, JavaScript, React etc. all detected despite wrong case.",
    "If not detected -> normalize in extract_skills is broken.",
])

# ── Case 6: Kinh nghiệm số dễ nhầm (năm calendar, tuổi, bảo hành...) ─────────
make_pdf("CASE6_misleading_numbers.pdf", [
    "## Tran Thi SoNam",
    "Email: sonam@email.com | Ho Chi Minh City",
    "---",
    "## Summary",
    "Software developer. Born in 2000. Laptop warranty expires in 2025.",
    # Không có câu nào là "X years experience" thật sự
    # Nhưng có nhiều số năm dễ nhầm
    "---",
    "## Education",
    "B.Sc. Information Technology - UIT (2018 - 2022)",
    "Expected graduation: 2022. Program duration: 4 years.",
    "---",
    "## Projects",
    "E-commerce Platform (2023) - Team of 5 members, completed in 6 months",
    "Hospital System (2022) - Maintenance contract: 2 years warranty",
    "Plan to study abroad for 2 years starting 2026.",
    "---",
    "## Technical Skills",
    "Languages: Java, Python, JavaScript",
    "Backend: Spring Boot, REST API",
    "Database: MySQL",
    "Tools: Git, Docker",
    "---",
    "## Note for tester",
    "Expected: experience_years = 0 (no valid 'X years experience' pattern).",
    "Numbers like '4 years' (program), '2 years' (warranty) should NOT be matched.",
    "If years > 0 -> regex is too loose, old bug still present.",
])

print(f"\nDone! 6 edge case CVs saved to ./{OUTPUT_DIR}/")
print("\nTest checklist:")
print("CASE1: Java NOT in skills, JavaScript IN skills")
print("CASE2: experience_years = 3, snippets reference 'experience'")
print("CASE3: experience_years = 0, no crash")
print("CASE4: Kafka/Go detected ONLY if JD requires them")
print("CASE5: All skills detected despite wrong case")
print("CASE6: experience_years = 0, misleading numbers ignored")