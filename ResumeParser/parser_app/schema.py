from pydantic import BaseModel, Field
from typing import List, Optional

class Education(BaseModel):
    graduation_date: Optional[str] = None
    course: Optional[str] = None
    result: Optional[str] = None
    institution: Optional[str] = None

class Experience(BaseModel):
    title: str
    company: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None

class Candidate(BaseModel):
    name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    phone_other: Optional[str] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None

class Resume(BaseModel):
    candidate: Candidate
    education: List[Education] = Field(default_factory=list)
    experience: List[Experience] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    profile: Optional[str] = None
    achievements: List[str] = Field(default_factory=list)
    skills_profile: Optional[str] = None
    raw_text: Optional[str] = None
