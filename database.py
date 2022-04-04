import mysql.connector
import json

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="geneticDatabase",
    database="remake"
)


class Lecture:
    def __init__(self, id, name, discipline, no_students, lecturer, class_groups):
        self.id = id
        self.name = name
        self.discipline = discipline
        self.lecturer = lecturer
        self.class_groups = class_groups
        self.no_students = no_students


class Location:
    def __init__(self, id, name, discipline, capacity):
        self.id = id
        self.name = name
        self.discipline = discipline
        self.capacity = capacity


class Lecturer:
    def __init__(self, id, name, lectures):
        self.id = id
        self.name = name
        self.lectures = lectures


class ClassGroup:
    def __init__(self, id, name, no_students, lectures):
        self.id = id
        self.name = name
        self.no_students = no_students
        self.lectures = lectures


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
    lecturer = Lecturer(id=x[0], name=x[1], lectures=lectures)
    lecturer_arr.append(lecturer)

# Get all classes
cursor.execute("SELECT * FROM classes")

results = cursor.fetchall()

for x in results:
    lectures = json.loads(x[3])
    class_group = ClassGroup(id=x[0], name=x[1], no_students=x[2], lectures=lectures)
    class_arr.append(class_group)

# Get all locations
cursor.execute("SELECT * FROM locations")

results = cursor.fetchall()

for x in results:
    location = Location(id=x[0], name=x[1], capacity=x[2], discipline=x[3])
    location_arr.append(location)

# Get all lectures
cursor.execute("SELECT * FROM lectures")

results = cursor.fetchall()

for x in results:
    class_groups = json.loads(x[4])
    lecture = Lecture(id=x[0], name=x[1], discipline=x[2], no_students=x[3], class_groups=class_groups, lecturer=x[5])
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
    for x in range(len(days)):
        for y in range(len(hours)):
            time = [days[x], hours[y]]
            times.append(time)
    return times
