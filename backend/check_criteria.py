import re
from flask import Flask, request, jsonify

app = Flask(__name__)

def check_criteria(resume_data, job_criteria):
    required_skills = set(job_criteria["skills"])
    min_marks = job_criteria["min_marks"]
    
    candidate_skills = set(resume_data["skills"])
    skill_match = required_skills.intersection(candidate_skills)
    skill_gap = required_skills - candidate_skills

    marks_pattern = r"\b(\d+\.\d+)\b"
    extracted_marks = re.findall(marks_pattern, resume_data["text"])
    candidate_marks = max(map(float, extracted_marks)) if extracted_marks else 0

    category = "Suitable ✅" if len(skill_match) == len(required_skills) and candidate_marks >= min_marks else \
               "Less Suitable ⚠️" if candidate_marks >= min_marks else "Not Eligible ❌"

    return category, skill_match, skill_gap, candidate_marks

@app.route("/check_criteria", methods=["POST"])
def api_check_criteria():
    data = request.json
    resume_data = data["resume"]
    job_criteria = data["job_criteria"]

    category, match, gap, marks = check_criteria(resume_data, job_criteria)

    return jsonify({"category": category, "skill_match": list(match), "skill_gap": list(gap), "marks": marks})

if __name__ == "__main__":
    app.run(debug=True)
