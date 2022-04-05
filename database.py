import mysql.connector
import json

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="geneticDatabase",
    database="remake"
)


class Lecture:
    def __init__(self, lect_id, name, discipline, no_students, lect_lecturer, lect_class_groups):
        self.id = lect_id
        self.name = name
        self.discipline = discipline
        self.lecturer = lect_lecturer
        self.class_groups = lect_class_groups
        self.no_students = no_students


class Location:
    def __init__(self, loc_id, name, discipline, capacity):
        self.id = loc_id
        self.name = name
        self.discipline = discipline
        self.capacity = capacity


class Lecturer:
    def __init__(self, lect_id, name, lect_lectures):
        self.id = lect_id
        self.name = name
        self.lectures = lect_lectures


class ClassGroup:
    def __init__(self, class_id, name, no_students, class_lectures):
        self.id = class_id
        self.name = name
        self.no_students = no_students
        self.lectures = class_lectures


lecture_arr = []
location_arr = []
time_arr = []
lecturer_arr = []
class_arr = []

cursor = mydb.cursor()

# Get all lecturers
cursor.execute("SELECT * FROM lecturers")

results = cursor.fetchall()

for x in results:
    lectures = json.loads(x[2])
    lecturer = Lecturer(lect_id=x[0], name=x[1], lect_lectures=lectures)
    lecturer_arr.append(lecturer)

# Get all classes
cursor.execute("SELECT * FROM classes")

results = cursor.fetchall()

for x in results:
    lectures = json.loads(x[3])
    class_group = ClassGroup(class_id=x[0], name=x[1], no_students=x[2], class_lectures=lectures)
    class_arr.append(class_group)

# Get all locations
cursor.execute("SELECT * FROM locations")

results = cursor.fetchall()

for x in results:
    location = Location(loc_id=x[0], name=x[1], capacity=x[2], discipline=x[3])
    location_arr.append(location)

# Get all lectures
cursor.execute("SELECT * FROM lectures")

results = cursor.fetchall()

for x in results:
    class_groups = json.loads(x[4])
    lecture = Lecture(lect_id=x[0], name=x[1], discipline=x[2], no_students=x[3], lect_class_groups=class_groups,
                      lect_lecturer=x[5])
    lecture_arr.append(lecture)


def getLectures():
    return lecture_arr


def getLecturers():
    return lecturer_arr


def getLocations():
    return location_arr


def getClasses():
    return class_arr


def getTimes():
    days = ["Mon", "Tue", "Wed", "Thur", "Fri"]
    hours = ["9am", "10am", "11am", "12pm", "1pm", "2pm", "3pm", "4pm", "5pm"]
    times = []
    for i in range(len(days)):
        for j in range(len(hours)):
            time = [days[i], hours[j]]
            times.append(time)
    return times
