import spacy
import pdfplumber
import re
from flask import Flask, request, jsonify

app = Flask(__name__)

# nlp = spacy.load("en_core_web_sm")
BIAS_TERMS = ["male", "female", "single", "married", "dob", "age", "citizen", "nationality", "religion"]

def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def remove_bias(text):
    for term in BIAS_TERMS:
        text = re.sub(rf"\b{term}\b", "", text, flags=re.IGNORECASE)
    return text

@app.route("/parse_resume", methods=["POST"])
def parse_resume():
    file = request.files["resume"]
    pdf_path = f"./uploads/{file.filename}"
    file.save(pdf_path)

    text = extract_text_from_pdf(pdf_path)
    clean_text = remove_bias(text)
    
    # doc = nlp(clean_text)
    skills = [ent.text for ent in clean_text.ents if ent.label_ == "SKILL"]
    experience = [ent.text for ent in clean_text.ents if ent.label_ in ["WORK_OF_ART", "ORG"]]

    return jsonify({"text": clean_text, "skills": list(set(skills)), "experience": list(set(experience))})

if __name__ == "__main__":
    app.run(debug=True)
