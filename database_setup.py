import random

import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="geneticDatabase",
    database="mockcollegedata"
)

mycursor = mydb.cursor()

# Clear
mycursor.execute("DROP TABLE IF EXISTS lecture_lecturers")
mycursor.execute("DROP TABLE IF EXISTS enrollments")
mycursor.execute("DROP TABLE IF EXISTS lectures")
mycursor.execute("DROP TABLE IF EXISTS lecturers")
mycursor.execute("DROP TABLE IF EXISTS students")
mycursor.execute("DROP TABLE IF EXISTS locations")

# Create tables
mycursor.execute(
    "CREATE TABLE lectures (code VARCHAR(7) PRIMARY KEY, name VARCHAR(100), no_slots INT, discipline VARCHAR(30), "
    "room_reqs VARCHAR(100), no_students INT)")
mycursor.execute("CREATE TABLE lecturers (id INT PRIMARY KEY, name VARCHAR(50), unavailable_times VARCHAR(100))")
mycursor.execute("CREATE TABLE students (id INT PRIMARY KEY, name VARCHAR(50), course VARCHAR(7))")
mycursor.execute(
    "CREATE TABLE locations (room_code VARCHAR(7) PRIMARY KEY, name VARCHAR(50), room_type VARCHAR(20), capacity INT, "
    "discipline VARCHAR(30), unavailable_times VARCHAR(50))")

mycursor.execute(
    "CREATE TABLE lecture_lecturers (lecture VARCHAR(7), lecturer INT, FOREIGN KEY(lecture) REFERENCES lectures(code), "
    "FOREIGN KEY(lecturer) REFERENCES lecturers(id))")
mycursor.execute(
    "CREATE TABLE enrollments (lecture VARCHAR(7), class_group VARCHAR(7), FOREIGN KEY(lecture) REFERENCES lectures(code))")

# Fill
# Lectures
sql = "INSERT INTO lectures (code, name, no_slots, discipline, room_reqs, no_students) VALUES (%s, %s, %s, %s, %s, %s)"
val = []
for x in range(1, 51):
    code = "LEC" + str(x)
    name = "Lecture " + str(x)
    no_slots = random.randint(1, 3)
    discipline = "Discipline " + str(random.randint(1, 5))
    room_reqs = None
    if random.randint(1, 10) == 4:
        room_reqs = "Room " + str(random.randint(1, 3))
    val.append((code, name, no_slots, discipline, room_reqs, 0))

mycursor.executemany(sql, val)

# Lecturers
sql = "INSERT INTO lecturers (id, name, unavailable_times) VALUES (%s, %s, %s)"
val = []
for x in range(1, 21):
    id = x
    name = "Lecturer " + str(x)
    unavailable_times = ""
    while random.randint(1, 10) == 4:
        unavailable_times = unavailable_times + "Day " + str(random.randint(1, 5)) + " Time " + str(random.randint(1,8))
    if unavailable_times == "":
        unavailable_times = None
    val.append((id, name, unavailable_times))

mycursor.executemany(sql, val)

# Students
sql = "INSERT INTO students (id, name, course) VALUES (%s, %s, %s)"
val = []
for x in range(1, 501):
    id = x
    name = "Student " + str(x)
    course = "Cl " + str(random.randint(1, 30))
    if random.randint(1, 10) == 4:
        room_reqs = "Room " + str(random.randint(1, 3))
    val.append((id, name, course))

mycursor.executemany(sql, val)

# Locations
sql = "INSERT INTO locations (room_code, name, room_type, capacity, discipline, unavailable_times) VALUES (%s, %s, %s, %s, %s, %s)"
val = []
for x in range(1, 31):
    room_code = str(x)
    name = "Room " + str(x)
    room_type = "Room " + str(random.randint(1, 3))
    capacity = random.randint(1,30)*10
    discipline = "Discipline " + str(random.randint(1, 5))
    unavailable_times = ""
    while random.randint(1, 10) == 4:
        unavailable_times = unavailable_times + "Day " + str(random.randint(1, 5)) + " Time " + str(
            random.randint(1, 8))
    if unavailable_times == "":
        unavailable_times = None
    val.append((room_code, name, room_type, capacity, discipline, unavailable_times))

mycursor.executemany(sql, val)

mydb.commit()

#Enrollments
sql = "INSERT INTO enrollments (lecture, class_group) VALUES (%s, %s)"
val = []
lects_per_class= {}
# Give each lecture students
for x in range(1,51):
    lecture_id = "LEC" + str(x)
    student_set = set({})
    course_set = set({})
    num_courses = random.randint(1,8)
    while len(course_set) < num_courses:
        course = "Cl " + str(random.randint(1, 30))
        if course not in lects_per_class.keys() or lects_per_class[course] < 8:
            print("Found suitable course")
            if course in lects_per_class.keys():
                lects_per_class[course] = lects_per_class[course] + 1
            else:
                lects_per_class[course] = 1
            mycursor.execute("SELECT * FROM students WHERE course = %s", [course])
            students = mycursor.fetchall()
            for student in students:
                student_set.add(student[0])
            course_set.add(course)
    for course in course_set:
        val.append((lecture_id,course))
    sql2 = "UPDATE lectures SET no_students = %s WHERE code = %s"
    val2 = (len(student_set), lecture_id)
    mycursor.execute(sql2,val2)

mycursor.executemany(sql, val)


#Lecture_lecturers
sql = "INSERT INTO lecture_lecturers (lecture, lecturer) VALUES (%s, %s)"
val = []

# Give each lecture lecturer(s)
for x in range(1,51):
    lecture_id = "LEC" + str(x)
    lecturer_set = set({})
    num_lecturers = 1
    if random.randint(1,20) == 4:
        num_lecturers = 2
    while len(lecturer_set)<num_lecturers:
        lecturer_set.add(random.randint(1,20))
    for lecturer in lecturer_set:
        val.append((lecture_id,lecturer))
# Ignore unassigned lecturers for now

mycursor.executemany(sql, val)
mydb.commit()
