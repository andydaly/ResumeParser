from fastapi import FastAPI, UploadFile, File
from parser_app.io_loaders import load_text
from parser_app.sectioning import split_sections
from parser_app.extractors import (
    extract_email, 
    extract_phone, 
    guess_name,
    load_skill_list, 
    extract_skills,
    extract_github_url, 
    extract_linkedin_url,
    extract_phone_numbers,         
)
from parser_app.work_history import parse_experience_from_whole_text
from parser_app.education import parse_education_section
from parser_app.simple_sections import extract_profile, parse_achievements, parse_skills_profile, get_section_text
from parser_app.schema import Resume, Candidate, Experience, Education
import os, tempfile, shutil

app = FastAPI(title="Resume Parser API")

SKILLS_PATH = os.path.join(os.path.dirname(__file__), "..", "parser_app", "skills", "skills_esco.txt")
SKILLS = load_skill_list(SKILLS_PATH) if os.path.exists(SKILLS_PATH) else []

@app.post("/parse", response_model=Resume)
async def parse_resume(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
        shutil.copyfileobj(file.file, tmp)
        temp_path = tmp.name

    text = load_text(temp_path)
    sections = split_sections(text)

    email = extract_email(text)
    phones = extract_phone_numbers(text, default_regions=("GB","IE"))
    phone = phones[0] if phones else None
    phone_other = phones[1] if len(phones) > 1 else None
    name  = guess_name(text)
    github = extract_github_url(text)
    linkedin = extract_linkedin_url(text)
    skills = extract_skills(text, SKILLS) if SKILLS else []

    wh_items = parse_experience_from_whole_text(sections, text)
    experience = [
        Experience(
            title=item.title,
            company=item.company,
            start_date=item.start_date,
            end_date=item.end_date,
            description="\n".join(item.description_lines) if item.description_lines else None
        )
        for item in wh_items
    ]

    education = []
    if sections:
        for k, v in sections.items():
            if "education" in k.lower():
                education = parse_education_section(v)
                break

    profile = extract_profile(sections, text)

    achievements_text = get_section_text(sections, ["achievements", "awards"])
    achievements = parse_achievements(achievements_text) if achievements_text else []

    skills_profile_text = get_section_text(
        sections,
        ["computer skills profile", "technical skills profile", "computer skills"]
    )
    skills_profile = parse_skills_profile(skills_profile_text) if skills_profile_text else None

    return Resume(
        candidate=Candidate(
            name=name,
            email=email,
            phone=phone,
            phone_other=phone_other,
            github_url=github,
            linkedin_url=linkedin
        ),
        education=education,
        experience=experience,
        skills=skills,
        profile=profile,
        skills_profile=skills_profile,
        achievements=achievements,
        raw_text=text
    )
