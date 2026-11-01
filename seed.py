"""
seed.py — Demo data for the Student Portfolio Management System.

Creates 2 demo engineering students with complete data in every module.
Safe to run multiple times: only demo accounts (email starts with seed_demo_)
are touched; real users are NEVER modified or deleted.

Usage:
    python seed.py

Output: login credentials and public portfolio URLs are printed to the terminal.
"""
import json
import sys
from datetime import date

# ---------------------------------------------------------------------------
# Bootstrap the Flask application context so models and db are available.
# ---------------------------------------------------------------------------
from app import create_app, db
from app.models import (
    Achievement, Certification, Education, Extracurricular,
    Internship, Profile, Project, Skill, User,
)
from app.utils import generate_unique_slug

DEMO_PASSWORD = "Demo@1234"
DEMO_EMAIL_MARKER = "seed_demo_"   # any email starting with this = demo account


# ---------------------------------------------------------------------------
# Demo student data (no LLM calls — bullets are pre-written manually)
# ---------------------------------------------------------------------------

STUDENTS = [
    # -----------------------------------------------------------------------
    # Student 1: Priya Sharma — BE Computer Engineering, Pune
    # -----------------------------------------------------------------------
    {
        "name": "Priya Sharma",
        "email": "seed_demo_priya@example.com",
        "profile": {
            "headline": "Final-year Computer Engineering student | Full-Stack & ML enthusiast",
            "phone": "+91-98765-43210",
            "location": "Pune, Maharashtra",
            "linkedin": "https://linkedin.com/in/priya-sharma-demo",
            "github": "https://github.com/priya-sharma-demo",
            "website": "https://priyasharma.example.com",
            "bio": (
                "I am a final-year Computer Engineering student at PICT, Pune, "
                "passionate about building scalable web applications and exploring "
                "machine learning. I enjoy solving real-world problems with clean, "
                "well-documented code and collaborating on open-source projects."
            ),
            "summary": (
                "Results-driven Computer Engineering student with hands-on experience in "
                "full-stack web development (Flask, React) and machine learning (scikit-learn, "
                "TensorFlow). Completed industry internships at two Pune-based product companies. "
                "Strong foundation in data structures, algorithms, and agile methodologies."
            ),
            "is_public": True,
        },
        "education": [
            {
                "level": "B.E. Computer Engineering",
                "institution": "Pune Institute of Computer Technology",
                "board_university": "Savitribai Phule Pune University",
                "start_year": 2021,
                "end_year": 2025,
                "score": "8.9 CGPA",
            },
            {
                "level": "Class XII (HSC)",
                "institution": "Fergusson College",
                "board_university": "Maharashtra State Board",
                "start_year": 2019,
                "end_year": 2021,
                "score": "93.4%",
            },
            {
                "level": "Class X (SSC)",
                "institution": "Vidya Valley School",
                "board_university": "Maharashtra State Board",
                "start_year": 2017,
                "end_year": 2019,
                "score": "97.2%",
            },
        ],
        "skills": [
            {"name": "Python", "category": "Programming Languages", "proficiency": "Expert"},
            {"name": "JavaScript", "category": "Programming Languages", "proficiency": "Advanced"},
            {"name": "C++", "category": "Programming Languages", "proficiency": "Intermediate"},
            {"name": "Flask", "category": "Frameworks & Libraries", "proficiency": "Advanced"},
            {"name": "React", "category": "Frameworks & Libraries", "proficiency": "Intermediate"},
            {"name": "scikit-learn", "category": "Frameworks & Libraries", "proficiency": "Intermediate"},
            {"name": "PostgreSQL", "category": "Databases", "proficiency": "Intermediate"},
            {"name": "SQLite", "category": "Databases", "proficiency": "Advanced"},
            {"name": "Git & GitHub", "category": "Tools & Platforms", "proficiency": "Advanced"},
            {"name": "Docker", "category": "Tools & Platforms", "proficiency": "Beginner"},
            {"name": "Data Structures & Algorithms", "category": "Core Subjects", "proficiency": "Advanced"},
            {"name": "Communication", "category": "Soft Skills", "proficiency": "Advanced"},
        ],
        "certifications": [
            {
                "title": "Machine Learning Specialization",
                "issuer": "Coursera (Andrew Ng)",
                "date": date(2024, 3, 15),
                "credential_url": "https://coursera.org/verify/example-ml-priya",
            },
            {
                "title": "The Web Developer Bootcamp",
                "issuer": "Udemy",
                "date": date(2023, 8, 20),
                "credential_url": "https://udemy.com/certificate/example-webdev-priya",
            },
        ],
        "projects": [
            {
                "title": "Student Portfolio Management System",
                "tech_stack": "Flask, SQLAlchemy, SQLite, Tailwind CSS, WeasyPrint",
                "description": (
                    "A full-stack web application that lets college students manage their "
                    "academic and professional profiles, generate PDF resumes in two themes, "
                    "and share a public portfolio page."
                ),
                "bullets": [
                    "Designed and implemented 8 profile modules (education, skills, certifications, "
                    "projects, internships, achievements, extracurriculars) with full CRUD operations.",
                    "Built a resume engine that translates DB rows into two PDF-ready themes "
                    "(IT/Industry and College/Campus) using WeasyPrint with a browser-print fallback.",
                    "Integrated Google Gemini free-tier API for AI-assisted bullet point improvement, "
                    "with a daily-limit guard and graceful offline fallback.",
                ],
                "github_link": "https://github.com/priya-sharma-demo/portfolio-system",
                "start_date": date(2024, 8, 1),
                "end_date": date(2025, 4, 30),
                "include_in_resume": True,
            },
            {
                "title": "Crop Disease Detection using CNN",
                "tech_stack": "Python, TensorFlow, Keras, OpenCV, Flask",
                "description": (
                    "A deep-learning web app that identifies crop diseases from leaf images "
                    "with 94% accuracy, helping farmers take timely action."
                ),
                "bullets": [
                    "Trained a MobileNetV2 CNN on the PlantVillage dataset (54,000 images, 38 classes) "
                    "achieving 94.2% validation accuracy.",
                    "Deployed as a RESTful Flask API with an HTML/JS frontend for real-time predictions.",
                    "Optimised inference time to under 200 ms per image through model quantisation.",
                ],
                "github_link": "https://github.com/priya-sharma-demo/crop-disease",
                "start_date": date(2024, 1, 10),
                "end_date": date(2024, 5, 30),
                "include_in_resume": True,
            },
            {
                "title": "Hostel Management System",
                "tech_stack": "Python, Django, MySQL, Bootstrap",
                "description": "A web-based hostel management system for tracking room allocations, fees, and complaints.",
                "bullets": [
                    "Built room allocation module handling 800+ rooms with occupancy tracking and automated email alerts.",
                    "Implemented fee management with payment history and overdue reminders.",
                ],
                "github_link": "https://github.com/priya-sharma-demo/hostel-mgmt",
                "start_date": date(2023, 6, 1),
                "end_date": date(2023, 11, 30),
                "include_in_resume": False,
            },
        ],
        "internships": [
            {
                "company": "Persistent Systems Ltd.",
                "role": "Software Development Intern",
                "start_date": date(2024, 5, 15),
                "end_date": date(2024, 7, 31),
                "description": (
                    "Worked on the internal developer portal team, building REST APIs "
                    "and integrating third-party services."
                ),
                "bullets": [
                    "Developed 12 REST API endpoints in Node.js/Express for the internal developer portal, "
                    "reducing data fetch time by 35%.",
                    "Wrote Pytest unit tests covering 85% of the new endpoints, integrated into the CI/CD pipeline.",
                    "Collaborated in a 6-member agile team, participating in daily stand-ups and sprint reviews.",
                ],
            },
            {
                "company": "Infosys BPM",
                "role": "Machine Learning Intern",
                "start_date": date(2023, 12, 1),
                "end_date": date(2024, 2, 28),
                "description": "Built a document classification pipeline for automated invoice processing.",
                "bullets": [
                    "Built a TF-IDF + SVM document classifier achieving 91% accuracy on 10,000+ labelled invoices.",
                    "Reduced manual document review effort by 60% through automated classification.",
                ],
            },
        ],
        "achievements": [
            {
                "title": "Winner — Smart India Hackathon 2024 (Software Edition)",
                "description": (
                    "Led a 6-member team to first place among 400+ national teams. "
                    "Built an AI-powered agricultural advisory platform in 36 hours."
                ),
                "date": date(2024, 9, 20),
            },
            {
                "title": "AIR 1243 — GATE CS 2025",
                "description": "Scored 68.33 out of 100, securing All India Rank 1243 in Computer Science.",
                "date": date(2025, 3, 12),
            },
            {
                "title": "Best Project Award — PICT Techfest 2024",
                "description": "Received best project in the Web & Cloud category for the Portfolio Management System.",
                "date": date(2024, 2, 18),
            },
        ],
        "extracurriculars": [
            {
                "activity": "PICT Open Source Club",
                "role": "Secretary",
                "description": "Organised 5 workshops on Git, open-source contribution, and Linux for 150+ students.",
            },
            {
                "activity": "National Service Scheme (NSS)",
                "role": "Volunteer",
                "description": "Participated in blood donation drives, tree plantation, and digital literacy camps.",
            },
        ],
    },

    # -----------------------------------------------------------------------
    # Student 2: Arjun Patel — BE Electronics & Telecommunication, Mumbai
    # -----------------------------------------------------------------------
    {
        "name": "Arjun Patel",
        "email": "seed_demo_arjun@example.com",
        "profile": {
            "headline": "Electronics Engineering student | Embedded Systems & IoT Developer",
            "phone": "+91-91234-56789",
            "location": "Mumbai, Maharashtra",
            "linkedin": "https://linkedin.com/in/arjun-patel-demo",
            "github": "https://github.com/arjun-patel-demo",
            "website": "",
            "bio": (
                "Third-year Electronics & Telecommunication Engineering student at VJTI, Mumbai. "
                "I build IoT devices and embedded systems that bridge the physical and digital worlds. "
                "Interested in VLSI design and RTOS-based applications."
            ),
            "summary": (
                "Motivated Electronics Engineering student specialising in embedded systems, IoT, and VLSI. "
                "Proficient in C/C++, Python, and ARM Cortex-M programming. "
                "Hands-on internship experience at a Mumbai-based electronics startup, "
                "designing firmware for BLE-enabled sensor nodes."
            ),
            "is_public": True,
        },
        "education": [
            {
                "level": "B.E. Electronics & Telecommunication",
                "institution": "Veermata Jijabai Technological Institute",
                "board_university": "University of Mumbai",
                "start_year": 2022,
                "end_year": 2026,
                "score": "8.4 CGPA",
            },
            {
                "level": "Class XII (HSC)",
                "institution": "Jai Hind College",
                "board_university": "Maharashtra State Board",
                "start_year": 2020,
                "end_year": 2022,
                "score": "89.6%",
            },
            {
                "level": "Class X (SSC)",
                "institution": "Don Bosco High School",
                "board_university": "Maharashtra State Board",
                "start_year": 2018,
                "end_year": 2020,
                "score": "95.8%",
            },
        ],
        "skills": [
            {"name": "C", "category": "Programming Languages", "proficiency": "Expert"},
            {"name": "C++", "category": "Programming Languages", "proficiency": "Advanced"},
            {"name": "Python", "category": "Programming Languages", "proficiency": "Intermediate"},
            {"name": "FreeRTOS", "category": "Frameworks & Libraries", "proficiency": "Intermediate"},
            {"name": "Arduino IDE", "category": "Tools & Platforms", "proficiency": "Expert"},
            {"name": "KiCad (PCB Design)", "category": "Tools & Platforms", "proficiency": "Intermediate"},
            {"name": "STM32CubeIDE", "category": "Tools & Platforms", "proficiency": "Intermediate"},
            {"name": "Oscilloscope & Logic Analyser", "category": "Tools & Platforms", "proficiency": "Advanced"},
            {"name": "Signals & Systems", "category": "Core Subjects", "proficiency": "Advanced"},
            {"name": "Digital Electronics", "category": "Core Subjects", "proficiency": "Expert"},
        ],
        "certifications": [
            {
                "title": "NPTEL — Embedded Systems Design",
                "issuer": "NPTEL / IIT Kharagpur",
                "date": date(2024, 10, 31),
                "credential_url": "https://nptel.ac.in/verify/example-embed-arjun",
            },
            {
                "title": "AWS IoT Core Essentials",
                "issuer": "Amazon Web Services",
                "date": date(2024, 6, 15),
                "credential_url": "https://aws.amazon.com/verify/example-iot-arjun",
            },
        ],
        "projects": [
            {
                "title": "Smart Home Automation with BLE Mesh",
                "tech_stack": "ESP32, FreeRTOS, BLE Mesh, MQTT, Node-RED",
                "description": (
                    "A home automation system using a BLE mesh network of ESP32 nodes to control "
                    "lights, fans, and security cameras from a mobile app."
                ),
                "bullets": [
                    "Designed a BLE mesh network of 8 ESP32 nodes with FreeRTOS tasks for concurrent "
                    "sensor polling and actuation, achieving <50 ms latency.",
                    "Implemented MQTT over Wi-Fi for cloud connectivity, enabling remote control via "
                    "a Node-RED dashboard.",
                    "Designed the PCB in KiCad with a 3.3 V LDO regulator and USB-C programming port, "
                    "reducing board cost by 40% vs. breakout modules.",
                ],
                "github_link": "https://github.com/arjun-patel-demo/ble-smart-home",
                "start_date": date(2024, 7, 1),
                "end_date": date(2024, 12, 31),
                "include_in_resume": True,
            },
            {
                "title": "Air Quality Monitoring Station",
                "tech_stack": "STM32F4, FreeRTOS, LoRa, Python, Grafana",
                "description": "A low-power outdoor air quality station transmitting PM2.5, CO₂, and temperature data over LoRa to a Grafana dashboard.",
                "bullets": [
                    "Programmed STM32F4 in C using FreeRTOS, achieving 18-month battery life through deep-sleep scheduling.",
                    "Built a LoRa gateway with a Raspberry Pi, forwarding sensor data to InfluxDB visualised in Grafana.",
                ],
                "github_link": "https://github.com/arjun-patel-demo/air-quality-station",
                "start_date": date(2024, 1, 5),
                "end_date": date(2024, 6, 30),
                "include_in_resume": True,
            },
        ],
        "internships": [
            {
                "company": "Embitel Technologies",
                "role": "Embedded Systems Intern",
                "start_date": date(2024, 4, 10),
                "end_date": date(2024, 7, 10),
                "description": (
                    "Developed BLE-based firmware for a wearable health monitor using Nordic nRF52840."
                ),
                "bullets": [
                    "Wrote BLE GATT service firmware in C for the Nordic nRF52840 SoC, implementing "
                    "Heart Rate and Battery Service profiles as per Bluetooth SIG specifications.",
                    "Reduced average current consumption from 12 mA to 4.2 mA through optimised "
                    "advertising intervals and connection parameter tuning.",
                    "Documented firmware APIs and contributed 3 bug fixes to the internal HAL library.",
                ],
            },
        ],
        "achievements": [
            {
                "title": "1st Place — ISTE VJTI TechFest Hardware Hackathon 2024",
                "description": "Won first prize for the BLE Smart Home project, selected from 80 teams across Mumbai.",
                "date": date(2024, 9, 5),
            },
            {
                "title": "NPTEL Elite Certificate — Embedded Systems (Score: 88/100)",
                "description": "Secured 88% in the NPTEL Embedded Systems Design course, earning the Elite certificate.",
                "date": date(2024, 10, 31),
            },
        ],
        "extracurriculars": [
            {
                "activity": "VJTI Robotics Club",
                "role": "Hardware Lead",
                "description": "Led the hardware sub-team for the autonomous line-following robot, winning inter-college competitions.",
            },
            {
                "activity": "IEEE VJTI Student Branch",
                "role": "Member",
                "description": "Attended workshops on VLSI, IoT, and participated in the IEEE Xtreme programming contest.",
            },
        ],
    },
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_json_bullets(bullet_list):
    return json.dumps(bullet_list)


def _seed_student(student_data):
    """Create or recreate one demo student. Returns the created User object."""
    email = student_data["email"]

    # Delete existing demo account with this email (reset, not skip).
    existing = User.query.filter_by(email=email).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        print(f"  [reset] Deleted existing demo user: {email}")

    # Create user.
    user = User(name=student_data["name"], email=email)
    user.set_password(DEMO_PASSWORD)
    db.session.add(user)
    db.session.flush()  # get user.id before adding children

    # Profile
    p = student_data["profile"]
    profile = Profile(
        user_id=user.id,
        public_slug=generate_unique_slug(student_data["name"]),
        headline=p.get("headline"),
        phone=p.get("phone"),
        location=p.get("location"),
        linkedin=p.get("linkedin") or None,
        github=p.get("github") or None,
        website=p.get("website") or None,
        bio=p.get("bio"),
        summary=p.get("summary"),
        is_public=p.get("is_public", False),
    )
    db.session.add(profile)

    # Education
    for e in student_data.get("education", []):
        db.session.add(Education(user_id=user.id, **e))

    # Skills
    for s in student_data.get("skills", []):
        db.session.add(Skill(user_id=user.id, **s))

    # Certifications
    for c in student_data.get("certifications", []):
        db.session.add(Certification(user_id=user.id, **c))

    # Projects (bullets stored as JSON; pop bullets key since model uses set_bullets)
    for proj in student_data.get("projects", []):
        proj_data = {k: v for k, v in proj.items() if k != "bullets"}
        project = Project(user_id=user.id, **proj_data)
        project.set_bullets(proj.get("bullets", []))
        db.session.add(project)

    # Internships
    for intern in student_data.get("internships", []):
        intern_data = {k: v for k, v in intern.items() if k != "bullets"}
        internship = Internship(user_id=user.id, **intern_data)
        internship.set_bullets(intern.get("bullets", []))
        db.session.add(internship)

    # Achievements
    for a in student_data.get("achievements", []):
        db.session.add(Achievement(user_id=user.id, **a))

    # Extracurriculars
    for x in student_data.get("extracurriculars", []):
        db.session.add(Extracurricular(user_id=user.id, **x))

    db.session.commit()
    return user, profile


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    app = create_app()
    with app.app_context():
        print("\n=== Student Portfolio — Demo Seed Script ===\n")

        # Safety: list all demo emails we will touch.
        all_demo_emails = [s["email"] for s in STUDENTS]
        print(f"Demo accounts managed by this script: {all_demo_emails}")
        print("(Only these accounts are deleted/recreated. Real users are untouched.)\n")

        created = []
        for student_data in STUDENTS:
            print(f"Seeding: {student_data['name']} ({student_data['email']})...")
            user, profile = _seed_student(student_data)
            portfolio_url = f"http://localhost:5000/portfolio/{profile.public_slug}"
            created.append({
                "name": user.name,
                "email": user.email,
                "portfolio_url": portfolio_url,
            })
            print(f"  ✓ Created with slug: {profile.public_slug}")

        print("\n" + "=" * 60)
        print("DEMO LOGIN CREDENTIALS")
        print("=" * 60)
        print(f"Password (all accounts) : {DEMO_PASSWORD}")
        print()
        for info in created:
            print(f"  Name     : {info['name']}")
            print(f"  Email    : {info['email']}")
            print(f"  Portfolio: {info['portfolio_url']}")
            print()
        print("=" * 60)
        print("Run `python run.py` and open http://localhost:5000 to log in.\n")


if __name__ == "__main__":
    main()
