"""
generate_test_cvs.py
Sinh CV PDF giả để test cv-jd-matcher.
Chạy: python generate_test_cvs.py
Output: thư mục test_cvs/ với nhiều file PDF
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib import colors
import os

OUTPUT_DIR = "test_cvs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Style ─────────────────────────────────────────────────────────────────────
styles = getSampleStyleSheet()
NAME_STYLE = ParagraphStyle("Name", fontSize=16, fontName="Helvetica-Bold", spaceAfter=2)
CONTACT_STYLE = ParagraphStyle("Contact", fontSize=9, fontName="Helvetica", textColor=colors.grey, spaceAfter=8)
SECTION_STYLE = ParagraphStyle("Section", fontSize=11, fontName="Helvetica-Bold", spaceAfter=4, spaceBefore=10)
BODY_STYLE = ParagraphStyle("Body", fontSize=9, fontName="Helvetica", spaceAfter=3, leading=13)
BULLET_STYLE = ParagraphStyle("Bullet", fontSize=9, fontName="Helvetica", leftIndent=12, spaceAfter=2, leading=13)


def section(title: str) -> list:
    return [
        Spacer(1, 4),
        Paragraph(title.upper(), SECTION_STYLE),
        HRFlowable(width="100%", thickness=0.5, color=colors.black, spaceAfter=4),
    ]


def build_cv(filename: str, data: dict):
    path = os.path.join(OUTPUT_DIR, filename)
    doc = SimpleDocTemplate(
        path, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=1.5*cm, bottomMargin=1.5*cm,
    )
    story = []

    # Header
    story.append(Paragraph(data["name"], NAME_STYLE))
    story.append(Paragraph(data["contact"], CONTACT_STYLE))

    # Summary
    if data.get("summary"):
        story += section("Professional Summary")
        story.append(Paragraph(data["summary"], BODY_STYLE))

    # Experience
    if data.get("experience"):
        story += section("Experience")
        for exp in data["experience"]:
            story.append(Paragraph(f"<b>{exp['title']}</b> — {exp['company']} ({exp['period']})", BODY_STYLE))
            for b in exp.get("bullets", []):
                story.append(Paragraph(f"• {b}", BULLET_STYLE))

    # Education
    if data.get("education"):
        story += section("Education")
        for edu in data["education"]:
            story.append(Paragraph(f"<b>{edu['degree']}</b> — {edu['school']} ({edu['period']})", BODY_STYLE))
            if edu.get("note"):
                story.append(Paragraph(edu["note"], BULLET_STYLE))

    # Projects
    if data.get("projects"):
        story += section("Projects")
        for proj in data["projects"]:
            story.append(Paragraph(f"<b>{proj['name']}</b> | {proj['tech']} ({proj['period']})", BODY_STYLE))
            for b in proj.get("bullets", []):
                story.append(Paragraph(f"• {b}", BULLET_STYLE))

    # Skills
    if data.get("skills"):
        story += section("Technical Skills")
        for k, v in data["skills"].items():
            story.append(Paragraph(f"<b>{k}:</b> {v}", BODY_STYLE))

    doc.build(story)
    print(f"Generated: {path}")


# ── CV Data ───────────────────────────────────────────────────────────────────

PROFILES = [
    # 1. Backend Java Senior — khớp tốt JD Java/Spring Boot
    {
        "name": "Nguyen Van An",
        "contact": "Ho Chi Minh City | anvan@email.com | github.com/anvan",
        "summary": "Senior Backend Developer with 5 years of experience building scalable microservices using Java, Spring Boot, and Docker. Strong background in database optimization and CI/CD pipelines.",
        "experience": [
            {
                "title": "Senior Backend Developer", "company": "TechCorp Vietnam", "period": "2020 – Present",
                "bullets": [
                    "Designed and implemented REST APIs using Spring Boot for an e-commerce platform serving 500K+ users.",
                    "Optimized MySQL query performance, reducing average response time by 40%.",
                    "Led migration from monolith to microservices architecture using Docker and Kubernetes.",
                    "Set up CI/CD pipelines with Jenkins and GitHub Actions for automated testing and deployment.",
                ]
            },
            {
                "title": "Junior Backend Developer", "company": "StartupXYZ", "period": "2018 – 2020",
                "bullets": [
                    "Built RESTful APIs with Spring Boot and integrated with PostgreSQL databases.",
                    "Wrote unit tests using JUnit and Mockito, achieving 80% code coverage.",
                ]
            }
        ],
        "education": [{"degree": "B.Sc. Computer Science", "school": "HCMUS", "period": "2014 – 2018", "note": "GPA: 3.6/4.0"}],
        "projects": [
            {
                "name": "Inventory Management System", "tech": "Java, Spring Boot, MySQL, Docker", "period": "2022",
                "bullets": ["Built full inventory system with role-based access control and real-time stock alerts."]
            }
        ],
        "skills": {
            "Languages": "Java, SQL, Python",
            "Backend": "Spring Boot, Spring, REST API, Microservices",
            "Database": "MySQL, PostgreSQL, Redis",
            "DevOps": "Docker, Kubernetes, Jenkins, Git, GitHub",
            "Testing": "JUnit, Postman",
        }
    },

    # 2. Frontend React — khớp vừa, thiếu backend
    {
        "name": "Le Thi Bich",
        "contact": "Ha Noi, Vietnam | bichle@email.com | github.com/bichle",
        "summary": "Frontend Developer with 2 years of experience building responsive web applications with React and TypeScript. Passionate about UI/UX and performance optimization.",
        "experience": [
            {
                "title": "Frontend Developer", "company": "Digital Agency ABC", "period": "2022 – Present",
                "bullets": [
                    "Developed reusable React components with TypeScript for a SaaS dashboard product.",
                    "Implemented responsive layouts using Tailwind CSS and Bootstrap.",
                    "Integrated REST APIs from backend teams using Axios and React Query.",
                    "Improved Lighthouse performance score from 62 to 91 by optimizing bundle size with Webpack.",
                ]
            }
        ],
        "education": [{"degree": "B.Sc. Information Technology", "school": "HUST", "period": "2018 – 2022", "note": "GPA: 3.2/4.0"}],
        "projects": [
            {
                "name": "Portfolio Builder", "tech": "React, TypeScript, Tailwind CSS, Next.js", "period": "2023",
                "bullets": ["Built a drag-and-drop portfolio builder with live preview and export to PDF."]
            }
        ],
        "skills": {
            "Languages": "JavaScript, TypeScript, HTML, CSS",
            "Frontend": "React, Next.js, Tailwind CSS, Redux, Webpack",
            "Tools": "Git, GitHub, Figma, Postman, VS Code",
        }
    },

    # 3. Data/ML — thiếu web skills, match kém JD backend
    {
        "name": "Pham Quoc Cuong",
        "contact": "Da Nang, Vietnam | cuongpq@email.com | github.com/cuongpq",
        "summary": "Data Scientist with 3 years of experience in machine learning and data analysis. Proficient in Python, PyTorch, and building end-to-end ML pipelines.",
        "experience": [
            {
                "title": "Data Scientist", "company": "AI Research Lab", "period": "2021 – Present",
                "bullets": [
                    "Built and deployed NLP models for sentiment analysis with 92% accuracy using PyTorch and Transformers.",
                    "Developed ETL pipelines using Pandas and Apache Spark to process 10GB+ daily datasets.",
                    "Created interactive dashboards with Power BI for business stakeholders.",
                    "Applied Computer Vision techniques (OpenCV) for defect detection in manufacturing images.",
                ]
            }
        ],
        "education": [{"degree": "M.Sc. Data Science", "school": "HCMUT", "period": "2019 – 2021"}],
        "projects": [
            {
                "name": "Customer Churn Prediction", "tech": "Python, Scikit-learn, Pandas, Matplotlib", "period": "2022",
                "bullets": ["Trained classification models achieving 88% F1-score on imbalanced dataset."]
            }
        ],
        "skills": {
            "Languages": "Python, R, SQL",
            "ML/Data": "PyTorch, TensorFlow, Scikit-learn, Pandas, NumPy, OpenCV, NLP",
            "Tools": "Jupyter, Power BI, Tableau, Git, Docker",
            "Big Data": "Apache Spark, Hadoop, ETL",
        }
    },

    # 4. DevOps — match trung bình, thiếu coding skills
    {
        "name": "Tran Minh Duc",
        "contact": "Ho Chi Minh City | ductm@email.com | linkedin.com/in/ductm",
        "summary": "DevOps Engineer with 4 years of experience in CI/CD, cloud infrastructure, and containerization. AWS Certified Solutions Architect.",
        "experience": [
            {
                "title": "DevOps Engineer", "company": "CloudOps Vietnam", "period": "2020 – Present",
                "bullets": [
                    "Managed AWS infrastructure (EC2, S3, RDS, EKS) for 20+ production services using Terraform.",
                    "Built CI/CD pipelines with Jenkins and GitHub Actions reducing deployment time by 60%.",
                    "Containerized 15+ legacy applications using Docker and orchestrated with Kubernetes.",
                    "Implemented monitoring with Prometheus and Grafana; set up alerting for SLA breaches.",
                    "Configured Nginx reverse proxy and SSL termination for high-traffic applications.",
                ]
            }
        ],
        "education": [{"degree": "B.Sc. Network Engineering", "school": "PTIT", "period": "2016 – 2020"}],
        "projects": [
            {
                "name": "Multi-cloud DR System", "tech": "AWS, Terraform, Kubernetes, Ansible", "period": "2023",
                "bullets": ["Designed disaster recovery system with RTO < 15 minutes across 2 cloud providers."]
            }
        ],
        "skills": {
            "Cloud": "AWS, GCP, Azure",
            "DevOps": "Docker, Kubernetes, Terraform, Ansible, Jenkins, CI/CD",
            "Monitoring": "Prometheus, Grafana, Nginx, Linux",
            "Languages": "Bash, Python, Go",
            "VCS": "Git, GitHub, GitLab, Bitbucket",
        }
    },

    # 5. Fresh grad — ít kinh nghiệm, skill đa dạng nhưng nông
    {
        "name": "Hoang Thi Em",
        "contact": "Ho Chi Minh City | emht@email.com | github.com/emht",
        "summary": "Final-year IT student with hands-on project experience in full-stack web development. Quick learner eager to contribute to software development teams.",
        "experience": [
            {
                "title": "Intern Frontend Developer", "company": "Web Studio DEF", "period": "Jun 2024 – Aug 2024",
                "bullets": [
                    "Assisted in building UI components using React and CSS for a real estate platform.",
                    "Fixed bugs and wrote unit tests with Jest for existing codebase.",
                ]
            }
        ],
        "education": [{"degree": "B.Sc. Information Technology", "school": "UIT", "period": "2021 – Present (Expected 2025)", "note": "GPA: 3.4/4.0 | Relevant: OOP, Database, Web Development"}],
        "projects": [
            {
                "name": "Library Management System", "tech": "Java, Spring Boot, MySQL, React", "period": "2024",
                "bullets": [
                    "Built CRUD REST APIs with Spring Boot and MySQL for book/member management.",
                    "Developed React frontend with search and filter features.",
                ]
            },
            {
                "name": "Weather App", "tech": "JavaScript, HTML, CSS, REST API", "period": "2023",
                "bullets": ["Integrated OpenWeather API to display real-time forecasts with responsive UI."]
            }
        ],
        "skills": {
            "Languages": "Java, JavaScript, Python, HTML, CSS, SQL",
            "Frontend": "React, Bootstrap",
            "Backend": "Spring Boot, REST API",
            "Database": "MySQL, SQLite",
            "Tools": "Git, GitHub, Docker, Postman, VS Code",
        }
    },
]

if __name__ == "__main__":
    names = [
        "NguyenVanAn_Backend_CV.pdf",
        "LeThiBich_Frontend_CV.pdf",
        "PhamQuocCuong_DataML_CV.pdf",
        "TranMinhDuc_DevOps_CV.pdf",
        "HoangThiEm_FreshGrad_CV.pdf",
    ]
    for filename, data in zip(names, PROFILES):
        build_cv(filename, data)
    print(f"\nDone! {len(PROFILES)} CVs saved to ./{OUTPUT_DIR}/")