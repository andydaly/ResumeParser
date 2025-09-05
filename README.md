# Resume Parser API (Python + FastAPI + spaCy)

A FastAPI-powered web service that extracts structured data from resumes (CVs).  
It parses uploaded `.docx`, `.pdf`, or `.txt` resumes into clean JSON fields, making it easier to integrate candidate data into HR or recruitment systems.

---

## Features

- **Candidate Information**
  - Full name
  - Email
  - Phone number
  - LinkedIn & GitHub URLs

- **Work History**
  - Job title
  - Company
  - Start / End dates (with month + year support)
  - Description (responsibilities, achievements, technologies used)

- **Education**
  - Graduation date
  - Course
  - Result
  - Institution

- **Skills**
  - Extracted from resume text, matched against a curated skill list (`skills_esco.txt`)

- **Profiles**
  - Personal Profile (summary / about me)
  - Skills Profile (technical / computer skills section)

- **Achievements**
  - Extracts key awards or personal achievements

- **Raw Text**
  - Full resume text included in the JSON for reference

---

## Tech Stack

- [FastAPI](https://fastapi.tiangolo.com/) – modern Python web framework
- [spaCy](https://spacy.io/) – NLP engine for entity recognition
- [Uvicorn](https://www.uvicorn.org/) – ASGI server
- [dateparser](https://dateparser.readthedocs.io/) – flexible date extraction
- [python-docx](https://python-docx.readthedocs.io/) – `.docx` parsing
- [pypdf](https://pypi.org/project/pypdf/) – `.pdf` parsing
- [rapidfuzz](https://github.com/maxbachmann/RapidFuzz) – fuzzy text matching

---

## Running Locally

1. **Clone the repository**  
   ```bash
   git clone https://github.com/<your-username>/<your-repo>.git
   cd <your-repo>
   ```

2. **Create a virtual environment**  
   ```bash
   python -m venv env
   source env/bin/activate   # Linux / macOS
   env\Scripts\activate      # Windows
   ```

3. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the API**  
   ```bash
   uvicorn api.server:app --reload
   ```

5. Open your browser at:  
   [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) (Swagger UI)

---

## Example Usage

**POST /parse**  
Upload a resume file and receive structured JSON:

```json
{
  "candidate": {
    "name": "Jane Doe",
    "email": "jane.doe@email.com",
    "phone": "+44 7555 123456",
    "phone_other": "+353 871234567",
    "github_url": "https://github.com/janedoe",
    "linkedin_url": "https://www.linkedin.com/in/janedoe"
  },
  "education": [
    {
      "graduation_date": "2015",
      "course": "Computer Science",
      "result": "BSc. 2.1 Honours",
      "institution": "Institute of Technology"
    }
  ],
  "experience": [
    {
      "title": "Software Developer",
      "company": "Some Company",
      "start_date": "2020-01",
      "end_date": "2025-01",
      "description": "Developed new features..."
    }
  ],
  "skills": ["C#", "Python", "Docker", "Azure", "SQL"],
  "profile": "Results-driven Software Developer...",
  "skills_profile": "Computer Programming (C, C++, Java, ...)",
  "achievements": [
    "Won a Prize"
  ],
  "raw_text": "Full resume text here..."
}
```

---

## Project Structure

```
repo/
│
├── api/
│   └── server.py            # FastAPI entry point
│
├── parser_app/
│   ├── sectioning.py        # Resume section splitter
│   ├── extractors.py        # Candidate + skill extractors
│   ├── work_history.py      # Work experience parser
│   ├── education.py         # Education parser
│   ├── simple_sections.py   # Profile, Achievements, Skills Profile
│   └── schema.py            # Pydantic models
│
├── skills_esco.txt          # Master skill dictionary
├── requirements.txt
└── README.md

---

## Contributing

Pull requests are welcome! If you’d like to add new parsers (e.g., certifications, publications), feel free to open an issue first to discuss.
