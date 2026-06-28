import os
try:
    from dotenv import load_dotenv
except Exception:
    # dotenv is optional in some environments (CI or constrained shells)
    def load_dotenv():
        return None

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
DB_PATH = "cv_matching.db"

# --- RAG config (Role: RAG team) ---
# Model đa ngôn ngữ (hỗ trợ tiếng Việt) để embed CV/JD cho semantic search.
# Nhẹ (~120MB), chạy tốt trên CPU, không cần GPU.
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "paraphrase-multilingual-MiniLM-L12-v2")
VECTOR_STORE_DIR = os.getenv("VECTOR_STORE_DIR", "vector_store")

# Danh sách kỹ năng dùng chung cho chức năng trích xuất và phân tích Skill-gap.
# Mở rộng để giảm tình trạng "JD yêu cầu skill ngoài whitelist thì không bao giờ
# detect được dù CV có ghi rõ". Whitelist này vẫn không thể bao quát hết mọi
# skill có thể có trong JD tự do -> dùng kèm get_scan_skill_keywords() bên dưới
# để tự bổ sung skill từ JD vào danh sách quét tại runtime.
SKILL_KEYWORDS = [
    # Ngôn ngữ lập trình
    "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "C", "Go",
    "Rust", "Kotlin", "Swift", "PHP", "Ruby", "Scala", "R", "Dart", "Perl",
    "MATLAB", "Objective-C", "Bash", "Shell Script",

    # Frontend
    "React", "Vue.js", "Angular", "Next.js", "Nuxt.js", "Svelte", "jQuery",
    "Tailwind CSS", "Bootstrap", "Redux", "Webpack", "Vite", "Sass", "HTML",
    "CSS",

    # Backend / Framework
    "Node.js", "Express", "FastAPI", "Spring Boot", "Spring", "Django",
    "Flask", "Laravel", "ASP.NET", "ASP.NET Core", "NestJS",
    "Ruby on Rails", ".NET", "Symfony",

    # Database
    "SQL", "MySQL", "PostgreSQL", "MongoDB", "Redis", "SQLite", "Oracle",
    "SQL Server", "Cassandra", "Elasticsearch", "Firebase", "DynamoDB",
    "MariaDB", "Neo4j",

    # Cloud / DevOps
    "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Git", "GitHub", "GitLab",
    "CI/CD", "Jenkins", "Terraform", "Linux", "Nginx", "Ansible", "Bitbucket",
    "Vagrant", "Prometheus", "Grafana",

    # Data / Machine Learning
    "Pandas", "NumPy", "TensorFlow", "PyTorch", "Scikit-learn",
    "Machine Learning", "Deep Learning", "Keras", "OpenCV", "NLP",
    "Computer Vision", "Spark", "Hadoop", "Power BI", "Tableau",
    "Matplotlib", "Seaborn", "Data Analysis", "Big Data", "ETL",

    # Mobile
    "React Native", "Flutter", "Android", "iOS", "Xcode", "SwiftUI",

    # Testing
    "JUnit", "Selenium", "Pytest", "Jest", "Cypress", "Postman",
    "Manual Testing", "Automation Testing",

    # Khác
    "REST API", "GraphQL", "Microservices", "Agile", "Scrum",
    "Project Management", "Excel", "PowerPoint", "Figma", "UI/UX",
]


def get_scan_skill_keywords(extra_skills=None) -> list:
    """Trả về danh sách skill dùng để quét CV: whitelist cố định (SKILL_KEYWORDS)
    UNION với các skill lấy từ JD (extra_skills, do người dùng nhập tự do ở
    2_Tao_Job.py). Giúp extractor.extract_skills() không bị giới hạn cứng vào
    whitelist cố định -- nếu JD yêu cầu skill chưa có trong whitelist mà CV có
    ghi rõ, hệ thống vẫn detect được thay vì luôn báo thiếu skill.

    Args:
        extra_skills (list[str] | None): skill lấy từ required_skills của 1 hoặc
            nhiều Job hiện có trong DB (vd lấy từ list_jobs()).

    Returns:
        list[str]: danh sách skill để quét, đã loại trùng (case-insensitive),
            giữ casing ưu tiên từ SKILL_KEYWORDS trước, JD sau.
    """
    seen_lower = set()
    result = []

    for s in SKILL_KEYWORDS:
        key = s.strip().lower()
        if key not in seen_lower:
            seen_lower.add(key)
            result.append(s)

    for s in (extra_skills or []):
        if not s or not isinstance(s, str):
            continue
        key = s.strip().lower()
        if key not in seen_lower:
            seen_lower.add(key)
            result.append(s.strip())

    return result


