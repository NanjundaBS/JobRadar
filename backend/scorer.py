import re
from typing import Optional

# Skills taxonomy — user's target skills
SKILL_GROUPS = {
    "cloud": ["aws", "gcp", "azure", "cloud", "ec2", "s3", "rds", "lambda", "eks", "ecs", "cloudformation"],
    "cicd": ["github actions", "jenkins", "ci/cd", "gitlab ci", "circleci", "github", "pipeline", "bitbucket"],
    "iac": ["terraform", "ansible", "cloudformation", "pulumi", "chef", "puppet"],
    "containers": ["docker", "kubernetes", "k8s", "helm", "containerd", "openshift", "podman"],
    "monitoring": [
        "prometheus", "grafana", "datadog", "elk", "kibana", "elasticsearch",
        "appdynamics", "splunk", "newrelic", "cloudwatch", "dynatrace"
    ],
    "artifacts": ["nexus", "artifactory", "jfrog", "tomcat", "maven", "gradle", "sonarqube"],
    "scripting": ["python", "bash", "shell", "go", "ruby", "powershell"],
    "networking": ["vpc", "load balancer", "nginx", "haproxy", "istio", "service mesh"],
}

HIGH_VALUE_SKILLS = [
    "aws", "terraform", "kubernetes", "docker", "github actions",
    "jenkins", "ansible", "prometheus", "grafana", "gcp", "helm", "eks"
]

TARGET_TITLES = [
    "devops", "aws devops", "cloud engineer", "platform engineer",
    "infrastructure engineer", "site reliability", "sre", "release engineer",
    "build engineer", "devsecops", "cloud ops", "devops engineer",
    "cloud devops", "aws cloud", "kubernetes engineer", "infrastructure"
]

EXCLUDE_TITLES = [
    "senior devops", "lead devops", "principal devops", "devops manager",
    "head of devops", "director", "vp engineering", "chief", "architect"
]

EXCLUDE_KEYWORDS = [
    "senior", "lead", "principal", "manager", "director", "head of",
    "vp ", "chief", "architect", "staff engineer"
]

JUNIOR_KEYWORDS = ["fresher", "entry level", "entry-level", "intern", "trainee", "0-1 year"]


def parse_experience(text: str) -> tuple[Optional[int], Optional[int]]:
    """Parse experience from text. Returns (min_years, max_years)."""
    if not text:
        return None, None
    text_lower = text.lower()

    # Check for exclusion by seniority title
    if any(kw in text_lower for kw in EXCLUDE_KEYWORDS):
        return 5, 99

    # Check for juniors
    if any(kw in text_lower for kw in JUNIOR_KEYWORDS):
        return 0, 1

    # Range: 2-4 years or 2 to 4 yrs
    m = re.search(r'(\d+)\s*[-–to]+\s*(\d+)\s*(?:years?|yrs?)', text_lower)
    if m:
        return int(m.group(1)), int(m.group(2))

    # 3+ years
    m = re.search(r'(\d+)\+\s*(?:years?|yrs?)', text_lower)
    if m:
        yr = int(m.group(1))
        return yr, yr + 3

    # N years experience / minimum N years
    m = re.search(r'(?:minimum|at\s*least|min)?\s*(\d+)\s*(?:years?|yrs?)', text_lower)
    if m:
        yr = int(m.group(1))
        return yr, yr

    return None, None


def is_experience_match(exp_text: str) -> bool:
    """Returns True if experience requirement matches 2-4 years profile."""
    min_yr, max_yr = parse_experience(exp_text)
    if min_yr is None:
        return True  # Unknown — keep it
    if max_yr is not None and max_yr < 2:
        return False  # Too junior (0-1 years)
    if min_yr is not None and min_yr >= 5:
        return False  # Too senior (5+ years)
    return True


def extract_matched_skills(text: str) -> list[str]:
    """Extract which target skills appear in job text."""
    text_lower = text.lower()
    matched = []
    for group_skills in SKILL_GROUPS.values():
        for skill in group_skills:
            if re.search(r'\b' + re.escape(skill) + r'\b', text_lower) and skill not in matched:
                matched.append(skill)
    return matched


def is_title_match(title: str) -> bool:
    """Check if job title matches target roles."""
    title_lower = title.lower()
    # Exclude senior/lead/principal
    if any(ex in title_lower for ex in EXCLUDE_KEYWORDS):
        return False
    if any(kw in title_lower for kw in JUNIOR_KEYWORDS):
        return False
    return any(t in title_lower for t in TARGET_TITLES)


def score_job(raw_job) -> tuple[int, list[str], str, bool]:
    """
    Score a job 0-100.
    Returns: (score, matched_skills, why_it_matches, passes_filter)
    """
    combined_text = f"{raw_job.title} {raw_job.description} {raw_job.experience_text}"

    # Title match check — primary filter
    title_ok = is_title_match(raw_job.title)
    if not title_ok:
        return 0, [], "", False

    # Experience filter
    exp_ok = is_experience_match(raw_job.experience_text or combined_text)
    if not exp_ok:
        return 0, [], "", False

    # Skill matching
    matched = extract_matched_skills(combined_text)

    score = 0

    # Title match: 25 points
    score += 25

    # Experience fit: up to 20 points
    min_yr, max_yr = parse_experience(raw_job.experience_text or combined_text)
    if min_yr is not None:
        if 2 <= min_yr <= 4:
            score += 20
        elif min_yr < 2 and max_yr and max_yr >= 2:
            score += 15
        elif min_yr < 5:
            score += 10
    else:
        score += 10  # Unknown — partial credit

    # Skill overlap: up to 40 points
    high_value_matches = [s for s in matched if s in HIGH_VALUE_SKILLS]
    all_group_matches = len(set(
        group for group, skills in SKILL_GROUPS.items()
        if any(s in matched for s in skills)
    ))
    skill_score = min(40, len(high_value_matches) * 6 + all_group_matches * 3)
    score += skill_score

    # Location bonus: up to 15 points
    location_lower = (raw_job.location or "").lower()
    india_cities = ["india", "bangalore", "bengaluru", "hyderabad", "pune",
                    "mumbai", "chennai", "delhi", "noida", "gurgaon", "gurugram", "remote"]
    if any(city in location_lower for city in india_cities):
        score += 15

    score = min(100, score)

    # Generate "why it matches" summary
    top_skills = high_value_matches[:3] or matched[:3]
    min_yr, max_yr = parse_experience(raw_job.experience_text or combined_text)
    exp_str = (
        f"{min_yr}–{max_yr} years" if min_yr is not None and max_yr is not None
        else f"{min_yr}+ years" if min_yr is not None
        else "experience not specified"
    )
    why = f"Matches your profile on {', '.join(top_skills[:3]) if top_skills else 'DevOps skills'}; requires {exp_str}."
    if all_group_matches >= 3:
        why += f" Covers {all_group_matches} of your skill areas."
    if "india" in location_lower or "remote" in location_lower:
        why += " India/Remote role."

    return score, matched, why, score >= 20


def filter_and_score_jobs(raw_jobs: list) -> list[dict]:
    """Filter and score a list of RawJob objects. Returns dicts of scored jobs, top 30."""
    results = []
    for job in raw_jobs:
        score, skills, why, passes = score_job(job)
        if passes:
            results.append({
                "raw_job": job,
                "score": score,
                "matched_skills": skills,
                "why_it_matches": why,
            })
    # Sort by score descending, return top 30
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:30]
