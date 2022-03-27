# Code for updating an existing timetable
import database_new
import files
import random

global lecture_arr, location_arr, time_arr, lecturer_arr, class_arr


def main(imported=False, filename=None, timetable=None):
    # Retrieve timetable info, either from import or database
    timetable = timetable
    if imported:
        timetable = getImportData(filename)
    else:
        getDataFromDatabase()
    # Call relevant function for desired output
    # Create random lectures to add
    new_lectures = []
    for x in range(10):
        lecture_id = 50 + x
        name = "New Lecture " + str(x)
        disc = "Discipline " + str(random.randint(1, 5))
        no_classes = random.randint(3,6)
        classes = []
        for y in range(no_classes):
            id = random.randint(0,29)
            if id not in classes:
                classes.append(id)
        no_students = 0
        for c in classes:
            no_students = no_students + class_arr[c].no_students
            class_arr[c].lectures.append(lecture_id)
        lecturer = random.randint(0,19)
        lecturer_arr[lecturer].lectures.append(lecture_id)
        new_lectures.append((database_new.Lecture(lecture_id, name, disc,no_students,lecturer,classes)))
    best_table = addLectures(new_lectures,timetable)
    print(best_table)
    print(scoreUpdate(best_table,timetable,50))
    scoreUpdateDetailed(best_table, timetable, len(timetable))
    files.printTimetableToCSV(best_table,"updated")


def getDataFromDatabase():
    global lecture_arr, location_arr, time_arr, lecturer_arr, class_arr
    lecture_arr = database_new.getLectures()
    location_arr = database_new.getLocations()
    time_arr = database_new.getTimes()
    lecturer_arr = database_new.getLecturers()
    class_arr = database_new.getClasses()


def getImportData(filename):
    global lecture_arr, location_arr, time_arr, lecturer_arr, class_arr
    data = files.importTimetable(filename)
    lecture_arr = data[1]
    location_arr = data[2]
    time_arr = data[3]
    lecturer_arr = data[4]
    class_arr = data[5]
    return data[0]


def addLectures(lectures, timetable):
    # Assign each lecture a slot at the end of the table, keeping track of the originals
    original_lec_count = len(lecture_arr)
    for lecture in lectures:
        lecture_arr.append(lecture)
    # Create initial population based on the old table
    population = []
    for x in range(100):
        new_table = timetable.copy()
        while len(new_table) < len(lecture_arr):
            new_table.append([random.randint(1,5),random.randint(1,8)])
        population.append(new_table)
    for x in range(10000):
        population = generateNextPopulation(population, timetable, original_lec_count)
    print(population[0])
    print(scoreUpdate(population[0], timetable, original_lec_count))
    return population[0]


def generateNextPopulation(curr_pop, original, original_lect_count):
    # Score current population
    score_dict = {}
    for x in range(len(curr_pop)):
        table = curr_pop[x]
        score_dict[x] = scoreUpdate(table, original, original_lect_count)
    # Create next population
    new_pop = []
    while len(new_pop) < len(curr_pop):
        # Pick two tables to combine
        # Method - pick 5 tables at random, choose best scoring of these
        first_table_index = random.randint(0, len(curr_pop) - 1)
        for x in range(5):
            index = random.randint(0, len(curr_pop) - 1)
            if score_dict[index] > score_dict[first_table_index]:
                first_table_index = index
        second_table_index = random.randint(0, len(curr_pop) - 1)
        for x in range(5):
            index = random.randint(0, len(curr_pop) - 1)
            if score_dict[index] > score_dict[second_table_index]:
                second_table_index = index
        first_table = curr_pop[first_table_index]
        second_table = curr_pop[second_table_index]
        # Cross-over - combine tables
        # Method - pick random cross-point, reverse second table, combine start of one with end of other
        cross_point = random.randint(0, len(lecture_arr) - 1)
        new_table = []
        for x in range(len(lecture_arr)):
            if x < cross_point:
                new_table.append(first_table[x])
            else:
                new_table.append(second_table[len(first_table) - x - 1])
        # Mutation - change table
        # Method - randomly reassign one value (with a greater chance of changing the new lectures values)
        weights = [1 for x in range(original_lect_count)]
        while len(weights)<len(lecture_arr):
            weights.append(100)
        lecture = random.choices(range(len(lecture_arr)),weights=weights)
        print(lecture)
        new_table[lecture[0]] = [random.randint(0, len(location_arr) - 1), random.randint(0, len(time_arr) - 1)]
        new_pop.append(new_table)
    # Merge new and old populations into final populations
    # Merge old and new tables
    merged_pop = curr_pop + new_pop
    # Sort population based on scores
    sorted_merged_pop = sorted(merged_pop, key=lambda i: scoreUpdate(i, original, original_lect_count), reverse=True)
    # Take best into final
    final_pop = []
    for x in range(len(curr_pop)):
        final_pop.append(sorted_merged_pop[x])
    # print("Best: "+str(score(final_pop[0]))+"\t\tWorst: "+str(score(final_pop[-1])))
    return final_pop


