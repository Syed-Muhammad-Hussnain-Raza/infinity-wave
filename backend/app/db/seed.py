"""Database seeding script for NovaWorks AI Project Manager.
Seeds the 10 demo accounts required for hackathon judging.
Re-running this script will NOT duplicate users.
"""
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.db.database import SessionLocal, init_db
from app.db.models import User, UserRole
from app.core.security import hash_password

DEMO_USERS: List[Dict[str, Any]] = [
    {
        "role": UserRole.ADMIN,
        "name": "Admin",
        "email": "admin@novaworks.example",
        "password": "Demo123!",
        "specialization": "System Administrator",
        "skills": "Administration, Governance, Management",
    },
    {
        "role": UserRole.MANAGER,
        "name": "Ayesha Khan",
        "email": "ayesha@novaworks.example",
        "password": "Demo123!",
        "specialization": "E-Commerce & Mobile Delivery PM",
        "skills": "Project Management, Agile, Client Relations",
    },
    {
        "role": UserRole.MANAGER,
        "name": "Bilal Ahmed",
        "email": "bilal@novaworks.example",
        "password": "Demo123!",
        "specialization": "Fintech & Core Banking PM",
        "skills": "Scrum, Stakeholder Management, Financial Tech",
    },
    {
        "role": UserRole.MANAGER,
        "name": "Hina Malik",
        "email": "hina@novaworks.example",
        "password": "Demo123!",
        "specialization": "Healthcare & Analytics PM",
        "skills": "Product Roadmap, Analytics, Team Leadership",
    },
    {
        "role": UserRole.AGENT,
        "name": "Ali Raza",
        "email": "ali@novaworks.example",
        "password": "Demo123!",
        "specialization": "Backend Engineering",
        "skills": "Python, FastAPI, PostgreSQL, Redis",
    },
    {
        "role": UserRole.AGENT,
        "name": "Hamza Shah",
        "email": "hamza@novaworks.example",
        "password": "Demo123!",
        "specialization": "Full Stack & API Engineering",
        "skills": "FastAPI, React, API Architecture, TypeScript",
    },
    {
        "role": UserRole.AGENT,
        "name": "Sara Noor",
        "email": "sara@novaworks.example",
        "password": "Demo123!",
        "specialization": "Frontend Engineering",
        "skills": "React, TailwindCSS, State Management, UI/UX",
    },
    {
        "role": UserRole.AGENT,
        "name": "Usman Tariq",
        "email": "usman@novaworks.example",
        "password": "Demo123!",
        "specialization": "DevOps & Cloud Architecture",
        "skills": "Docker, Kubernetes, AWS, CI/CD, Terraform",
    },
    {
        "role": UserRole.AGENT,
        "name": "Zain Abbas",
        "email": "zain@novaworks.example",
        "password": "Demo123!",
        "specialization": "QA & Test Automation",
        "skills": "PyTest, Playwright, API Testing, Performance Testing",
    },
    {
        "role": UserRole.AGENT,
        "name": "Maryam Asif",
        "email": "maryam@novaworks.example",
        "password": "Demo123!",
        "specialization": "UI/UX Design & Frontend",
        "skills": "Figma, React, Design Systems, Accessibility",
    },
]


def seed_users(db: Session) -> int:
    """Seed the 10 demo users if they don't already exist."""
    created_count = 0
    for user_data in DEMO_USERS:
        existing = db.query(User).filter(User.email == user_data["email"]).first()
        if not existing:
            new_user = User(
                name=user_data["name"],
                email=user_data["email"],
                password_hash=hash_password(user_data["password"]),
                role=user_data["role"],
                specialization=user_data["specialization"],
                skills=user_data["skills"],
            )
            db.add(new_user)
            created_count += 1
    db.commit()
    return created_count


def run_seed() -> None:
    """Entrypoint to initialize tables and seed users."""
    print("Initializing database tables...")
    init_db()
    db = SessionLocal()
    try:
        created = seed_users(db)
        print(f"Seeding completed. Created {created} new demo user(s).")
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
