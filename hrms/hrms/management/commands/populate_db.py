# hrms/management/commands/populate_db.py

import time
from django.core.management.base import BaseCommand
from portal.models import Department, Position # Make sure to import your models from the correct app

# --- Data to be Inserted ---

DEPARTMENTS = [
    "Software Development",
    "Quality Assurance & Testing",
    "IT Operations & Infrastructure",
    "Project Management Office (PMO)",
    "Business Analysis & Consulting",
    "User Experience (UX) & UI Design",
    "Sales & Business Development",
    "Marketing",
    "Client Services & Account Management",
    "Human Resources",
    "Finance & Accounting",
    "Administration & Operations",
]

POSITIONS = [
    "Associate Software Engineer",
    "Software Engineer",
    "Senior Software Engineer",
    "Technical Lead",
    "Solutions Architect",
    "QA Tester",
    "QA Automation Engineer",
    "Test Lead",
    "IT Support Specialist",
    "System Administrator",
    "Network Administrator",
    "Database Administrator (DBA)",
    "Cloud Engineer",
    "DevOps Engineer",
    "Project Coordinator",
    "Project Manager",
    "Program Manager",
    "Business Analyst",
    "IT Consultant",
    "UI/UX Designer",
    "Sales Development Representative (SDR)",
    "Account Executive",
    "Marketing Coordinator",
    "Account Manager",
    "HR Generalist",
    "Talent Acquisition Specialist",
    "Financial Analyst",
    "Office Manager",
]


class Command(BaseCommand):
    help = 'Populates the database with initial departments and positions'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting database population...'))

        # --- Populate Departments ---
        for dept_name in DEPARTMENTS:
            department, created = Department.objects.get_or_create(name=dept_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Successfully created Department: {department.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Department "{department.name}" already exists.'))

        # --- Populate Positions ---
        for pos_title in POSITIONS:
            position, created = Position.objects.get_or_create(title=pos_title)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Successfully created Position: {position.title}'))
            else:
                self.stdout.write(self.style.WARNING(f'Position "{position.title}" already exists.'))
        
        self.stdout.write(self.style.SUCCESS('Database population complete! ✅'))