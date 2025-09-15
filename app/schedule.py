import json
import datetime
from app.student import StudentUser
from app.teacher import TeacherUser, Course

class ScheduleManager:
    #class loads data, saves data, and provides main actions for the app.
    def __init__(self, data_path="data/msms.json"):
        self.data_path = data_path
        self.students = []
        self.teachers = []
        self.courses = []
        self.attendance_log = []  #list of dicts: {"student_id":..., "course_id":..., "timestamp":...}
        self._load_data()

    def _load_data(self):
        #load everything from JSON into Python objects.
        try:
            with open(self.data_path, "r") as f:
                data = json.load(f)
        #if file not found, start with empty data
        except FileNotFoundError:
            print("Data file not found. Starting empty.")
            data = {}

        #students
        self.students = []
        for s in data.get("students", []):
            stu = StudentUser(s["id"], s["name"])
            stu.enrolled_course_ids = s.get("enrolled_course_ids", [])
            self.students.append(stu)

        #teachers
        self.teachers = []
        for t in data.get("teachers", []):
            teacher = TeacherUser(t["id"], t["name"], t.get("speciality", ""))
            self.teachers.append(teacher)

        #courses
        self.courses = []
        for c in data.get("courses", []):
            course = Course(c["id"], c["name"], c["instrument"], c["teacher_id"])
            course.enrolled_student_ids = c.get("enrolled_student_ids", [])
            course.lessons = c.get("lessons", [])
            self.courses.append(course)

        #attendance
        self.attendance_log = data.get("attendance", [])

    def _save_data(self):
        #turn objects back into dictionaries and save to JSON.
        students_out = []
        for s in self.students:
            students_out.append({
                "id": s.id,
                "name": s.name,
                "enrolled_course_ids": s.enrolled_course_ids
            })

        teachers_out = []
        for t in self.teachers:
            teachers_out.append({
                "id": t.id,
                "name": t.name,
                "speciality": t.speciality
            })

        courses_out = []
        for c in self.courses:
            courses_out.append({
                "id": c.id,
                "name": c.name,
                "instrument": c.instrument,
                "teacher_id": c.teacher_id,
                "enrolled_student_ids": c.enrolled_student_ids,
                "lessons": c.lessons
            })

        data_to_save = {
            "students": students_out,
            "teachers": teachers_out,
            "courses": courses_out,
            "attendance": self.attendance_log
        }

        with open(self.data_path, "w") as f:
            json.dump(data_to_save, f, indent=4)

    #simple find helpers
    def find_student_by_id(self, student_id):
        for s in self.students:
            if s.id == student_id:
                return s
        return None

    def find_course_by_id(self, course_id):
        for c in self.courses:
            if c.id == course_id:
                return c
        return None

    def find_teacher_by_id(self, teacher_id):
        for t in self.teachers:
            if t.id == teacher_id:
                return t
        return None

    #core actions
    def check_in(self, student_id, course_id):
        student = self.find_student_by_id(student_id)
        course = self.find_course_by_id(course_id)

        if student is None or course is None:
            print("Error: Invalid student or course ID.")
            return False

        if student_id not in course.enrolled_student_ids:
            print("Error: Student is not enrolled in this course.")
            return False

        timestamp = datetime.datetime.now().isoformat()
        record = {"student_id": student_id, "course_id": course_id, "timestamp": timestamp}
        self.attendance_log.append(record)
        self._save_data()
        print(f"Checked in: {student.name} -> {course.name}")
        return True

    def get_lessons_by_day(self, day):
        #return basic info for printing the roster.
        result = []
        for c in self.courses:
            teacher = self.find_teacher_by_id(c.teacher_id)
            teacher_name = teacher.name if teacher else "Unknown"
            for lesson in c.lessons:
                if lesson.get("day", "").lower() == day.lower():
                    result.append({
                        "course_name": c.name,
                        "teacher_name": teacher_name,
                        "start_time": lesson.get("start_time", ""),
                        "room": lesson.get("room", "")
                    })
        #sort by time so the list looks neat.
        result.sort(key=lambda x: x["start_time"])
        return result

    def switch_student_course(self, student_id, from_course_id, to_course_id):
        student = self.find_student_by_id(student_id)
        from_course = self.find_course_by_id(from_course_id)
        to_course = self.find_course_by_id(to_course_id)

        if student is None or from_course is None or to_course is None:
            print("Error: Invalid IDs.")
            return False

        if student_id not in from_course.enrolled_student_ids:
            print("Error: Student not in the 'from' course.")
            return False

        #remove from old course
        from_course.enrolled_student_ids.remove(student_id)
        # Add to new course (avoid duplicates)
        if student_id not in to_course.enrolled_student_ids:
            to_course.enrolled_student_ids.append(student_id)

        #update student's list
        if from_course_id in student.enrolled_course_ids:
            student.enrolled_course_ids.remove(from_course_id)
        if to_course_id not in student.enrolled_course_ids:
            student.enrolled_course_ids.append(to_course_id)

        self._save_data()
        print(f"Switched: {student.name} from {from_course.name} to {to_course.name}")
        return True