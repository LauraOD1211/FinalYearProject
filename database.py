import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="geneticDatabase",
    database="mockcollegedata"
)


class Lecture:
    def __init__(self, code, name, timeslots, room_reqs, discipline, lecturers, class_groups, no_students):
        self.code = code
        self.name = name
        self.timeslots = timeslots
        self.room_reqs = room_reqs
        self.discipline = discipline
        self.lecturers = lecturers
        self.class_groups = class_groups
        self.no_students = no_students

class Location:
    def __init__(self, code, name, discipline, room_type, capacity, unavailable_times):
        self.code = code
        self.name = name
        self.discipline = discipline
        self.room_type = room_type
        self.capacity = capacity
        self.unavailable_times = unavailable_times



class Lecturer:
    def __init__(self, staff_id, unavailable_times):
        self.staff_id = staff_id
        self.unavailable_times = unavailable_times


lectures = []
lecturers = []
locations = []

cursor = mydb.cursor()

# Get all lecturers
cursor.execute("SELECT * FROM lecturers")

results = cursor.fetchall()

for x in results:
    lecturer = Lecturer(staff_id=x[0], unavailable_times=x[1])
    lecturers.append(lecturer)

# Get all locations
cursor.execute("SELECT * FROM locations")

results = cursor.fetchall()

for x in results:
    location = Location(code=x[0], name=x[1], discipline=x[4], room_type=x[2], capacity=x[3], unavailable_times=x[5])
    locations.append(location)

# Get all lectures
cursor.execute("SELECT * FROM lectures")

results = cursor.fetchall()

for x in results:
    lecture_id = [x[0]]
    sql = "SELECT class_group FROM enrollments WHERE lecture = %s"
    cursor.execute(sql, lecture_id)
    groups = cursor.fetchall()
    sql = "SELECT lecturer FROM lecture_lecturers WHERE lecture = %s"
    cursor.execute(sql, lecture_id)
    lecturer_ids = cursor.fetchall()
    lecturer_list = []
    for lecturer in lecturers:
        if lecturer.staff_id in lecturer_ids:
            lecturer_list.append(lecturer)

    lecture = Lecture(code=x[0], name=x[1], timeslots=x[2], room_reqs=x[4], discipline=x[3], lecturers=lecturer_list,
                      class_groups=groups, no_students=x[5])
    lectures.append(lecture)


def getLectures():
    return lectures


def getLecturers():
    return lecturers


def getLocations():
    return locations
