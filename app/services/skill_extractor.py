import re

skills_db = {
    "Programming Languages": [
        "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "Go", "Golang",
        "Rust", "PHP", "Ruby", "Swift", "Kotlin", "R", "Dart"
    ],
    "Frontend Development": [
        "React", "React.js", "ReactJS", "Next.js", "Angular", "Vue", "Vue.js",
        "Svelte", "Redux", "HTML", "HTML5", "CSS", "CSS3", "Tailwind", "TailwindCSS",
        "Bootstrap", "Material-UI", "MUI", "WebAssembly"
    ],
    "Backend & APIs": [
        "FastAPI", "Flask", "Django", "Node.js", "Express", "Express.js",
        "NestJS", "Spring", "Spring Boot", "ASP.NET", "GraphQL", "REST API",
        "gRPC", "Microservices"
    ],
    "Databases & Caching": [
        "SQL", "MySQL", "PostgreSQL", "Postgres", "MongoDB", "SQLite", "Oracle",
        "Redis", "DynamoDB", "Cassandra", "Elasticsearch", "Firebase", "Supabase"
    ],
    "DevOps & Cloud": [
        "AWS", "Azure", "Google Cloud", "GCP", "Docker", "Kubernetes", "K8s",
        "CI/CD", "Git", "GitHub", "GitLab", "Terraform", "Ansible", "Linux", "Nginx"
    ],
    "AI, ML & Data Science": [
        "Machine Learning", "Deep Learning", "Artificial Intelligence", "AI",
        "PyTorch", "TensorFlow", "Pandas", "NumPy", "Scikit-Learn", "OpenCV",
        "NLP", "LLM", "LangChain", "Hugging Face"
    ],
    "Testing & Methodology": [
        "Jest", "Pytest", "Selenium", "Cypress", "Postman", "Agile", "Scrum", "Jira"
    ]
}

def extract_skills(text: str) -> list[str]:
    """Extract skills from text using regex boundary matching."""
    if not text:
        return []

    found_skills = set()
    # Pad text so string boundaries act as whitespace
    padded_text = f" {text} "

    for category, keywords in skills_db.items():
        for keyword in keywords:
            escaped = re.escape(keyword)
            # Fixed-width 1-character lookbehind and lookahead
            pattern = rf"(?i)(<=[\s,.\(\)\[\]/:\-;]|^){escaped}"
            # Standard boundary regex for alphanumeric, custom lookaround for C++/C#/etc.
            if keyword in ["C++", "C#", ".NET"]:
                pattern = rf"(?i)(?<=\s){escaped}(?=[\s,.\(\)\[\]/:\-;]|$)"
            else:
                pattern = rf"(?i)(?<=[^a-zA-Z0-9_]|^){escaped}" if len(keyword) == 1 else rf"(?i)\b{escaped}\b"

            try:
                if re.search(pattern, text):
                    found_skills.add(keyword)
            except Exception:
                if re.search(rf"(?i)\b{escaped}\b", text):
                    found_skills.add(keyword)

    return sorted(list(found_skills))


