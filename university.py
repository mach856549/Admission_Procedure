global departments, dict_department_applicants, placed_students, test_score_column, original_scores, full_applicant_list
departments = sorted(["Biotech", "Chemistry", "Engineering", "Mathematics", "Physics"])
# Test Scores from original input "applicant.txt"
original_scores = {"Physics": 2, "Chemistry": 3, "Mathematics": 4, "ComputerScience": 5, "Special": 6}
# Acceptance scores column references from new processed input "applicant_assessment.txt"
test_score_column = {"Biotech": 2, "Chemistry": 3, "Engineering": 4, "Mathematics": 5, "Physics": 6}
placed_students = 0
dict_department_applicants = {}
full_applicant_list = []

def create_list_from_file():
    """Return the list of candidates from a file. No Sorting at this stage
    """
    global full_applicant_list
    with open("applicants_assessment.txt", "r") as applicant_file:
        for line in applicant_file.readlines():
            full_applicant_list.append(line.split())


def add_consolidated_scores(list_):
    """Calculate and add the consolidated scores to each students information.

    Physics requires: (Maths + Physics) / 2 --> New Column = 9
    Engineering requires: (Computer science + Maths) / 2 --> New Column = 10
    Biotech requires: (Chemistry + Physics) / 2 --> New Column = 11

    These additional scores are calculated and added to the student information.
    """
    # These scores could have been calculated at time of filter but it is easier to include them as part of
    # the student list at this stage since all filtering is done within students_to_consider() and based on
    # test_score_column dictionary

    for student in list_:
        phys = calc_average(student, "Physics", "Mathematics")
        eng = calc_average(student, "ComputerScience", "Mathematics")
        bio = calc_average(student, "Physics", "Chemistry")
        student.extend([phys, eng, bio])
    return list_


def process_input():
    """Create new input file replacing original exam scores with assessment scores.

    Output Format for "applicant_assessment.txt"
    ------------------THESE CONTAIN THE SCORES USED FOR ACCEPTANCE (i.e. MAX SPECIAL EXAM or RELEVANT AVERAGE)-------
    <first_name> <last_name> <Biotech> <Chemistry> <Engineering> <Mathematics> <Physics> <Choice1> <Choice2> <Choice3>
    Biotech requires: MAX: (Chemistry + Physics) / 2 OR Special Exam
    Chemistry requires: MAX Chemistry OR Special Exam
    Engineering requires: MAX: (Computer science + Maths) / 2 OR Special Exam
    Mathematics requires: MAX: Maths OR Special Exam
    Physics requires: MAX: (Maths + Physics) / 2 OR Special Exam

    These acceptance scores are calculated and a new file "applicant_assessment.txt" create.
    """
    with open("applicants.txt", "r") as applicant_file, open("applicants_assessment.txt", "wt") as out_f:
        for line in applicant_file.readlines():
            student_orig = line.split()
            first_name = student_orig[0]
            last_name = student_orig[1]
            special_exam = float(student_orig[6])
            choice1 = student_orig[7]
            choice2 = student_orig[8]
            choice3 = student_orig[9]
            bio = round(max(calc_average(student_orig, "Physics", "Chemistry"), special_exam), 1)
            chem = round(max(float(student_orig[original_scores.get("Chemistry")]), special_exam), 1)
            eng = round(max(calc_average(student_orig, "ComputerScience", "Mathematics"), special_exam), 1)
            maths = round(max(float(student_orig[original_scores.get("Mathematics")]), special_exam), 1)
            phys = round(max(calc_average(student_orig, "Physics", "Mathematics"), special_exam), 1)
            out_f.write(f"{first_name} {last_name} {bio} {chem} {eng} {maths} {phys} {choice1} {choice2} {choice3}\n")


def calc_average(list_, sub1, sub2):
    """Return the average of two test scores as float.

    list_ = individual student list
    sub1 = subject name from list original_scores
    sub2 = subject name from list original_scores
    """
    return round((float(list_[original_scores.get(sub1)]) + float(list_[original_scores.get(sub2)])) / 2, 1)


def assign_students_to_department():
    """Create a dictionary of lists with key as defined in departments variable.

    'departments' variable - Defines all of the possible primary departments
    'max_students' - User Input to define the maximum students permitted in each department
    Create a dictionary of format {department: [sorted list of students accepted into this department]}
    """
    global departments, dict_department_applicants, placed_students, test_score_column
    max_students = int(input("Enter maximum number of students in a department"))
    # Create the department list dictionary and fill with successful students who made primary choice.
    for dep in departments:
        applicant_list = students_to_consider(full_applicant_list, dep, 1)
        if len(applicant_list) > max_students:
            applicant_list = applicant_list[:max_students]
        dict_department_applicants[dep] = applicant_list
    find_unplaced_students()
    for dep_list in dict_department_applicants.values():
        placed_students += len(dep_list)
    if len(unassigned_students) > 0:
        for i in range(2, 4):  # 2 for 2nd choice, 3 for 3rd choice.
            # Check for unfilled space in each department and then populate it
            for dep_item in dict_department_applicants.items():
                if len(dep_item[1]) < max_students:
                    number_to_admit = max_students - len(dep_item[1])
                    extra_students = students_to_consider(unassigned_students, dep_item[0], i)
                    if number_to_admit <= len(extra_students):
                        extra_students = extra_students[:number_to_admit]
                    dep_item[1].extend(extra_students)
                    for student in extra_students:
                        unassigned_students.remove(student)
                    dep_item[1].sort(key=lambda x: (-float(x[test_score_column.get(dep_item[0])]), x[0] + x[1]))


def students_to_consider(list_, subject, num):
    """Return a filtered list of unassigned students sorted based on correct score.

    Take list, subject and choice (1, 2 or 3) corresponding to 1st, 2nd or 3rd choice.
    Return a filtered list containing only students who;
     - have not been allocated yet
     - chose the subject as their 1st, 2nd or 3rd choice
     - sorted by relevant score
    """
    local_list = [student for student in list_ if student[6 + num] == subject]
    local_list.sort(key=lambda x: (-float(x[test_score_column[subject]]), x[0] + x[1]))
    return local_list


def is_student_placed(student):
    """Return True if student has been assigned a place otherwise False"""
    for dep_list in dict_department_applicants.values():
        if student in dep_list:
            return True
    return False


def find_unplaced_students():
    """Create a new list of students without places.

    When this code is called it will create a new list "unassigned_students" who do not currently have a place
    """
    global unassigned_students
    unassigned_students = [student for student in full_applicant_list if not is_student_placed(student)]


def application_summary():
    """Print the output of the final data"""
    for dep_list in dict_department_applicants.items():
        print(dep_list[0])
        for student in dep_list[1]:
            print(f"{student[0]} {student[1]} {student[test_score_column[dep_list[0]]]}")
        print()
    print("Unassigned Students")
    for student in unassigned_students:
        print(student)
    print()
    print("Application Summary")
    print(f"Total Applied: {len(full_applicant_list)}, Total Accepted: {placed_students}, "
          f"Total Rejected: {len(unassigned_students)}")


def write_output_to_file():
    for dep_list in dict_department_applicants.items():
        with open(dep_list[0] + ".txt", "wt") as applicant_output:
            for student in dep_list[1]:
                applicant_output.write(f"{student[0]} {student[1]} {student[test_score_column[dep_list[0]]]}\n")


def main():
    """This is the main function which calls all other sub-functions as required."""
    process_input()
    create_list_from_file()
    assign_students_to_department()
    write_output_to_file()

main()

