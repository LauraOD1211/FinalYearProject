import random
import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="geneticDatabase",
    database="remake"
)

mycursor = mydb.cursor()

# Clear
mycursor.execute("DROP TABLE IF EXISTS enrollments")
mycursor.execute("DROP TABLE IF EXISTS lectures")
mycursor.execute("DROP TABLE IF EXISTS lecturers")
mycursor.execute("DROP TABLE IF EXISTS locations")
mycursor.execute("DROP TABLE IF EXISTS classes")

# Create tables
mycursor.execute(
    "CREATE TABLE lectures (id INT PRIMARY KEY, name VARCHAR(100), discipline VARCHAR(30), no_students INT, class_groups VARCHAR(100), lecturer INT)")
mycursor.execute("CREATE TABLE lecturers (id INT PRIMARY KEY, name VARCHAR(50), lectures VARCHAR(100))")
mycursor.execute("CREATE TABLE classes (id INT PRIMARY KEY, name VARCHAR(50), no_students INT, lectures VARCHAR(100))")
mycursor.execute("CREATE TABLE locations (id INT PRIMARY KEY, name VARCHAR(50), capacity INT, discipline VARCHAR(30))")
mycursor.execute(
    "CREATE TABLE enrollments (lecture INT, class_group INT, FOREIGN KEY(lecture) REFERENCES lectures(id), FOREIGN KEY(class_group) REFERENCES classes(id))")

# Fill
# Lectures
sql = "INSERT INTO lectures (id, name, discipline, no_students, class_groups, lecturer) VALUES (%s, %s, %s, %s, %s, %s)"
val = []
for id in range(0, 50):
    name = "Lecture " + str(id)
    discipline = "Discipline " + str(random.randint(1, 5))
    val.append((id, name, discipline, 0, "[]", -1))

mycursor.executemany(sql, val)

# Lecturers
sql = "INSERT INTO lecturers (id, name, lectures) VALUES (%s, %s, %s)"
val = []
for id in range(0, 20):
    name = "Lecturer " + str(id)
    val.append((id, name, "[]"))

mycursor.executemany(sql, val)

# Classes
sql = "INSERT INTO classes (id, name, no_students, lectures) VALUES (%s, %s, %s, %s)"
val = []
class_size = []
for id in range(0, 30):
    name = "Course " + str(id)
    no_students = str(random.randint(10, 150))
    class_size.append(no_students)
    val.append((id, name, no_students, "[]"))

mycursor.executemany(sql, val)

# Locations
sql = "INSERT INTO locations (id, name, capacity, discipline) VALUES (%s, %s, %s, %s)"
val = []
for id in range(0, 30):
    name = "Room " + str(id)
    capacity = random.randint(3, 30) * 10
    discipline = "Discipline " + str(random.randint(1, 5))
    val.append((id, name, capacity, discipline))

mycursor.executemany(sql, val)

mydb.commit()

# Enrollments
sql = "INSERT INTO enrollments (lecture, class_group) VALUES (%s, %s)"
val = []
lects_by_class = {}
# Give each lecture students
for lecture_id in range(0, 50):
    no_students = 0
    class_set = []
    num_courses = random.randint(1, 5)
    while len(class_set) < num_courses and no_students < 200:
        class_id = random.randint(0, 29)
        while class_id in class_set:
            class_id = class_id + 1
        if class_id not in lects_by_class.keys() or len(lects_by_class[class_id]) < 8:
            if class_id in lects_by_class.keys():
                lects_by_class[class_id].append(lecture_id)
            else:
                lects_by_class[class_id] = [lecture_id]
            class_set.append(class_id)
            no_students = no_students + int(class_size[class_id])
    for id in class_set:
        val.append((lecture_id, id))
    sqlLect = "UPDATE lectures SET no_students = %s WHERE id = %s"
    valLect = (no_students, lecture_id)
    mycursor.execute(sqlLect, valLect)
    sqlLect = "UPDATE lectures SET class_groups = %s WHERE id = %s"
    valLect = (str(class_set), lecture_id)
    mycursor.execute(sqlLect, valLect)
for class_id in lects_by_class.keys():
    print("here")
    sqlClass = "UPDATE classes SET lectures = %s WHERE id = %s"
    valClass = (str(lects_by_class[class_id]), class_id)
    mycursor.execute(sqlClass, valClass)

mycursor.executemany(sql, val)

# Give each lecture a lecturer
lects_by_lecturer = {}
for lecture_id in range(0, 50):
    print(lecture_id)
    lecturer_id = random.randint(0,19)
    while lecturer_id in lects_by_lecturer.keys() and len(lects_by_lecturer[lecturer_id]) > 10:
        lecturer_id = random.randint(0,19)
    if lecturer_id in  lects_by_lecturer.keys():
        lects_by_lecturer[lecturer_id].append(lecture_id)
    else:
        lects_by_lecturer[lecturer_id] = [lecture_id]
    sqlLect = "UPDATE lectures SET lecturer = %s WHERE id = %s"
    valLect = (lecturer_id, lecture_id)
    mycursor.execute(sqlLect, valLect)

for lecturer_id in lects_by_lecturer.keys():
    sqlLect = "UPDATE lecturers SET lectures = %s WHERE id = %s"
    valLect = (str(lects_by_lecturer[lecturer_id]), lecturer_id)
    mycursor.execute(sqlLect, valLect)

mydb.commit()
print("setup done")