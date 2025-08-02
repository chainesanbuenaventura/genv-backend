## API Usage

### User Specific Inputs

These are inputs specific to the user and chat session

```bash

    curl -i -X POST https://lexa-backend-xidw.vercel.app/ingest \
  -H "Content-Type: application/json" \
  -d '[
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": {
          "Candidate name": "Bohan LI",
          "Email": "bohanli9@outlook.com",
          "Skills": [
            "Statistics & Econometrics",
            "Deep learning",
            "Machine learning",
            "NLP & Applications",
            "Data mining (R)",
            "CRM",
            "NoSQL data processing",
            "Business Intelligence (BI)",
            "Big Data (Hadoop)",
            "Software Engineering",
            "Project Management",
            "Java",
            "C",
            "Web Programming",
            "Databases",
            "Digital Marketing",
            "Advanced Mathematics",
            "Statistics",
            "Python (Advanced)",
            "R (Advanced)",
            "SQL Server",
            "PostgreSQL",
            "MongoDB",
            "Neo4j",
            "JavaScript",
            "HTML",
            "CSS",
            "PHP",
            "XML",
            "JQuery",
            "Bootstrap",
            "Linux Scripting",
            "Excel",
            "Power BI (Advanced)",
            "Tableau",
            "Eclipse",
            "RStudio",
            "WordPress",
            "Databricks",
            "Snowflake",
            "Google Cloud Platform",
            "Microsoft Azure"
          ],
          "Experience": [
            {
              "company": "Infopro digital",
              "title": "Data scientist et Analyste Web",
              "years": "09/2022-09/2023"
            },
            {
              "company": "CMR Group",
              "title": "Analyste de BI et Développeur de python",
              "years": "08/2021-09/2022"
            },
            {
              "company": "Energyzon Group",
              "title": "Développeur de web",
              "years": "04/2021-07/2021"
            },
            {
              "company": "Interlart",
              "title": "Chef de Projet informatique",
              "years": "05/2020-07/2020"
            }
          ]
        }
      }
    }
  ]'

```

```bash
curl -i -H "Accept: application/json" http://127.0.0.1:8000/candidates
```

```bash
curl -i \
  -H "Accept: application/json" \
  https://lexa-backend-xidw.vercel.app/candidates
```

```bash
curl -i -X POST http://127.0.0.1:8000/ingest_job \
  -H "Content-Type: application/json" \
  -d @- <<'EOF'
[
  {
    "index": 0,
    "message": {
      "role": "assistant",
      "content": {
        "job_title": "Machine Learning Engineer",
        "company": "Outgoing",
        "location": "Greater Paris Metropolitan Region",
        "contract_type": null,
        "remote": true,
        "salary_range": { "min": null, "max": null },
        "responsibilities": [
          "Implementing & Optimizing LLM-Powered Features: Integrate and fine-tune open-source…",
          "Developing Advanced Ranking & Recommendation Algorithms: Design and implement…",
          "Owning End-to-End Development of Scalable Platforms: Take full ownership…",
          "Driving Technical Architecture & Tooling Decisions: Contribute significantly…"
        ],
        "requirements": [
          "5+ years of hands-on engineering experience…",
          "Proven hands-on experience applying LLMs in production…",
          "Strong familiarity with ranking algorithms…",
          "Proficiency with Python, FastAPI, GCP, and various databases."
        ],
        "nice_to_have": [ "Experience with Flutter, Node.js, Rust" ],
        "description": "Shape the Future of Real-World Experiences with AI\n\nAre you…"
      }
    }
  }
]
EOF
```

