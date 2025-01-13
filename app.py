from flask import Flask, render_template, request, jsonify
import os
import PyPDF2
import docx
import spacy
from spacy.matcher import PhraseMatcher
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load spaCy language model
nlp = spacy.load("en_core_web_sm")

# Expanded list of example skills to extract from resumes
skills_list = [
    "Python", "SQL", "Java", "JavaScript", "HTML", "CSS", "R",
    "TensorFlow", "PyTorch", "Machine Learning", "Deep Learning",
    "Data Science", "NLP", "Flask", "Django", "Keras", "Pandas",
    "NumPy", "Scikit-Learn", "AI", "Artificial Intelligence", "Cloud",
    "AWS", "Azure", "DevOps", "MLOps", "CI/CD", "Git", "Node.js",
    "React", "Docker", "Android", "Swift", "Kotlin", "Ruby", "Go",
    "PHP", "C#", "Scala", "Big Data", "Hadoop", "Spark", "Tableau",
    "Excel", "Power BI", "Selenium", "Jest", "Agile", "UX/UI", "UI/UX Design",
    "Cloud Computing", "Jupyter", "Matplotlib", "Seaborn", "GitHub", "Linux"
]
matcher = PhraseMatcher(nlp.vocab)
patterns = [nlp(skill.lower()) for skill in skills_list]
matcher.add("SKILLS", None, *patterns)

# Expanded job descriptions dataset
job_descriptions = {
    "Data Scientist": "Analyze large datasets using statistical and machine learning techniques. Skills in Python, R, and SQL.",
    "Software Engineer": "Design and maintain software. Proficient in programming languages like Java, C++, or Python.",
    "Web Developer": "Build and maintain websites. Knowledge of HTML, CSS, JavaScript, and frameworks.",
    "AI Engineer": "Develop machine learning and AI solutions. Deep learning experience required.",
    "Data Analyst": "Interpret data to provide insights. Proficiency in Excel, SQL, and data visualization.",
    "Mobile App Developer": "Develop mobile apps for Android and iOS. Familiar with Kotlin, Swift, and React Native.",
    "Cloud Engineer": "Manage cloud services like AWS, Azure, or Google Cloud. Cloud deployment expertise.",
    "Digital Marketing Specialist": "Create digital marketing strategies. Knowledge of SEO and social media marketing.",
    "Project Manager": "Manage projects across teams. Skilled in project management methodologies.",
    "Sales Manager": "Develop and lead sales strategies. Strong negotiation and communication skills.",
    "Business Analyst": "Analyze business processes and data. Requires analytical and data visualization skills.",
    "Product Manager": "Oversee product development and management. Strong leadership and critical thinking.",
    "Network Engineer": "Manage network systems and connectivity. Proficiency in networking and troubleshooting.",
    "HR Specialist": "Manage recruitment and employee relations. Strong interpersonal and organizational skills.",
    "UI/UX Designer": "Design user interfaces and experiences. Knowledge of design tools and user research.",
    "Financial Analyst": "Analyze financial data to support decision-making. Requires financial modeling skills.",
    "Brand Manager": "Oversee brand strategies and campaigns. Strong understanding of brand management.",
    "Content Writer": "Develop content for marketing. Proficient in writing, editing, and SEO.",
    "Data Engineer": "Build and maintain data pipelines. Familiarity with SQL, ETL processes, and big data.",
    "Cybersecurity Analyst": "Protect systems from cyber threats. Knowledge of cybersecurity tools and protocols."
}

def extract_text_from_pdf(filepath):
    with open(filepath, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
        return text

def extract_text_from_docx(filepath):
    doc = docx.Document(filepath)
    text = '\n'.join([para.text for para in doc.paragraphs])
    return text

def extract_skills(text):
    doc = nlp(text.lower())
    matches = matcher(doc)
    skills = set()
    for match_id, start, end in matches:
        skills.add(doc[start:end].text.title())
    return list(skills)

def extract_experience(text):
    # Simple keyword search to extract experience-related sentences
    experience_keywords = ['experience', 'internship', 'role', 'position', 'worked', 'responsibilities']
    sentences = text.split('\n')
    experience_data = []
    for sentence in sentences:
        if any(keyword in sentence.lower() for keyword in experience_keywords):
            experience_data.append(sentence.strip())
    return "\n".join(experience_data) if experience_data else "No clear experience section found."

def preprocess_resume(text):
    doc = nlp(text)
    tokens = [token.lemma_.lower() for token in doc if not token.is_stop and not token.is_punct]
    return ' '.join(tokens)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['resume']
        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)

            # Extract text
            if file.filename.endswith('.pdf'):
                resume_text = extract_text_from_pdf(filepath)
            elif file.filename.endswith('.docx'):
                resume_text = extract_text_from_docx(filepath)
            else:
                resume_text = None

            if resume_text:
                processed_resume = preprocess_resume(resume_text)

                # Recommend job and extract skills & experience
                recommended_job, skills, experience = recommend_jobs(processed_resume)

                return jsonify({
                    "recommended_job": recommended_job,
                    "skills": skills,
                    "experience": experience
                })

    return render_template('index.html')

def recommend_jobs(resume_text):
    skills = extract_skills(resume_text)
    experience = extract_experience(resume_text)  # Extract experience
    documents = [resume_text] + list(job_descriptions.values())

    # TF-IDF
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents)

    # cosine similarity
    cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

    # job description
    recommended_index = cosine_sim.argmax()
    recommended_job = list(job_descriptions.keys())[recommended_index]

    return recommended_job, skills, experience

if __name__ == "__main__":
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    app.run(debug=True)