def scoreUpdate(timetable, original_table, original_lect_count):
    total = 0
    # Hard requirements
    # Check if two lectures on in same time and place
    for x in range(len(timetable)):
        lecture = lecture_arr[x]
        if timetable.count(timetable[x]) > 1:
            total = total - 1
        # Check if room big enough
        location = location_arr[timetable[x][0]]
        if lecture.no_students > location.capacity:
            total = total - 1
    # Check if lecturer not free
    for lecturer in lecturer_arr:
        lectures = lecturer.lectures
        lecture_times = [timetable[lecture][1] for lecture in lectures]
        for time in lecture_times:
            if lecture_times.count(time) > 1:
                total = total - 1
    # Check if class not free
    for class_group in class_arr:
        lectures = class_group.lectures
        lecture_times = [timetable[lecture][1] for lecture in lectures]
        for time in lecture_times:
            if lecture_times.count(time) > 1:
                total = total - 1
    # Soft Requirements - Only check if hard requirements all pass
    if total == 0:
        total = 100
        # If possible, the lecture should take place in a relevant building
        for lecture_id in range(len(lecture_arr)):
            if lecture_arr[lecture_id].discipline == location_arr[timetable[lecture_id][0]].discipline:
                total = total + 1
            # A lecture should not take place in a room that’s too big
            room_cap = location_arr[timetable[lecture_id][0]].capacity
            extra_space = room_cap - lecture_arr[lecture_id].no_students
            # Reduce score by 1 for every 10% of the room that's empty
            percent_empty = (extra_space / room_cap) * 100
            while percent_empty > 20:
                total = total - 1
                percent_empty = percent_empty - 20
        # Students should not have too many lectures in a row or huge gaps between lectures
        for class_group in class_arr:
            lectures = class_group.lectures
            lecture_times = [timetable[lecture][1] for lecture in lectures]
            gap, run = getGapRun(lecture_times)
            if gap > 3:
                total = total - 1
            if run > 3:
                total = total - 1
        # Lecturers should not have too many lectures in a row or huge gaps between lectures
        for lecturer in lecturer_arr:
            lectures = lecturer.lectures
            lecture_times = [timetable[lecture][1] for lecture in lectures]
            gap, run = getGapRun(lecture_times)
            if gap > 3:
                total = total - 1
            if run > 3:
                total = total - 1
    # Then, compare new to original
        for x in range(original_lect_count):
            if timetable[x] == original_table[x]:
                total = total + 1
    return total