```bash
curl -i -X POST https://lexa-backend-xidw.vercel.app/ingest_job \
  -H "Content-Type: application/json" \
  -d @- <<'EOF'
[
  {
    "index": 0,
    "message": {
      "role": "assistant",
      "content": {
        "job_title": "Machine Learning Engineer",
        "company": "Outgoing",
        "location": "Greater Paris Metropolitan Region",
        "contract_type": null,
        "remote": true,
        "salary_range": { "min": null, "max": null },
        "responsibilities": [
          "Implementing & Optimizing LLM-Powered Features: Integrate and fine-tune open-source…",
          "Developing Advanced Ranking & Recommendation Algorithms: Design and implement…",
          "Owning End-to-End Development of Scalable Platforms: Take full ownership…",
          "Driving Technical Architecture & Tooling Decisions: Contribute significantly…"
        ],
        "requirements": [
          "5+ years of hands-on engineering experience…",
          "Proven hands-on experience applying LLMs in production…",
          "Strong familiarity with ranking algorithms…",
          "Proficiency with Python, FastAPI, GCP, and various databases."
        ],
        "nice_to_have": [ "Experience with Flutter, Node.js, Rust" ],
        "description": "Shape the Future of Real-World Experiences with AI\n\nAre you…"
      }
    }
  }
]
EOF
```

[
  {
    "index": 0,
    "message": {
      "role": "assistant",
      "content": {
        "job_title": "{{ $json.message.content.job_title }}",
        "company": "{{ $json.message.content.company }}",
        "location": "{{ $json.message.content.location }}",
        "contract_type": {{ $json.message.content.contract_type }},
        "remote": {{ $json.message.content.remote }},
        "salary_range": {
          "min": {{ $json.message.content.salary_range.min }},
          "max": {{ $json.message.content.salary_range.max }}
        },
        "responsibilities": {{ JSON.stringify($json.message.content.responsibilities) }},
        "requirements": {{ JSON.stringify($json.message.content.requirements) }},
        "nice_to_have": {{ JSON.stringify($json.message.content.nice_to_have[0]) }},
        "description": "{{ $json.message.content.description }}"
      }
    }
  }
] 


curl -X POST http://localhost:8000/ingest_campaign \
  -H "Content-Type: application/json" \
  --data-binary @- << 'EOF'
[
  {
    "index": 0,
    "message": {
      "role": "assistant",
      "content": {
        "core": {
          "job_title": "Machine Learning Engineer",
          "company_name": "Outgoing",
          "location": "Greater Paris Metropolitan Region",
          "contract_type": "Full-time",
          "seniority_level": null,
          "salary_range": { "min": null, "max": null, "currency": null },
          "job_description": "As an early team member, you'll directly shape Outgoing's core product. This is hands-on, applied AI, not theoretical research: We need engineers fluent in implementing and experimenting with the fast-evolving open-source LLM space, ready to operate at startup velocity, on a consumer-facing product.",
          "responsibilities": [
            "Integrate and fine-tune open-source Large Language Models (LLMs) to enhance natural language understanding, content generation, and conversational interfaces",
            "Design and implement generative and traditional ML to deliver highly personalized and contextually relevant activity suggestions",
            "Take full ownership of key features from concept to deployment, developing robust systems that ensure high performance, scalability, and reliability in a fast-paced environment",
            "Contribute significantly to strategic technical decisions, including system architecture, technology stack, and platform evolution"
          ],
          "requirements": [
            "5+ years of hands-on engineering experience scaling complex, user-facing products",
            "Proven hands-on experience applying Large Language Models (LLMs) in production environments, ideally including fine-tuning and quantizing open-weight models (e.g. Gemma, Llama, Qwen)",
            "Strong familiarity with ranking algorithms and recommendation systems, with experience in their design, implementation, and optimization",
            "Proficiency with Python (including Pydantic), modern backend frameworks like FastAPI, Google Cloud Platform (GCP), and relational, NoSQL, vector, and graph databases",
            "Bonus: Experience with Flutter, Node.js, Rust"
          ],
          "application_link": null
        },
        "enrichment": {
          "skills": [
            { "name": "Python", "mastery": null },
            { "name": "Pydantic", "mastery": null },
            { "name": "FastAPI", "mastery": null },
            { "name": "Google Cloud Platform", "mastery": null },
            { "name": "LLMs", "mastery": null },
            { "name": "Flutter", "mastery": null },
            { "name": "Node.js", "mastery": null },
            { "name": "Rust", "mastery": null },
            { "name": "ranking algorithms", "mastery": null },
            { "name": "recommendation systems", "mastery": null }
          ],
          "languages": [
            { "name": "English", "mastery": null }
          ],
          "work_mode": "remote",
          "team_department": null,
          "company_description": "Outgoing is a dynamic AI startup based in Paris, founded by seasoned entrepreneurs. They are building an AI-powered concierge that helps people discover, plan, and enjoy real-world activities.",
          "benefits_perks": ["Competitive salary", "Equity"],
          "seniority_tags": [],
          "education_requirements": [],
          "travel_requirements": []
        },
        "advanced": {
          "application_steps": [],
          "job_function": "Engineering",
          "industry_sector": "Artificial Intelligence",
          "remote_time_zone": "European time zone",
          "equity_bonus_info": "Equity",
          "recruiter_contact": null,
          "estimated_team_size": "11-50"
        }
      }
    }
  }
]
EOF

