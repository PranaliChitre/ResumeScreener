from flask import Flask, request, jsonify
from parse_resume import parse_resume
from check_criteria import check_criteria
from analyze_github import fetch_github_data
from predict_fit import evaluate_candidate

import re

app = Flask(__name__)

@app.route("/parse_resume", methods=["POST"])
def parse_resume():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON or empty request"}), 400

        resume_text = data.get("resume", {}).get("text", "")
        if not resume_text:
            return jsonify({"error": "Missing resume text"}), 400

        # Process the resume...
        return jsonify({"message": "Resume processed successfully!"})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route("/check_criteria", methods=["POST"])
def check_criteria_endpoint():
    """API to Check if Resume Meets Job Criteria"""
    try:
        data = request.json
        resume_text = data["resume"]["text"]
        job_criteria = data["job_criteria"]

        meets_criteria, skill_gaps = check_criteria(resume_text, job_criteria["skills"], job_criteria["min_marks"])
        return jsonify({"category": "Suitable ✅" if meets_criteria else "Less Suitable ⚠️", "skill_match": job_criteria["skills"], "skill_gap": skill_gaps})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/analyze_github", methods=["POST"])
def analyze_github_endpoint():
    """API to Analyze GitHub Profile (if available)"""
    try:
        data = request.json
        github_url = data["github_url"]

        if not github_url:
            return jsonify({"error": "No GitHub URL provided"}), 400

        github_data = fetch_github_data(github_url)
        return jsonify(github_data)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/evaluate_candidate", methods=["POST"])
def evaluate_candidate_endpoint():
    """API to Evaluate Candidate Using Groq API"""
    try:
        data = request.json
        resume_text = data["resume"]["text"]
        job_description = data["job_description"]
        github_data = data.get("github_data", {})

        evaluation = evaluate_candidate(resume_text, job_description, github_data)
        return jsonify({"evaluation": evaluation})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/")
def home():
    """Health Check Endpoint"""
    return jsonify({"message": "Resume Screening AI Backend is running!"})


if __name__ == "__main__":
    app.run(debug=True)
