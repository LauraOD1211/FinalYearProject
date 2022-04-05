# Code for updating an existing timetable
import database
import files
import random

global lecture_arr, location_arr, time_arr, lecturer_arr, class_arr


def demo():
    getDataFromDatabase()
    # Create random lectures to add
    new_lectures = []
    for x in range(10):
        lecture_id = 50 + x
        name = "New Lecture " + str(x)
        disc = "Discipline " + str(random.randint(1, 5))
        no_classes = random.randint(3, 6)
        classes = []
        for y in range(no_classes):
            class_id = random.randint(0, 29)
            if class_id not in classes:
                classes.append(class_id)
        no_students = 0
        for c in classes:
            no_students = no_students + class_arr[c].no_students
        lecturer = random.randint(0, 19)
        new_lectures.append((database.Lecture(lecture_id, name, disc, no_students, lecturer, classes)))
    # Call main
    table = [[16, 7], [6, 40], [7, 43], [3, 32], [19, 34], [4, 21], [23, 19], [5, 33], [14, 17], [17, 13], [17, 15],
             [23, 36], [16, 4], [19, 6], [7, 26], [0, 8], [10, 11], [10, 5], [16, 5], [2, 13], [12, 9], [3, 20],
             [22, 12], [16, 29], [23, 8], [13, 24], [0, 10], [22, 24], [12, 11], [21, 14], [16, 18], [22, 7], [19, 22],
             [16, 30], [7, 16], [7, 28], [15, 29], [3, 0], [19, 38], [15, 17], [22, 1], [19, 33], [21, 35], [12, 25],
             [28, 22], [13, 10], [3, 13], [12, 13], [19, 18], [16, 15]]
    main("add lectures", new_lectures, timetable=table, outfile="add")
    main("update lecture", [16, new_lectures[0]], timetable=table, outfile="update")
    main("remove room", 16, timetable=table, outfile="remove")


def main(mode, data, imported=False, filename=None, timetable=None, outfile="out"):
    # Retrieve timetable info, either from import or database
    timetable = timetable
    if imported:
        timetable = getImportData(filename)
    else:
        getDataFromDatabase()
    # Call relevant function for desired output
    if mode == "add lectures":
        result = addLectures(data, timetable)
    elif mode == "update lecture":
        result = updateLecture(data, timetable)
    elif mode == "remove room":
        result = removeRoom(data, timetable)
    else:
        print("Invalid mode, valid modes are:\nadd lectures\nupdate lecture\nremove room")
        return
    print(result)
    files.printTimetableToCSV(result, outfile)


def getDataFromDatabase():
    global lecture_arr, location_arr, time_arr, lecturer_arr, class_arr
    lecture_arr = database.getLectures()
    location_arr = database.getLocations()
    time_arr = database.getTimes()
    lecturer_arr = database.getLecturers()
    class_arr = database.getClasses()


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
    # Setup data and generate initial population
    population = addSetup(lectures, timetable)
    # Run genetic algorithm
    for x in range(100):
        population = addGenerateNextPop(population, timetable)
    return population[0]


def addSetup(lectures, timetable):
    # Add lecture information to datalists
    for lecture in lectures:
        # Add lecture to lecture_arr
        lecture_arr.append(lecture)
        # Add lecture to classes in class_arr
        for class_id in lecture.class_groups:
            class_arr[class_id].lectures.append(lecture_arr.index(lecture))
        # Add lecture to lecturer in lecturer_arr
        lecturer_arr[lecture.lecturer].lectures.append(lecture_arr.index(lecture))
    # Generate new timetable population
    population = []
    for x in range(100):
        # Make each table copy of original, then add random values for extra lectures
        new_table = timetable.copy()
        while len(new_table) < len(lecture_arr):
            new_table.append([random.randint(0, len(location_arr) - 1), random.randint(0, len(time_arr) - 1)])
        population.append(new_table)
    return population


def addGenerateNextPop(curr_pop, original_table):
    # Score current population
    score_dict = {}
    for x in range(len(curr_pop)):
        table = curr_pop[x]
        score_dict[x] = addScore(table, original_table)
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
        # Method - pick cross-point somewhere in middle of added lectures, combine together
        cross_point = random.randint(len(original_table), len(lecture_arr) - 1)
        new_table = []
        for x in range(len(lecture_arr)):
            if x < cross_point:
                new_table.append(first_table[x])
            else:
                new_table.append(second_table[x])
        # Mutation - change table
        # Method - randomly reassign one value (with a greater chance of changing the new lectures values)
        weights = [1 for _ in range(len(original_table))]
        while len(weights) < len(lecture_arr):
            weights.append(100)
        lecture = random.choices(range(len(lecture_arr)), weights=weights)
        new_entry = [random.randint(0, len(location_arr) - 1), random.randint(0, len(time_arr) - 1)]
        while new_entry in new_table:
            new_entry = [random.randint(0, len(location_arr) - 1), random.randint(0, len(time_arr) - 1)]
        new_table[lecture[0]] = new_entry
        new_pop.append(new_table)
    # Merge new and old populations into final populations
    # Merge old and new tables
    merged_pop = curr_pop + new_pop
    # Sort population based on scores
    sorted_merged_pop = sorted(merged_pop, key=lambda i: addScore(i, original_table), reverse=True)
    # Take best into final
    final_pop = []
    for x in range(len(curr_pop)):
        final_pop.append(sorted_merged_pop[x])
    return final_pop


