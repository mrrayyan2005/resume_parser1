from flask import Flask, render_template, request
import re
from pdfminer.high_level import extract_text
import spacy
from spacy.matcher import Matcher

app = Flask(__name__)

def extract_text_from_pdf(pdf_file):
    text = extract_text(pdf_file.stream)  # Read the content of the file stream
    return text


def extract_contact_number_from_resume(text):
    contact_number = None
    pattern = r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
    match = re.search(pattern, text)
    if match:
        contact_number = match.group()
    return contact_number

def extract_email_from_resume(text):
    email = None
    pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    match = re.search(pattern, text)
    if match:
        email = match.group()
    return email

# Define a dictionary of skills
skill_dataset = {
    'Python', 'Data Analysis', 'Machine Learning', 'Communication', 'Project Management',
    'Deep Learning', 'SQL', 'Tableau', 'Java', 'C++', 'JavaScript', 'HTML', 'CSS', 
    'React', 'Angular', 'Node.js', 'Photoshop', 'Illustrator', 'UI/UX Design', 'Graphic Design',
    'Web Design', 'Adobe Creative Suite', 'Sketch', 'InDesign', 'Prototyping', 'User Interface Design'
}

def extract_skills_from_resume(text, skill_dataset):
    # Initialize an empty set to store extracted skills
    extracted_skills = set()

    # Convert text to lowercase for case-insensitive matching
    text_lower = text.lower()

    # Loop through each skill in the dataset
    for skill in skill_dataset:
        # Check if the skill keyword is present in the text (case-insensitive)
        if skill.lower() in text_lower:
            extracted_skills.add(skill)

    return extracted_skills

def extract_education_from_resume(text):
    education = []

    # Define patterns to extract education information
    patterns = [
        r'(?i)(?:BE|B\.?Eng|Bachelor(?:\'?s)?(?:\sDegree)?)(?:\s(?:in|of)\s|\s)?(?:\w+\s)*\w+(?:\sEngineering)?',
        r'(?i)\b[A-Z]{2,} College(?:\sof\s\w+)?(?:\sEngineering\sand\sTechnology)?\b',
        r'\d{4}\s?–\s?\d{4}\s?\|\s?.*?,\s?.*?\b'
    ]

    # Search for education information using each pattern
    for pattern in patterns:
        matches = re.findall(pattern, text)
        # Exclude unwanted phrases
        matches = [match for match in matches if not any(unwanted_phrase in match for unwanted_phrase in ['ber of packets sent by', 'be blocked by'])]
        education.extend(matches)

    # Clean up the extracted education information
    education = [item.strip() for item in education]

    return education

    



def extract_name(resume_text):
    nlp = spacy.load('en_core_web_sm')
    matcher = Matcher(nlp.vocab)
    patterns = [
        [{'POS': 'PROPN'}, {'POS': 'PROPN'}],
        [{'POS': 'PROPN'}, {'POS': 'PROPN'}, {'POS': 'PROPN'}],
        [{'POS': 'PROPN'}, {'POS': 'PROPN'}, {'POS': 'PROPN'}, {'POS': 'PROPN'}]
    ]
    for pattern in patterns:
        matcher.add('NAME', patterns=[pattern])
    doc = nlp(resume_text)
    matches = matcher(doc)
    for match_id, start, end in matches:
        span = doc[start:end]
        return span.text
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    resume_file = request.files['resume']
    if resume_file:
        text = extract_text_from_pdf(resume_file)
        name = extract_name(text)
        contact_number = extract_contact_number_from_resume(text)
        email = extract_email_from_resume(text)
        extracted_skills = extract_skills_from_resume(text, skill_dataset)

        extracted_education = extract_education_from_resume(text)
        return render_template('result.html', name=name, contact_number=contact_number, email=email, skills=extracted_skills, education=extracted_education)
    else:
        return "No file uploaded"

if __name__ == '__main__':
    app.run(debug=True)
