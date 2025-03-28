import requests
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

def fetch_github_data(github_url):
    username = github_url.split("/")[-1]
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    repos_url = f"https://api.github.com/users/{username}/repos"
    response = requests.get(repos_url, headers=headers)
    
    if response.status_code == 200:
        repos = response.json()
        project_count = len(repos)
        stars = sum(repo["stargazers_count"] for repo in repos)
        top_repo = max(repos, key=lambda x: x["stargazers_count"], default={}).get("name", "No projects")
        
        return {"projects": project_count, "stars": stars, "top_repo": top_repo}
    return {"error": "GitHub profile not found"}

@app.route("/analyze_github", methods=["POST"])
def api_analyze_github():
    github_url = request.json["github_url"]
    github_data = fetch_github_data(github_url)
    return jsonify(github_data)

if __name__ == "__main__":
    app.run(debug=True)
