import json
from datetime import datetime
from app.student import StudentUser
from app.teacher import TeacherUser, Course

class ScheduleManager:
    """The main controller for all business logic and data handling."""
    def __init__(self, data_path="data/msms.json"):
        self.data_path = data_path
        self.students = []
        self.teachers = []
        self.courses = []
        self.attendance = []
        self.next_student_id = 100
        self.next_lesson_id = 1
        self._load_data()

    def _load_data(self):
        """Loads data from the JSON file and populates the object lists."""
        try:
            with open(self.data_path, 'r') as f:
                data = json.load(f)
                # The logic here remains the same, but the source of the Course class has changed.
                # TODO: For each dictionary in data['students'], create a StudentUser object and append to self.students.
                for student_data in data.get('students', []):
                    student = StudentUser(student_data['id'], student_data['name'])
                    student.enrolled_course_ids = student_data.get('enrolled_course_ids', [])
                    self.students.append(student)
                    if student_data['id'] >= self.next_student_id:
                        self.next_student_id = student_data['id'] + 1
                
                # TODO: Do the same for teachers (creating TeacherUser objects).
                for teacher_data in data.get('teachers', []):
                    teacher = TeacherUser(
                        teacher_data['id'], 
                        teacher_data['name'], 
                        teacher_data['speciality']
                    )
                    self.teachers.append(teacher)
                
                # TODO: Do the same for courses (creating Course objects).
                for course_data in data.get('courses', []):
                    course = Course(
                        course_data['id'],
                        course_data['name'],
                        course_data['instrument'],
                        course_data['teacher_id']
                    )
                    course.enrolled_student_ids = course_data.get('enrolled_student_ids', [])
                    course.lessons = course_data.get('lessons', [])
                    self.courses.append(course)
                
                # Load attendance records
                self.attendance = data.get('attendance', [])
                
        except FileNotFoundError:
            print("Data file not found. Starting with a clean state.")
        except json.JSONDecodeError:
            print("Error decoding JSON data. Starting with a clean state.")
    
    def _save_data(self):
        """Converts object lists back to dictionaries and saves to JSON."""
        # The logic here remains the same.
        # TODO: Create a 'data_to_save' dictionary.
        data_to_save = {
            'students': [],
            'teachers': [],
            'courses': [],
            'attendance': self.attendance
        }
        
        # Convert self.students, self.teachers, and self.courses into lists of dictionaries.
        for student in self.students:
            data_to_save['students'].append({
                'id': student.id,
                'name': student.name,
                'enrolled_course_ids': student.enrolled_course_ids
            })
        
        for teacher in self.teachers:
            data_to_save['teachers'].append({
                'id': teacher.id,
                'name': teacher.name,
                'speciality': teacher.speciality
            })
        
        for course in self.courses:
            data_to_save['courses'].append({
                'id': course.id,
                'name': course.name,
                'instrument': course.instrument,
                'teacher_id': course.teacher_id,
                'enrolled_student_ids': course.enrolled_student_ids,
                'lessons': course.lessons
            })
        
        # Write the result to the JSON file.
        try:
            with open(self.data_path, 'w') as f:
                json.dump(data_to_save, f, indent=4)
        except Exception as e:
            print(f"Error saving data: {e}")

    def register_new_student(self, name, instrument):
        """Registers a new student and enrolls them in an available course for their instrument."""
        try:
            # Find an available course for the instrument
            available_course = None
            for course in self.courses:
                if course.instrument.lower() == instrument.lower():
                    available_course = course
                    break
            
            if not available_course:
                print(f"No available course found for instrument: {instrument}")
                return None
            
            # Create new student
            new_student = StudentUser(self.next_student_id, name)
            self.next_student_id += 1
            
            # Enroll student in the course
            new_student.enrolled_course_ids.append(available_course.id)
            available_course.enrolled_student_ids.append(new_student.id)
            
            # Add to students list and save
            self.students.append(new_student)
            self._save_data()
            
            print(f"Successfully registered {name} for {instrument}")
            return new_student
            
        except Exception as e:
            print(f"Error registering student: {e}")
            return None

    def check_in(self, student_id, course_id):
        """Checks in a student for a course they're enrolled in."""
        try:
            # Verify student exists and is enrolled in the course
            student = next((s for s in self.students if s.id == student_id), None)
            if not student:
                print(f"Student with ID {student_id} not found")
                return False
            
            if course_id not in student.enrolled_course_ids:
                print(f"Student {student.name} is not enrolled in course {course_id}")
                return False
            
            # Record attendance
            attendance_record = {
                'student_id': student_id,
                'course_id': course_id,
                'timestamp': datetime.now().isoformat()
            }
            self.attendance.append(attendance_record)
            
            # Save data
            self._save_data()
            
            print(f"Successfully checked in {student.name}")
            return True
            
        except Exception as e:
            print(f"Error during check-in: {e}")
            return False

    def get_courses_by_day(self, day):
        """Returns courses that have lessons on the specified day."""
        day_courses = []
        for course in self.courses:
            for lesson in course.lessons:
                if lesson.get('day', '').lower() == day.lower():
                    day_courses.append(course)
                    break
        return day_courses