# Functions for importing and exporting timetables as files
import pickle

from database import getTimes


def importTimetable(filename):
    input_file = open('employee.dat', 'rb')
    try:
        timetable = pickle.load(input_file)
    except EOFError:
        print("eof")
    input_file.close()  # Close the file


def exportTimetable(timetable, filename):
    out_file = open(filename, 'wb')
    pickle.dump(timetable, out_file)
    out_file.close()


def printTimetableToCSV(timetable):
    time_dict = {}
    for entry in timetable:
        if timetable[entry][1] in time_dict:
            time_dict[timetable[entry][1]].add((entry, timetable[entry][0]))
        else:
            time_dict[timetable[entry][1]] = {(entry, timetable[entry][0])}
    f = open("output/timetable.csv", "w")
    f.write("")
    f.close()
    f = open("output/timetable.csv", "a")
    for time in getTimes():
        if time in time_dict:
            for lecture in time_dict[time]:
                out = time + "," + lecture[0].name + "," + lecture[1].name + "," + lecture[0].lecturers[0].name + "\n"
                f.write(out)
        else:
            out = time + ",,,\n"
            f.write(out)
    f.close()


def printLecturerTimetableToCSV(timetable, lecturer):
    time_dict = {}
    for entry in timetable:
        if lecturer in entry.lecturers:
            time_dict[timetable[entry][1]] = [entry, timetable[entry][0]]
    f = open("output/" + lecturer.name + ".csv", "w")
    f.write("")
    f.close()
    f = open("output/" + lecturer.name + ".csv", "a")
    for time in getTimes():
        out = time + ","
        if time in time_dict:
            out = out + time_dict[time][0].name + "," + time_dict[time][1].name + "," + time_dict[time][0].lecturers[
                0].name + "\n"
        else:
            out = out + ",,\n"
        f.write(out)
    f.close()


def printClassTimetableToCSV(timetable, group):
    time_dict = {}
    for entry in timetable:
        if group in entry.class_groups:
            time_dict[timetable[entry][1]] = [entry, timetable[entry][0]]
    f = open("output/" + group + ".csv", "w")
    f.write("")
    f.close()
    f = open("output/" + group + ".csv", "a")
    for time in getTimes():
        out = time + ","
        if time in time_dict:
            out = out + time_dict[time][0].name + "," + time_dict[time][1].name + "," + time_dict[time][0].lecturers[
                0].name + "\n"
        else:
            out = out + ",,\n"
        f.write(out)
    f.close()


def printRoomTimetableToCSV(timetable, room):
    time_dict = {}
    for entry in timetable:
        if room == timetable[entry][0]:
            time_dict[timetable[entry][1]] = [entry, timetable[entry][0]]
    f = open("output/" + room.name + ".csv", "w")
    f.write("")
    f.close()
    f = open("output/" + room.name + ".csv", "a")
    for time in getTimes():
        out = time + ","
        if time in time_dict:
            out = out + time_dict[time][0].name + "," + time_dict[time][1].name + "," + time_dict[time][0].lecturers[
                0].name + "\n"
        else:
            out = out + ",,\n"
        f.write(out)
    f.close()