# Mapping from normalized skill name -> short recommendation string.
# Keep keys lowercased. These are used by the skill-gap recommender
# to provide actionable next steps for missing skills.
SKILL_RECOMMENDATIONS = {
    # Ngôn ngữ lập trình
    "python": "Nâng cao Python: hướng tới làm project xử lý dữ liệu và web với FastAPI.",
    "java": "Ôn Java core và Spring Boot để xây dựng backend quy mô lớn.",
    "javascript": "Làm các project frontend hoặc động với ES6+ và tư duy bất đồng bộ.",
    "typescript": "Học TypeScript: type system, interface/generic, áp dụng vào project React/Node có sẵn.",
    "c++": "Củng cố C++ về quản lý bộ nhớ, STL và làm project liên quan cấu trúc dữ liệu/giải thuật.",
    "c#": "Học C# và .NET để xây dựng ứng dụng desktop/web, làm quen LINQ và Entity Framework.",
    "c": "Ôn lại C: con trỏ, quản lý bộ nhớ thủ công, làm project hệ thống nhỏ để củng cố.",
    "go": "Học Go (Golang): goroutine, channel, xây dựng một service nhỏ để hiểu concurrency.",
    "rust": "Học Rust: ownership/borrowing, làm 1 CLI tool nhỏ để nắm vững memory safety.",
    "kotlin": "Học Kotlin cho phát triển Android hoặc backend với Spring, làm quen coroutines.",
    "swift": "Học Swift và SwiftUI để xây dựng ứng dụng iOS cơ bản.",
    "php": "Ôn PHP hiện đại (PHP 8+) và một framework như Laravel để xây REST API.",
    "ruby": "Học Ruby cơ bản và Ruby on Rails để hiểu convention-over-configuration.",
    "scala": "Học Scala cơ bản, đặc biệt nếu làm việc với Spark cho xử lý dữ liệu lớn.",
    "r": "Học R cho phân tích thống kê và trực quan hoá dữ liệu (ggplot2, dplyr).",
    "dart": "Học Dart song song với Flutter để phát triển ứng dụng mobile đa nền tảng.",
    "perl": "Ôn Perl cơ bản cho xử lý text/script tự động hoá hệ thống.",
    "matlab": "Luyện MATLAB cho tính toán số học, xử lý tín hiệu/ảnh hoặc mô phỏng.",
    "objective-c": "Ôn Objective-C cơ bản nếu cần maintain codebase iOS cũ.",
    "bash": "Luyện viết Bash script để tự động hoá tác vụ hệ thống và CI/CD.",
    "shell script": "Thực hành shell scripting: xử lý file, pipeline lệnh, cron job cơ bản.",

    # Frontend
    "react": "Học React hooks, quản lý state bằng Redux hoặc Context API và làm SPA.",
    "vue.js": "Học Vue 3 với Composition API, Vue Router và Pinia/Vuex để quản lý state.",
    "angular": "Học Angular: component, dependency injection, RxJS và làm 1 project CRUD hoàn chỉnh.",
    "next.js": "Học Next.js: SSR/SSG, routing và API routes để xây dựng ứng dụng React full-stack.",
    "nuxt.js": "Học Nuxt.js để xây dựng ứng dụng Vue có SSR, làm quen module ecosystem.",
    "svelte": "Học Svelte/SvelteKit để trải nghiệm cách viết component không cần virtual DOM.",
    "jquery": "Ôn lại jQuery cơ bản nếu cần maintain code cũ, song song học JS thuần hiện đại.",
    "tailwind css": "Thực hành Tailwind CSS: utility-first, responsive design và custom theme.",
    "bootstrap": "Luyện Bootstrap: grid system, components có sẵn để dựng UI nhanh.",
    "redux": "Học Redux/Redux Toolkit để quản lý state phức tạp trong ứng dụng React lớn.",
    "webpack": "Tìm hiểu Webpack: cấu hình loader, plugin, code splitting cơ bản.",
    "vite": "Học Vite để hiểu build tool hiện đại, so sánh với Webpack về tốc độ dev.",
    "sass": "Luyện Sass/SCSS: nesting, mixin, variable để viết CSS có cấu trúc hơn.",
    "html": "Củng cố HTML semantic và các nguyên tắc accessibility cơ bản.",
    "css": "Học CSS Flexbox, Grid và thiết kế responsive.",

    # Backend / Framework
    "node.js": "Thực hành Node.js với Express hoặc NestJS, hiểu async I/O và viết kiểm thử cơ bản.",
    "express": "Học Express.js: middleware, routing, xây REST API cơ bản với Node.js.",
    "fastapi": "Xây API với FastAPI, viết unit test và triển khai bằng Docker.",
    "spring boot": "Tập trung vào Spring Boot nền tảng và cấu hình cho môi trường production.",
    "spring": "Ôn Spring Framework core: IoC, dependency injection, AOP.",
    "django": "Học Django: ORM, admin panel, authentication để xây web app nhanh.",
    "flask": "Xây dựng REST API với Flask, viết test và triển khai ứng dụng cơ bản.",
    "laravel": "Học Laravel: Eloquent ORM, routing, blade template để xây web app PHP.",
    "asp.net": "Học ASP.NET: MVC pattern, routing và làm quen Entity Framework.",
    "asp.net core": "Học ASP.NET Core: Web API, dependency injection, middleware pipeline.",
    "nestjs": "Học NestJS: module/controller/service architecture, decorator pattern.",
    "ruby on rails": "Học Ruby on Rails: MVC, ActiveRecord, làm 1 CRUD app hoàn chỉnh.",
    ".net": "Ôn .NET ecosystem: C#, ASP.NET, Entity Framework cho phát triển enterprise app.",
    "symfony": "Học Symfony: component-based architecture, Doctrine ORM.",

    # Database
    "sql": "Thực hành SQL với join, indexing và một hệ quản trị dữ liệu như PostgreSQL hoặc MySQL.",
    "mysql": "Luyện MySQL: thiết kế schema, indexing, tối ưu query chậm.",
    "postgresql": "Học PostgreSQL: kiểu dữ liệu nâng cao, window function, EXPLAIN ANALYZE.",
    "mongodb": "Học MongoDB: schema design cho NoSQL, aggregation pipeline.",
    "redis": "Học Redis: caching strategy, pub/sub, các cấu trúc dữ liệu cơ bản.",
    "sqlite": "Ôn SQLite cho ứng dụng nhỏ/embedded, hiểu giới hạn khi scale.",
    "oracle": "Học Oracle DB: PL/SQL, tối ưu query cho hệ thống enterprise.",
    "sql server": "Học SQL Server: T-SQL, stored procedure, SQL Server Management Studio.",
    "cassandra": "Tìm hiểu Cassandra cho dữ liệu phân tán, hiểu mô hình wide-column.",
    "elasticsearch": "Học Elasticsearch: indexing, full-text search, tích hợp với ELK stack.",
    "firebase": "Học Firebase: Firestore, Authentication, Cloud Functions cho app nhanh.",
    "dynamodb": "Học DynamoDB: thiết kế bảng NoSQL trên AWS, partition key/sort key.",
    "mariadb": "Ôn MariaDB tương tự MySQL, chú ý các khác biệt về engine/feature.",
    "neo4j": "Tìm hiểu Neo4j và Cypher query language cho dữ liệu dạng graph.",

    # Cloud / DevOps
    "docker": "Học Docker: containerize ứng dụng, docker-compose và các thực hành tốt nhất.",
    "kubernetes": "Học Kubernetes cơ bản: pod, deployment, service, dùng minikube để thực hành.",
    "aws": "Tìm hiểu AWS cơ bản: EC2, S3, IAM và triển khai ứng dụng đơn giản.",
    "azure": "Tìm hiểu Azure cơ bản: App Service, Azure Functions, Azure DevOps.",
    "gcp": "Tìm hiểu Google Cloud Platform: Compute Engine, Cloud Storage, Cloud Run.",
    "git": "Sử dụng Git branching, quy trình pull request và xử lý merge conflict.",
    "github": "Thực hành quy trình GitHub: pull request, issues, releases và GitHub Actions cơ bản.",
    "gitlab": "Làm quen GitLab CI/CD, merge request workflow.",
    "ci/cd": "Học nguyên lý CI/CD: tự động build/test/deploy với GitHub Actions hoặc Jenkins.",
    "jenkins": "Học Jenkins: pipeline as code, tích hợp build/test tự động.",
    "terraform": "Học Terraform: Infrastructure as Code, quản lý resource cloud bằng HCL.",
    "linux": "Luyện Linux cơ bản: shell commands, permissions và quản lý tiến trình.",
    "nginx": "Học Nginx: reverse proxy, load balancing, cấu hình SSL cơ bản.",
    "ansible": "Học Ansible: playbook, automation cấu hình server không cần agent.",
    "bitbucket": "Làm quen Bitbucket pipelines và quy trình review code trên Bitbucket.",
    "vagrant": "Tìm hiểu Vagrant để dựng môi trường dev đồng nhất qua VM.",
    "prometheus": "Học Prometheus: thu thập metrics, viết alerting rule cơ bản.",
    "grafana": "Học Grafana: dashboard hoá metrics, tích hợp với Prometheus.",

    # Data / Machine Learning
    "pandas": "Luyện Pandas cho xử lý dữ liệu: groupby, merge và thao tác chuỗi thời gian.",
    "numpy": "Nâng cao NumPy để tối ưu tính toán ma trận và vector hóa mã nguồn.",
    "tensorflow": "Học TensorFlow cơ bản: xây dựng mô hình, huấn luyện, đánh giá và tối ưu.",
    "pytorch": "Học PyTorch cơ bản để xây dựng mô hình deep learning và custom training loop.",
    "scikit-learn": "Học scikit-learn: xây dựng pipeline, chọn mô hình và đánh giá bằng cross-validation.",
    "machine learning": "Ôn kiến thức machine learning cơ bản: mô hình học có giám sát và không giám sát.",
    "deep learning": "Học deep learning cơ bản: CNN, RNN, và thực hành với 1 dataset thực tế.",
    "keras": "Học Keras để xây dựng nhanh các mô hình neural network trên nền TensorFlow.",
    "opencv": "Học OpenCV: xử lý ảnh cơ bản, phát hiện đối tượng, làm 1 project computer vision nhỏ.",
    "nlp": "Học NLP cơ bản: tokenization, word embedding, thử với thư viện như spaCy/Transformers.",
    "computer vision": "Học computer vision cơ bản: image classification, object detection.",
    "spark": "Học Apache Spark: xử lý dữ liệu lớn phân tán, PySpark cho data pipeline.",
    "hadoop": "Tìm hiểu Hadoop ecosystem: HDFS, MapReduce cho xử lý big data.",
    "power bi": "Học Power BI: tạo dashboard, DAX cơ bản để phân tích dữ liệu kinh doanh.",
    "tableau": "Học Tableau: kết nối dữ liệu, xây dashboard trực quan.",
    "matplotlib": "Luyện Matplotlib để vẽ biểu đồ trực quan hoá dữ liệu cơ bản.",
    "seaborn": "Học Seaborn để vẽ biểu đồ thống kê đẹp hơn, dựa trên Matplotlib.",
    "data analysis": "Luyện kỹ năng phân tích dữ liệu: làm sạch, EDA, rút insight từ dataset thực tế.",
    "big data": "Tìm hiểu hệ sinh thái Big Data: Hadoop, Spark, Kafka cho xử lý dữ liệu quy mô lớn.",
    "etl": "Học quy trình ETL: extract-transform-load, dùng công cụ như Airflow để tự động hoá.",

    # Mobile
    "react native": "Học React Native: xây app cross-platform, navigation và state management.",
    "flutter": "Học Flutter và Dart: widget tree, state management (Provider/Bloc).",
    "android": "Học phát triển Android: Kotlin/Java, Jetpack components, lifecycle.",
    "ios": "Học phát triển iOS: Swift, UIKit/SwiftUI, App lifecycle.",
    "xcode": "Làm quen Xcode: debugging, Interface Builder, quản lý project iOS.",
    "swiftui": "Học SwiftUI: declarative UI, state binding cho phát triển iOS hiện đại.",

    # Testing
    "junit": "Luyện viết JUnit test: unit test, mock với Mockito cho Java/Spring Boot.",
    "selenium": "Học Selenium: automation test UI web, làm quen Page Object Model.",
    "pytest": "Luyện Pytest: fixture, parametrize, mock cho unit test Python.",
    "jest": "Học Jest: unit test cho JavaScript/React, snapshot testing.",
    "cypress": "Học Cypress: E2E testing cho ứng dụng web hiện đại.",
    "postman": "Luyện Postman: test API thủ công, viết collection và script kiểm tra response.",
    "manual testing": "Củng cố kỹ năng test thủ công: test case design, EP/BVA, bug report rõ ràng.",
    "automation testing": "Học automation testing: chọn framework phù hợp (Selenium/Cypress), CI integration.",

    # Khác
    "rest api": "Ôn nguyên lý REST API: HTTP method, status code, thiết kế endpoint chuẩn.",
    "graphql": "Học GraphQL: schema, query/mutation, so sánh ưu nhược điểm với REST.",
    "microservices": "Tìm hiểu kiến trúc microservices: giao tiếp giữa service, API Gateway cơ bản.",
    "agile": "Ôn quy trình Agile: sprint planning, retrospective, làm việc nhóm theo iteration.",
    "scrum": "Học Scrum: vai trò Scrum Master/PO, daily standup, sprint review.",
    "project management": "Luyện kỹ năng quản lý dự án: lập kế hoạch, theo dõi tiến độ, quản lý rủi ro.",
    "excel": "Luyện Excel: công thức, PivotTable và quy trình làm sạch dữ liệu.",
    "powerpoint": "Luyện kỹ năng làm slide PowerPoint: bố cục rõ ràng, trình bày dữ liệu trực quan.",
    "figma": "Học Figma: thiết kế UI cơ bản, làm quen component và prototype.",
    "ui/ux": "Học nguyên lý UI/UX cơ bản: user research, wireframe, usability testing.",
}