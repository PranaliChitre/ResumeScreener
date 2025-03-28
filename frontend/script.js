async function processResumes() {
    const jobDescription = document.getElementById("job-description").value;
    const requiredSkills = document.getElementById("required-skills").value.split(",");
    const minMarks = parseFloat(document.getElementById("min-marks").value);
    const numCandidates = parseInt(document.getElementById("num-candidates").value);
    const resumes = document.getElementById("resume-upload").files;

    if (!jobDescription || !requiredSkills.length || isNaN(minMarks) || isNaN(numCandidates) || resumes.length === 0) {
        alert("Please fill all fields and upload at least one resume!");
        return;
    }

    let resultsDiv = document.getElementById("results");
    resultsDiv.innerHTML = "<p>Processing resumes...</p>";

    let candidates = [];

    for (let file of resumes) {
        let formData = new FormData();
        formData.append("resume", file);

        // Step 1: Parse Resume
        let resumeResponse = await fetch("http://127.0.0.1:5000/parse_resume", {
            method: "POST",
            body: formData
        });

        let resumeData = await resumeResponse.json();

        // Step 2: Check Criteria
        let criteriaResponse = await fetch("http://127.0.0.1:5000/check_criteria", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ resume: resumeData, job_criteria: { skills: requiredSkills, min_marks: minMarks } })
        });

        let criteriaData = await criteriaResponse.json();

        // Step 3: Check GitHub (if available)
        let githubInfo = { projects: 0, stars: 0, top_repo: "N/A" };
        let githubLinkMatch = resumeData.text.match(/https:\/\/github\.com\/[^\s]+/);

        if (githubLinkMatch) {
            let githubResponse = await fetch("http://127.0.0.1:5000/analyze_github", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ github_url: githubLinkMatch[0] })
            });

            githubInfo = await githubResponse.json();
        }

        // Step 4: Predict Fit using Groq
        let predictResponse = await fetch("http://127.0.0.1:5000/evaluate_candidate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                resume: resumeData,
                job_description: jobDescription,
                github_data: githubInfo
            })
        });

        let predictData = await predictResponse.json();

        candidates.push({ name: file.name, criteria: criteriaData, github: githubInfo, evaluation: predictData.evaluation });
    }

    // Display Results
    resultsDiv.innerHTML = "<h4>Candidate Rankings:</h4>";
    candidates.forEach((candidate, index) => {
        resultsDiv.innerHTML += `
            <div>
                <h5>${index + 1}. ${candidate.name}</h5>
                <p><b>Category:</b> ${candidate.criteria.category}</p>
                <p><b>Skill Match:</b> ${candidate.criteria.skill_match.join(", ")}</p>
                <p><b>Skill Gap:</b> ${candidate.criteria.skill_gap.join(", ")}</p>
                <p><b>GitHub Projects:</b> ${candidate.github.projects}, <b>Stars:</b> ${candidate.github.stars}</p>
                <p><b>Evaluation Summary:</b> ${candidate.evaluation}</p>
            </div><hr>`;
    });
}
