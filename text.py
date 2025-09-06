import re
import json
import pdfplumber   
import docx
import spacy
import pandas as pd

nlp = spacy.load("en_core_web_sm")

def extract_text(file_path):
    text = ""
    if file_path.endswith(".pdf"):
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
    elif file_path.endswith(".docx"):
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    elif file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
    else:
        raise ValueError("Unsupported file format")
    return text


def clean_text(text):
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)  
    return text.strip()

def extract_email(text):
    matches = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    return matches[0] if matches else None

def extract_phone(text):
    matches = re.findall(r"\+?\d[\d\s-]{8,13}\d", text)
    return matches[0] if matches else None

def extract_links(text):
    return re.findall(r"(https?:\/\/\S+)", text)

def extract_skills(text):
    skills_df = pd.read_csv("skills_list_clean.csv")
    skill_set = [s.strip().lower() for s in skills_df["Skill"].dropna().tolist()]
    
    text = text.lower()
    
    found = []
    for skill in skill_set:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, text):
            found.append(skill.title())
    
    return sorted(set(found))  

def process_resume(file_path):
    raw_text = extract_text(file_path)
    cleaned_text = clean_text(raw_text)

    email = extract_email(cleaned_text)
    phone = extract_phone(cleaned_text)
    links = extract_links(cleaned_text)
    skills = extract_skills(cleaned_text)

    resume_data = {
        "email": email,
        "phone": phone,
        "links": links,
        "skills": skills
    }

    return resume_data

if __name__ == "__main__":
    file_path = "Khushi_Gupta.pdf"
    data = process_resume(file_path)
    print(json.dumps(data, indent=4))
