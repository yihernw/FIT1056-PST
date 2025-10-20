# Music School Management System (MSMS) - PST5

## Overview
This project represents the development of the Music School Management System (MSMS) across five PST stages, culminating in PST5 where quality, finance, and automated testing were added. The system uses Object-Oriented Programming and a Streamlit GUI to manage students, teachers, courses, attendance, finance, and administrative utilities.

## Features
- Allows for the enrollment of new students and registration in courses based on their instrument preference
- Enables tracking of teachers and their specialities
- Enables the creation of courses, including lesson scheduling and student enrollment
- Provides a means for checking in students, ensuring they are enrolled in the relevant courses
- Allows users to view the daily schedule of courses and lessons
- Finance features: record payments, view payment history, and export finance reports (CSV)
- Allows for logging and timestamped backups of the JSON data file
- Uses JSON for data storage, ensuring information is retained between sessions
- Automated test suite (pytest) covering core business logic

## How to Run
- Ensure you have Python 3.9+, Streamlit, and Pytest installed.
- Navigate to the project directory
- Enter streamlit run main.py in the terminal
- Follow the on-screen menu instructions

## Running Tests
From the project root (PowerShell):
```
pip install pytest
pytest -q
```

## Design Choices
- Implemented Object-Oriented Programming architecture for better scalability
- Used Model-View-Controller (MVC) pattern for separation of concerns
- JSON format chosen for data persistence for simplicity and readability
- Added input validation for all operations
- The GUI provides immediate feedback for user actions, improving user experience
- Tests: `pytest` is used for fast, maintainable unit tests following Arrange–Act–Assert

## Future Improvements
- Stronger validation: disallow recording payments for unknown student IDs (or auto-create placeholders) — current system records payments even if the student object isn't present
- Role-based authentication and authorization for admin vs. teacher vs. student

## GitHub Link
- https://github.com/yihernw/FIT1056-PST
