# Functions for importing and exporting timetables as files
import pickle
import database_new

# Import details from database
global lecture_arr, location_arr, time_arr, lecturer_arr, class_arr


def getDataFromDatabase():
    global lecture_arr, location_arr, time_arr, lecturer_arr, class_arr
    lecture_arr = database_new.getLectures()
    location_arr = database_new.getLocations()
    time_arr = database_new.getTimes()
    lecturer_arr = database_new.getLecturers()
    class_arr = database_new.getClasses()


def importTimetable(filename):
    global lecture_arr, location_arr, time_arr, lecturer_arr, class_arr
    # Export files contain all necessary info
    input_file = open(filename, 'rb')
    timetable = []
    try:
        timetable = pickle.load(input_file)
        lecture_arr = pickle.load(input_file)
        location_arr = pickle.load(input_file)
        time_arr = pickle.load(input_file)
        lecturer_arr = pickle.load(input_file)
        class_arr = pickle.load(input_file)
    except EOFError:
        print("eof")
    input_file.close()  # Close the file
    return [timetable, lecture_arr, location_arr, time_arr, lecturer_arr, class_arr]


def exportTimetable(timetable, filename):
    getDataFromDatabase()
    out_file = open(filename, 'wb')
    pickle.dump(timetable, out_file)
    pickle.dump(lecture_arr, out_file)
    pickle.dump(location_arr, out_file)
    pickle.dump(time_arr, out_file)
    pickle.dump(lecturer_arr, out_file)
    pickle.dump(class_arr, out_file)
    out_file.close()


def printTimetableToCSV(timetable):
    getDataFromDatabase()
    time_dict = {}
    for lecture_id in range(len(lecture_arr)):
        if timetable[lecture_id][1] in time_dict:
            time_dict[timetable[lecture_id][1]].add((lecture_id, timetable[lecture_id][0]))
        else:
            time_dict[timetable[lecture_id][1]] = {(lecture_id, timetable[lecture_id][0])}
    f = open("output/timetable.csv", "w")
    f.write("")
    f.close()
    f = open("output/timetable.csv", "a")
    for time in range(len(time_arr)):
        if time in time_dict:
            for entry in time_dict[time]:
                out = time_arr[time] + "," + lecture_arr[entry[0]].name + "," + location_arr[entry[1]].name + "," + \
                      lecture_arr[entry[0]].lecturer.name + "," + lecture_arr[entry[0]].class_groups + "\n"
                f.write(out)
        else:
            out = time_arr[time] + ",,,,\n"
            f.write(out)
    f.close()


def printLecturerTimetableToCSV(timetable, lecturer_id):
    getDataFromDatabase()
    time_dict = {}
    lecturer = lecturer_arr[lecturer_id]
    for lecture_id in lecturer.lectures:
        time_dict[timetable[lecture_id][1]] = [lecture_id, timetable[lecture_id][0]]
    f = open("output/" + lecturer.name + ".csv", "w")
    f.write("")
    f.close()
    f = open("output/" + lecturer.name + ".csv", "a")
    for time in time_arr:
        if time in time_dict:
            out = time_arr[time] + "," + lecture_arr[time_dict[time][0]].name + "," + \
                  location_arr[time_dict[time][1]].name + "," + lecture_arr[time_dict[time][0]].lecturer.name + "," + \
                  lecture_arr[time_dict[time][0]].class_groups + "\n"
            f.write(out)
        else:
            out = time_arr[time] + ",,,,\n"
        f.write(out)
    f.close()


def printClassTimetableToCSV(timetable, class_id):
    time_dict = {}
    class_group = class_arr[class_id]
    for lecture_id in class_group.lectures:
        time_dict[timetable[lecture_id][1]] = [lecture_id, timetable[lecture_id][0]]
    f = open("output/" + class_group.name + ".csv", "w")
    f.write("")
    f.close()
    f = open("output/" + class_group.name + ".csv", "a")
    for time in time_arr:
        if time in time_dict:
            out = time_arr[time] + "," + lecture_arr[time_dict[time][0]].name + "," + \
                  location_arr[time_dict[time][1]].name + "," + lecture_arr[time_dict[time][0]].lecturer.name + "," + \
                  lecture_arr[time_dict[time][0]].class_groups + "\n"
            f.write(out)
        else:
            out = time_arr[time] + ",,,,\n"
        f.write(out)
    f.close()


def printRoomTimetableToCSV(timetable, room_id):
    time_dict = {}
    room = location_arr[room_id]
    for lecture_id in range(len(lecture_arr)):
        if timetable[lecture_id][0] == room_id:
            time_dict[timetable[lecture_id][1]] = [lecture_id, timetable[lecture_id][0]]
    f = open("output/" + room.name + ".csv", "w")
    f.write("")
    f.close()
    f = open("output/" + room.name + ".csv", "a")
    for time in time_arr:
        if time in time_dict:
            out = time_arr[time] + "," + lecture_arr[time_dict[time][0]].name + "," + \
                  location_arr[time_dict[time][1]].name + "," + lecture_arr[time_dict[time][0]].lecturer.name + "," + \
                  lecture_arr[time_dict[time][0]].class_groups + "\n"
            f.write(out)
        else:
            out = time_arr[time] + ",,,,\n"
        f.write(out)
    f.close()
