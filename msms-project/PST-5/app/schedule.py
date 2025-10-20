import json
import logging
import datetime
import csv
import os

from app.student import StudentUser
from app.teacher import TeacherUser, Course

class ScheduleManager:
    """The main controller for all business logic and data handling."""

    def __init__(self, data_path="data/msms.json"):
        self.data_path = data_path
        self.students = []
        self.teachers = []
        self.courses = []
        self.attendance_log = []
        self.finance_log = []
        self.next_lesson_id = 1
        # ensure data directory exists (when saving later)
        self._load_data()

    def _load_data(self):
        """Loads data from the JSON file and populates the object lists."""
        if not os.path.exists(self.data_path):
            # No data file - start empty
            return

        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"Failed to read data file {self.data_path}: {e}")
            return

        # Load students
        self.students = []
        for s in data.get('students', []):
            su = StudentUser(s.get('id'), s.get('name'))
            # keep enrolled_course_ids if present
            su.enrolled_course_ids = s.get('enrolled_course_ids', [])
            self.students.append(su)

        # Load teachers
        self.teachers = []
        for t in data.get('teachers', []):
            tu = TeacherUser(t.get('id'), t.get('name'), t.get('speciality'))
            self.teachers.append(tu)

        # Load courses
        self.courses = []
        for c in data.get('courses', []):
            co = Course(c.get('id'), c.get('name'), c.get('instrument'), c.get('teacher_id'))
            co.enrolled_student_ids = c.get('enrolled_student_ids', [])
            co.lessons = c.get('lessons', [])
            self.courses.append(co)

        # Attendance & Finance
        self.attendance_log = data.get('attendance', [])
        self.finance_log = data.get('finance', [])

        # compute next_lesson_id
        max_lid = 0
        for course in self.courses:
            for l in getattr(course, 'lessons', []):
                lid = l.get('lesson_id', 0)
                if isinstance(lid, int) and lid > max_lid:
                    max_lid = lid
        self.next_lesson_id = max_lid + 1

    def _save_data(self):
        """Converts object lists back to dictionaries and saves to JSON."""
        # Ensure directory exists
        dirpath = os.path.dirname(self.data_path)
        if dirpath and not os.path.exists(dirpath):
            os.makedirs(dirpath)

        data_to_save = {
            "students": [
                {
                    "id": s.id,
                    "name": s.name,
                    "enrolled_course_ids": getattr(s, "enrolled_course_ids", [])
                } for s in self.students
            ],
            "teachers": [
                {
                    "id": t.id,
                    "name": t.name,
                    "speciality": getattr(t, "speciality", None)
                } for t in self.teachers
            ],
            "courses": [
                {
                    "id": c.id,
                    "name": c.name,
                    "instrument": c.instrument,
                    "teacher_id": c.teacher_id,
                    "enrolled_student_ids": getattr(c, "enrolled_student_ids", []),
                    "lessons": getattr(c, "lessons", [])
                } for c in self.courses
            ],
            "attendance": self.attendance_log,
            "finance": self.finance_log
        }

        try:
            with open(self.data_path, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Failed to save data to {self.data_path}: {e}")

    # --- Minimal business methods used by tests / GUI ---

    def create_course(self, name, instrument, teacher_id):
        """Create a new course and persist it."""
        new_id = 1
        if self.courses:
            try:
                new_id = max(c.id for c in self.courses if isinstance(c.id, int)) + 1
            except Exception:
                new_id = len(self.courses) + 1
        course = Course(new_id, name, instrument, teacher_id)
        # initialize lists
        course.enrolled_student_ids = []
        course.lessons = []
        self.courses.append(course)
        self._save_data()
        logging.info(f"Created course '{name}' (id={new_id}) by teacher {teacher_id}.")
        return course

    def record_payment(self, student_id, amount, method):
        """Adds a payment record to the finance log."""
        # Accept numeric amounts; normalize to float
        try:
            amt = float(amount)
        except Exception:
            raise ValueError("Invalid amount")

        payment_record = {
            "student_id": student_id,
            "amount": amt,
            "method": method,
            "timestamp": datetime.datetime.now().isoformat()
        }
        self.finance_log.append(payment_record)
        self._save_data()
        logging.info(f"Payment of {amt} recorded for student ID {student_id}.")
        return payment_record

    def get_payment_history(self, student_id):
        """Returns a list of all payments for a given student."""
        return [p for p in self.finance_log if p.get('student_id') == student_id]

    def export_report(self, kind, out_path):
        """Exports a log to a CSV file. kind: 'finance' or 'attendance'."""
        if kind == "finance":
            data_to_export = self.finance_log
            headers = ["student_id", "amount", "method", "timestamp"]
        elif kind == "attendance":
            data_to_export = self.attendance_log
            headers = ["student_id", "course_id", "timestamp"]
        else:
            logging.error(f"Unknown report kind: {kind}")
            return False

        # Ensure output directory exists
        out_dir = os.path.dirname(out_path)
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir)

        try:
            with open(out_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                for row in data_to_export:
                    # write only keys from headers; missing keys -> empty
                    writer.writerow({h: row.get(h, "") for h in headers})
            logging.info(f"Exported {kind} report to {out_path}")
            return True
        except Exception as e:
            logging.error(f"Failed to export report to {out_path}: {e}")
            return False

    def cancel_lesson(self, lesson_id, reason):
        """Cancel a lesson by id. Returns True if found+removed, False otherwise."""
        removed = False
        for course in self.courses:
            new_lessons = []
            for l in getattr(course, "lessons", []):
                if l.get('lesson_id') == lesson_id:
                    removed = True
                    # skip adding -> effectively removed
                else:
                    new_lessons.append(l)
            course.lessons = new_lessons
        if removed:
            self._save_data()
            logging.warning(f"Lesson ID {lesson_id} was cancelled. Reason: {reason}")
        return removed