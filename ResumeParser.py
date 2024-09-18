import fitz  # PyMuPDF for PDF parsing
import spacy
import subprocess
import sys
import re
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st

# Function to install the spaCy model if not present
def install_spacy_model():
    subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])

# Try loading the 'en_core_web_sm' model; install it if it doesn't exist
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    install_spacy_model()
    nlp = spacy.load("en_core_web_sm")


# Dictionary of industry skills and focus areas
industry_skills = {
    "Accounting/Financial": [
        "budgeting", "financial analysis", "compliance", "QuickBooks", "Excel", "taxation",
        "auditing", "payroll management", "financial reporting", "cost accounting",
        "accounts payable", "accounts receivable", "bank reconciliation", "SAP",
        "financial modeling", "investment analysis", "forensic accounting", "risk management",
        "financial forecasting", "ERP systems", "GAAP", "accounting software", "Peachtree",
        "Xero", "tax planning", "variance analysis", "balance sheet", "income statement",
        "cash flow statement", "credit analysis", "hedge accounting", "IFRS"
    ],
    # Additional categories are omitted for brevity, but include all your industry skill categories here.
}


# Function to extract text from PDF
def extract_text_from_pdf(file):
    with fitz.open(stream=file.read(), filetype="pdf") as doc:
        text = ""
        for page in doc:
            text += page.get_text()
    return text


# Function to extract skills from the resume text using regex
def extract_skills(resume_text):
    skills_pattern = r"Skills(?:\n|:)(.*)"
    skills_match = re.search(skills_pattern, resume_text, re.DOTALL | re.IGNORECASE)

    if skills_match:
        skills_text = skills_match.group(1).strip()
        skills = re.split(r',|\n', skills_text)
        skills = [skill.strip() for skill in skills if skill]
        return skills
    else:
        return []


# Function to extract entities like job experience and education using spaCy
def extract_entities(resume_text):
    doc = nlp(resume_text)
    experience = []
    education = []
   
    for ent in doc.ents:
        if ent.label_ == "ORG":  # Organization, potentially job experience
            experience.append(ent.text)
        elif ent.label_ == "DATE":  # Dates, useful for education or experience
            education.append(ent.text)
   
    return experience, education


# Function to generate feedback based on selected industry
def generate_feedback(resume_skills, selected_industry):
    industry_relevant_skills = industry_skills[selected_industry]
    missing_skills = [skill for skill in industry_relevant_skills if skill.lower() not in [rs.lower() for rs in resume_skills]]
   
    if not missing_skills:
        return "Your resume matches well with the industry standards. Great job!"
    else:
        feedback = "Consider adding or emphasizing the following skills to match industry standards: " + ", ".join(missing_skills)
        return feedback


# Function to visualize skill matching with industry standards
def visualize_skills_comparison(resume_skills, selected_industry):
    industry_relevant_skills = industry_skills[selected_industry]
    matching_skills = [skill for skill in resume_skills if skill.lower() in [is_.lower() for is_ in industry_relevant_skills]]
   
    labels = ['Matching Skills', 'Missing Skills']
    sizes = [len(matching_skills), len(industry_relevant_skills) - len(matching_skills)]
   
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.title("Skill Match Overview")
    st.pyplot(fig)


# Streamlit UI
st.title("Resume Parsing and Industry Feedback Tool")


# Upload resume PDF
uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])


# Industry selection dropdown
industries = ["Accounting/Financial", "Engineering", "Hospitality", "Sciences", "Tech/Information Technology", "Education"]
selected_industry = st.selectbox("Select Your Industry", industries)


if uploaded_file is not None:
    # Extract text from the uploaded PDF
    resume_text = extract_text_from_pdf(uploaded_file)
   
    # Display the extracted text
    st.subheader("Extracted Resume Text:")
    st.text(resume_text)
   
    # Extract skills
    st.subheader("Extracted Skills:")
    skills = extract_skills(resume_text)
    if skills:
        st.write(skills)
    else:
        st.write("No skills found.")
   
    # Extract experience and education
    st.subheader("Extracted Experience and Education:")
    experience, education = extract_entities(resume_text)
    st.write("Experience: ", experience)
    st.write("Education: ", education)
   
    # Provide custom feedback for selected industry
    if skills:
        feedback = generate_feedback(skills, selected_industry)
        st.subheader("Custom Feedback for Your Industry:")
        st.write(feedback)
   
        # Visualize skill matching
        visualize_skills_comparison(skills, selected_industry)


# Option to download the extracted data as CSV (if skills were found)
if uploaded_file is not None and skills:
    st.subheader("Download Extracted Data")
    df = pd.DataFrame({"Skills": skills})
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Skills Data as CSV",
       
