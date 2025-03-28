import os
import requests

# Load the Groq API key from environment variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Groq API URL
GROQ_API_URL = "https://api.groq.com/v1/chat/completions"

def evaluate_candidate(resume_text, job_description, extracted_info):
    """
    Uses the Groq API to analyze the candidate's resume text 
    and predict their fit for the given job description.
    
    :param resume_text: Parsed resume text (after bias removal)
    :param job_description: HR-provided job description
    :param extracted_info: Dictionary containing parsed details (experience, GitHub info, extra skills)
    :return: Dictionary containing ATS Score, Suitability Category, and a Summary
    """

    # Prompt for the Groq API
    prompt = f"""
    You are an advanced AI recruiter. Given a job description and a candidate's resume, evaluate their suitability.

    - Remove bias-related factors before analysis.
    - Compare skills, experience, and qualifications with job requirements.
    - If there are missing skills, highlight the gaps.
    - If the candidate has a GitHub profile, analyze the quality of their projects, collaborations, and activity.
    - Provide an ATS Score (0-100) based on alignment with the job description.
    - Categorize the candidate as:
        1. **Highly Suitable** (Excellent match)
        2. **Partially Suitable** (Meets criteria but lacks some skills)
        3. **Not Suitable** (Does not meet key criteria)
    - Generate a brief summary including:
        - Experience
        - GitHub Insights (if available)
        - ATS Score

    **Job Description:**  
    {job_description}

    **Candidate Resume (Processed):**  
    {resume_text}

    **Extracted Info:**  
    {extracted_info}
    """

    # API request payload
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "gpt-4",
        "messages": [{"role": "system", "content": "You are an AI resume evaluator."},
                     {"role": "user", "content": prompt}],
        "temperature": 0.3
    }

    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=payload)
        response_data = response.json()
        analysis = response_data.get("choices", [{}])[0].get("message", {}).get("content", "No response")

        return {
            "ATS_Score": extract_ats_score(analysis),
            "Category": extract_category(analysis),
            "Summary": analysis
        }

    except Exception as e:
        return {"error": str(e)}

def extract_ats_score(analysis_text):
    """Extracts the ATS Score from the response text."""
    import re
    match = re.search(r"ATS Score:\s*(\d+)", analysis_text)
    return int(match.group(1)) if match else None

def extract_category(analysis_text):
    """Extracts the suitability category from the response text."""
    if "Highly Suitable" in analysis_text:
        return "Highly Suitable ✅"
    elif "Partially Suitable" in analysis_text:
        return "Partially Suitable ⚠️ (Skill Gaps)"
    else:
        return "Not Suitable ❌"

