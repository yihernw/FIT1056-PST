# main.py - Simple text menu (View)
from app.schedule import ScheduleManager

def show_daily_roster(manager):
    #prompt user for day and display lessons for that day
    day = input("Enter day (e.g., Monday): ").strip()
    lessons = manager.get_lessons_by_day(day)
    print(f"\n--- Daily Roster for {day} ---")
    if len(lessons) == 0:
        print("No lessons scheduled.")
        return
    #print header
    print(f"{'Time':<8} {'Room':<8} {'Course':<28} {'Teacher'}")
    print("-" * 70)
    #print each lesson details
    for row in lessons:
        print(f"{row['start_time']:<8} {row['room']:<8} {row['course_name']:<28} {row['teacher_name']}")

def do_check_in(manager):
    #prompt user for student ID and course ID then check in the student
    try:
        student_id = int(input("Student ID: "))
        course_id = int(input("Course ID: "))
    except ValueError:
        print("Please enter numbers.")
        return
    manager.check_in(student_id, course_id)

def do_switch_course(manager):
    #prompt user for student ID, from course ID and to course ID then switch the student
    try:
        student_id = int(input("Student ID: "))
        from_course_id = int(input("From course ID: "))
        to_course_id = int(input("To course ID: "))
    except ValueError:
        print("Please enter numbers.")
        return
    manager.switch_student_course(student_id, from_course_id, to_course_id)

def main():
    # Initialize the ScheduleManager
    manager = ScheduleManager()

    while True:
        #display menu
        print("\n===== MSMS v3 Menu =====")
        print("1) Show daily roster")
        print("2) Check-in a student")
        print("3) Switch a student between courses")
        print("q) Quit")
        choice = input("Choose: ").strip().lower()

        #handle user choice
        if choice == "1":
            show_daily_roster(manager)
        elif choice == "2":
            do_check_in(manager)
        elif choice == "3":
            do_switch_course(manager)
        elif choice == "q":
            print("Goodbye.")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()