def addScore(timetable, original_table):
    # Score table using normal scoring algorithm
    total = score(timetable)
    # Then do special scoring - compare new to original
    # Check hard requirements pass
    if total > 0:
        # Check each original lecture unchanged
        for x in range(len(original_table)):
            if timetable[x] == original_table[x]:
                total = total + 1
    return total


def updateLecture(lecture_info, timetable):
    # Setup data and generate initial population
    population = updateSetup(lecture_info, timetable)
    # Run genetic algorithm
    for x in range(100):
        population = updateGenerateNextPop(population, timetable, lecture_info[0])
    return population[0]


def updateSetup(lecture_info, timetable):
    # Inputted data specifies index of lecture to be replaced and the new lecture object
    lect_index = lecture_info[0]
    new_lecture = lecture_info[1]
    # Update class info to match new lecture
    if lecture_arr[lect_index].class_groups != new_lecture.class_groups:
        for class_group in lecture_arr[lect_index].class_groups:
            class_arr[class_group].lectures.remove(lect_index)
        for class_group in new_lecture.class_groups:
            class_arr[class_group].lectures.append(lect_index)
    # Update lecturer info to match new lecture
    if lecture_arr[lect_index].lecturer != new_lecture.lecturer:
        lecturer_arr[lecture_arr[lect_index].lecturer].lectures.remove(lect_index)
        lecturer_arr[new_lecture.lecturer].lectures.append(lect_index)
    # Replace old lecture with new in array
    lecture_arr[lect_index] = new_lecture

    # Generate new timetable population
    population = []
    for x in range(100):
        # Make each table copy of original
        new_table = timetable.copy()
        population.append(new_table)
    return population


def updateGenerateNextPop(curr_pop, original_table, lecture_index):
    # Score current population
    score_dict = {}
    for x in range(len(curr_pop)):
        table = curr_pop[x]
        score_dict[x] = updateScore(table, original_table)
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
        # Method - pick cross-point anywhere in table
        cross_point = random.randint(0, len(lecture_arr) - 1)
        new_table = []
        for x in range(len(lecture_arr)):
            if x < cross_point:
                new_table.append(first_table[x])
            else:
                new_table.append(second_table[x])
        # Mutation - change table
        # Method - randomly reassign one value (with a greater chance of changing the new lecture values)
        weights = [1 for _ in range(len(original_table))]
        weights[lecture_index] = 100
        lecture = random.choices(range(len(lecture_arr)), weights=weights)
        new_entry = [random.randint(0, len(location_arr) - 1), random.randint(0, len(time_arr) - 1)]
        while new_entry in new_table:
            new_entry = [random.randint(0, len(location_arr) - 1), random.randint(0, len(time_arr) - 1)]
        new_table[lecture[0]] = new_entry
        new_pop.append(new_table)
    # Merge new and old populations into final populations
    # Merge old and new tables
    merged_pop = curr_pop + new_pop
    # Sort population based on scores
    sorted_merged_pop = sorted(merged_pop, key=lambda i: updateScore(i, original_table), reverse=True)
    # Take best into final
    final_pop = []
    for x in range(len(curr_pop)):
        final_pop.append(sorted_merged_pop[x])
    return final_pop


def updateScore(timetable, original_table):
    # Score table using normal scoring algorithm
    total = score(timetable)
    # Then do special scoring - compare new to original
    # Check hard requirements pass
    if total > 0:
        # Check each original lecture unchanged
        for x in range(len(original_table)):
            if timetable[x] == original_table[x]:
                total = total + 1
    return total


def removeRoom(room, timetable):
    # Setup data and generate initial population
    population = removeSetup(room, timetable)
    # Run genetic algorithm
    for x in range(100):
        population = removeGenerateNextPop(population, timetable, room)
    return population[0]