curl -X POST https://lexa-backend-xidw.vercel.app/ingest_campaign \
  -H "Content-Type: application/json" \
  --data-binary @- << 'EOF'
[
  {
    "index": 0,
    "message": {
      "role": "assistant",
      "content": {
        "core": {
          "job_title": "Machine Learning Engineer",
          "company_name": "Outgoing",
          "location": "Greater Paris Metropolitan Region",
          "contract_type": "Full-time",
          "seniority_level": null,
          "salary_range": { "min": null, "max": null, "currency": null },
          "job_description": "As an early team member, you'll directly shape Outgoing's core product. This is hands-on, applied AI, not theoretical research: We need engineers fluent in implementing and experimenting with the fast-evolving open-source LLM space, ready to operate at startup velocity, on a consumer-facing product.",
          "responsibilities": [
            "Integrate and fine-tune open-source Large Language Models (LLMs) to enhance natural language understanding, content generation, and conversational interfaces",
            "Design and implement generative and traditional ML to deliver highly personalized and contextually relevant activity suggestions",
            "Take full ownership of key features from concept to deployment, developing robust systems that ensure high performance, scalability, and reliability in a fast-paced environment",
            "Contribute significantly to strategic technical decisions, including system architecture, technology stack, and platform evolution"
          ],
          "requirements": [
            "5+ years of hands-on engineering experience scaling complex, user-facing products",
            "Proven hands-on experience applying Large Language Models (LLMs) in production environments, ideally including fine-tuning and quantizing open-weight models (e.g. Gemma, Llama, Qwen)",
            "Strong familiarity with ranking algorithms and recommendation systems, with experience in their design, implementation, and optimization",
            "Proficiency with Python (including Pydantic), modern backend frameworks like FastAPI, Google Cloud Platform (GCP), and relational, NoSQL, vector, and graph databases",
            "Bonus: Experience with Flutter, Node.js, Rust"
          ],
          "application_link": null
        },
        "enrichment": {
          "skills": [
            { "name": "Python", "mastery": null },
            { "name": "Pydantic", "mastery": null },
            { "name": "FastAPI", "mastery": null },
            { "name": "Google Cloud Platform", "mastery": null },
            { "name": "LLMs", "mastery": null },
            { "name": "Flutter", "mastery": null },
            { "name": "Node.js", "mastery": null },
            { "name": "Rust", "mastery": null },
            { "name": "ranking algorithms", "mastery": null },
            { "name": "recommendation systems", "mastery": null }
          ],
          "languages": [
            { "name": "English", "mastery": null }
          ],
          "work_mode": "remote",
          "team_department": null,
          "company_description": "Outgoing is a dynamic AI startup based in Paris, founded by seasoned entrepreneurs. They are building an AI-powered concierge that helps people discover, plan, and enjoy real-world activities.",
          "benefits_perks": ["Competitive salary", "Equity"],
          "seniority_tags": [],
          "education_requirements": [],
          "travel_requirements": []
        },
        "advanced": {
          "application_steps": [],
          "job_function": "Engineering",
          "industry_sector": "Artificial Intelligence",
          "remote_time_zone": "European time zone",
          "equity_bonus_info": "Equity",
          "recruiter_contact": null,
          "estimated_team_size": "11-50"
        }
      }
    }
  }
]
EOF