def getGapRun(lecture_times):
    days = {}
    longest_run = 0
    longest_gap = 0
    for atime in lecture_times:
        time = time_arr[atime]
        if time[0] in days:
            days[time[0]].append(time[1])
        else:
            days[time[0]] = [time[1]]
    for day in days:
        if len(day) == 1:
            continue
        else:
            curr_gap = 0
            curr_run = 0
            day = sorted(day)
            x = day[0]
            is_gap = False
            while x <= day[-1]:
                if x in day and not is_gap:
                    curr_run = curr_run + 1
                elif x in day and is_gap:
                    if curr_gap > longest_gap:
                        longest_gap = curr_gap
                    curr_gap = 0
                    curr_run = 1
                elif x not in day and is_gap:
                    curr_gap = curr_gap + 1
                elif x not in day and not is_gap:
                    if curr_run > longest_run:
                        longest_run = curr_run
                    curr_run = 0
                    curr_gap = 1
                else:
                    print("that's not good")
    return longest_gap, longest_run


def scoreUpdateDetailed(timetable, original_table, original_lect_count):
    print(timetable)
    total = 0
    # Hard requirements
    # Check if two lectures on in same time and place
    for x in range(len(timetable)):
        lecture = lecture_arr[x]
        if timetable.count(timetable[x]) > 1:
            print("collision")
            total = total - 1
        # Check if room big enough
        location = location_arr[timetable[x][0]]
        if lecture.no_students > location.capacity:
            print("room too small")
            total = total - 1
    # Check if lecturer not free
    for lecturer in lecturer_arr:
        lectures = lecturer.lectures
        lecture_times = [timetable[lecture][1] for lecture in lectures]
        for time in lecture_times:
            if lecture_times.count(time) > 1:
                print("lecturer clash")
                total = total - 1
    # Check if class not free
    for class_group in class_arr:
        lectures = class_group.lectures
        lecture_times = [timetable[lecture][1] for lecture in lectures]
        for time in lecture_times:
            if lecture_times.count(time) > 1:
                print("class clash")
                total = total - 1
    # Soft Requirements - Only check if hard requirements all pass
    print(total)
    if total == 0:
        total = 100
        # If possible, the lecture should take place in a relevant building
        for lecture_id in range(len(lecture_arr)):
            if lecture_arr[lecture_id].discipline == location_arr[timetable[lecture_id][0]].discipline:
                total = total + 1

            # A lecture should not take place in a room that’s too big
            room_cap = location_arr[timetable[lecture_id][0]].capacity
            extra_space = room_cap - lecture_arr[lecture_id].no_students
            # Reduce score by 1 for every 20% of the room that's empty
            percent_empty = (extra_space/room_cap)*100
            if percent_empty > 20:
                print("location too big for lecture "+lecture_arr[lecture_id].name+" by percent "+str(percent_empty))
            while percent_empty > 20:
                total = total - 1
                percent_empty = percent_empty - 20
        # Students should not have too many lectures in a row or huge gaps between lectures
        for class_group in class_arr:
            lectures = class_group.lectures
            lecture_times = [timetable[lecture][1] for lecture in lectures]
            gap, run = getGapRun(lecture_times)
            if gap > 3:
                print("Class " + str(class_group.id) + " has gap of " + str(gap))
                total = total - 1
            if run > 3:
                print("Class " + str(class_group.id) + " has run of " + str(run))
                total = total - 1
        # Lecturers should not have too many lectures in a row or huge gaps between lectures
        for lecturer in lecturer_arr:
            lectures = lecturer.lectures
            lecture_times = [timetable[lecture][1] for lecture in lectures]
            gap, run = getGapRun(lecture_times)
            if gap > 3:
                print("Lecturer "+str(lecturer.id)+" has gap of "+str(gap))
                total = total - 1
            if run > 3:
                print("Lecturer " + str(lecturer.id) + " has run of " + str(run))
                total = total - 1
        # Then, compare new to original
        for x in range(original_lect_count):
            if timetable[x] == original_table[x]:
                total = total + 1
            else:
                print("Timetable slot "+str(x)+" changed")
    else:
        print("Hard requirements not passed")

    return total