def removeSetup(room, timetable):
    # Cannot remove location object from array as this will change index of all other rooms
    # Instead, replace with None and add checks for this
    location_arr[room] = None
    # Generate new timetable population
    population = []
    for x in range(100):
        # Make each table copy of original, replace any that are in the bad room with random other room
        new_table = timetable.copy()
        for entry in new_table:
            if entry[0] == room:
                new_room = random.randint(0, len(location_arr) - 1)
                while new_room == room:
                    new_room = random.randint(0, len(location_arr) - 1)
                entry[0] = new_room
        population.append(new_table)
    return population


def removeGenerateNextPop(curr_pop, original_table, room):
    # Score current population
    score_dict = {}
    for x in range(len(curr_pop)):
        table = curr_pop[x]
        score_dict[x] = removeScore(table, original_table, room)
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
        # Method - pick cross-point anywhere in table
        cross_point = random.randint(0, len(lecture_arr) - 1)
        new_table = []
        for x in range(len(lecture_arr)):
            if x < cross_point:
                new_table.append(first_table[x])
            else:
                new_table.append(second_table[x])
        # Mutation - change table
        # Method - randomly reassign one value (with higher priority to affected lectures)
        weights = [1 for _ in range(len(original_table))]
        for x in range(len(original_table)):
            if original_table[x][0] == room:
                weights[x] = 100
        lecture = random.choices(range(len(lecture_arr)), weights=weights)
        # Don't randomly assign the removed room
        new_entry = [random.randint(0, len(location_arr) - 1), random.randint(0, len(time_arr) - 1)]
        while new_entry in new_table or new_entry[0] == room:
            new_entry = [random.randint(0, len(location_arr) - 1), random.randint(0, len(time_arr) - 1)]
        new_table[lecture[0]] = new_entry
        new_pop.append(new_table)
    # Merge new and old populations into final populations
    # Merge old and new tables
    merged_pop = curr_pop + new_pop
    # Sort population based on scores
    sorted_merged_pop = sorted(merged_pop, key=lambda i: removeScore(i, original_table, room), reverse=True)
    # Take best into final
    final_pop = []
    for x in range(len(curr_pop)):
        final_pop.append(sorted_merged_pop[x])
    return final_pop


def removeScore(timetable, original_table, room):
    # Before scoring, make sure room isn't in timetable
    for entry in timetable:
        if entry[0] == room:
            return -1000
    # Score table using normal scoring algorithm
    total = score(timetable)
    # Then do special scoring - compare new to original
    # Check hard requirements pass
    if total > 0:
        # Check each original lecture unchanged (except those in that room)
        for x in range(len(original_table)):
            if original_table[x][0] != room:
                if timetable[x] == original_table[x]:
                    total = total + 1
            # If lecture was in removed room, just check time
            else:
                if timetable[x][1] == original_table[x][1]:
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
        if len(days[day]) == 1:
            continue
        else:
            curr_gap = 0
            curr_run = 0
            day = sorted(days[day])
            hours = ["9am", "10am", "11am", "12pm", "1pm", "2pm", "3pm", "4pm", "5pm"]
            index = 0
            while hours[index] not in day:
                index = index + 1
            is_gap = False
            while index < len(hours) and hours[index - 1] != day[-1]:
                if hours[index] in day and not is_gap:
                    curr_run = curr_run + 1
                elif hours[index] in day and is_gap:
                    if curr_gap > longest_gap:
                        longest_gap = curr_gap
                    curr_gap = 0
                    curr_run = 1
                elif hours[index] not in day and is_gap:
                    curr_gap = curr_gap + 1
                elif hours[index] not in day and not is_gap:
                    if curr_run > longest_run:
                        longest_run = curr_run
                    curr_run = 0
                    curr_gap = 1
                else:
                    print("that's not good")
                index = index + 1
    return longest_gap, longest_run


def score(timetable):
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
        total = 200
        for lecture_id in range(len(lecture_arr)):
            # If possible, the lecture should take place in a relevant building
            if lecture_arr[lecture_id].discipline == location_arr[timetable[lecture_id][0]].discipline:
                total = total + 1
            # A lecture should not take place in a room that’s too big
            room_cap = location_arr[timetable[lecture_id][0]].capacity
            extra_space = room_cap - lecture_arr[lecture_id].no_students
            # Reduce score by 2 for every 20% of the room that's empty
            percent_empty = (extra_space / room_cap) * 100
            while percent_empty > 20:
                total = total - 2
                percent_empty = percent_empty - 20
            # Lectures should not be held after 12 on a friday
            if time_arr[timetable[lecture_id][1]][0] == "Fri" and time_arr[timetable[lecture_id][1]][1] in ["12pm",
                                                                                                            "1pm",
                                                                                                            "2pm",
                                                                                                            "3pm",
                                                                                                            "4pm",
                                                                                                            "5pm"]:
                total = total - 1
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
    return total
