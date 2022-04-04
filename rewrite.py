import math
import random
# import database_setup
import database
import matplotlib.pyplot as plt

import files
import update

global lecture_arr, location_arr, time_arr, lecturer_arr, class_arr


def getDataFromDatabase():
    global lecture_arr, location_arr, time_arr, lecturer_arr, class_arr
    lecture_arr = database.getLectures()
    location_arr = database.getLocations()
    time_arr = database.getTimes()
    lecturer_arr = database.getLecturers()
    class_arr = database.getClasses()


def main():
    getDataFromDatabase()
    best_tables = []
    best_scores = []
    for x in range(1):
        best_tables.append(runGA(check_convergence=True, num_gens=50000, min_score=0))
        best_scores.append(score(best_tables[x]))
    if best_scores[0] < 0:
        print("No good timetable found")
        scoreDetailed(best_tables[0])
        return
    scoreDetailed(best_tables[0])
    files.printTimetableToCSV(best_tables[0],"original")
    update.main(timetable=best_tables[0])


def runGA(num_gens = 20000, min_score = 100, check_convergence=True, convergence_count=500):
    global lecture_arr, location_arr, time_arr, lecturer_arr, class_arr
    # Generate initial population
    population = [generateStartingTable(len(lecture_arr), len(location_arr), len(time_arr)) for x in range(100)]
    best = []
    x = 0
    if check_convergence:
        converged = False
        converged_count = 0
        while score(population[0]) < min_score and x < num_gens and converged is False:
            new_population = generateNextPopulation(population, len(lecture_arr), len(location_arr), len(time_arr))
            # Check if new generation the same as the previous (convergence)
            if population == new_population:
                converged_count = converged_count + 1
                # If converged but not passing hard requirements, mix up the population
                if converged_count == convergence_count and score(population[0]) < 0:
                    print("oh no "+str(x))
                    new_population = [generateStartingTable(len(lecture_arr), len(location_arr), len(time_arr)) for x in range(100)]
                    x = 0
                elif converged_count == convergence_count:
                    converged == True

            else:
                converged_count = 0
            population = new_population
            best.append(score(population[0]))
            x = x + 1
    else:
        while score(population[0]) < min_score and x < num_gens:
            population = generateNextPopulation(population, 50, 30, 40)
            best.append(score(population[0]))
            # avg.append(getAverageScore(population))
            x = x + 1
            print(best[-1])
    # Print best of final population
    print(population[0])
    print(score(population[0]))
    print(score(population[-1]))
    # plt.plot(avg)
    # plt.show()
    plt.plot(best)
    plt.show()
    return population[0]


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
        total = 100
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
            if time_arr[timetable[lecture_id][1]][0] == "Fri" and time_arr[timetable[lecture_id][1]][1] in ["12pm", "1pm", "2pm", "3pm",
                                                                                        "4pm", "5pm"]:
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


def generateNextPopulation(curr_pop, num_lectures, num_locations, num_times):
    # Score current population
    score_dict = {}
    for x in range(len(curr_pop)):
        table = curr_pop[x]
        score_dict[x] = score(table)
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
        cross_point = random.randint(0, num_lectures - 1)
        new_table = []
        for x in range(num_lectures):
            if x < cross_point:
                new_table.append(first_table[x])
            else:
                new_table.append(second_table[len(first_table) - x - 1])
        # Mutation - change table
        # Method - randomly reassign one value
        lecture = random.randint(0, num_lectures - 1)
        new_table[lecture] = [random.randint(0, num_locations - 1), random.randint(0, num_times - 1)]
        new_pop.append(new_table)
    # Merge new and old populations into final populations
    # Merge old and new tables
    merged_pop = curr_pop + new_pop
    # Sort population based on scores
    sorted_merged_pop = sorted(merged_pop, key=lambda i: score(i), reverse=True)
    # Take best into final
    final_pop = []
    for x in range(len(curr_pop)):
        final_pop.append(sorted_merged_pop[x])
    # print("Best: "+str(score(final_pop[0]))+"\t\tWorst: "+str(score(final_pop[-1])))
    return final_pop


def generateStartingTable(num_lectures, num_locations, num_times):
    timetable = []
    for x in range(0, num_lectures):
        timetable.append([random.randint(0, num_locations - 1), random.randint(0, num_times - 1)])
    return timetable


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


def getAverageScore(population):
    total = 0
    for table in population:
        total = total + score(table)
    total = total / len(population)
    return total


def scoreDetailed(timetable):
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
            # Reduce score by 2 for every 20% of the room that's empty
            percent_empty = (extra_space / room_cap) * 100
            if percent_empty > 20:
                print("location too big for lecture " + lecture_arr[lecture_id].name + " by percent " + str(
                    percent_empty))
            while percent_empty > 20:
                total = total - 2
                percent_empty = percent_empty - 20
            # Lectures should not be held after 12 on a friday
            if time_arr[timetable[lecture_id][1]][0] == "Fri" and time_arr[timetable[lecture_id][1]][1] in ["12pm", "1pm", "2pm", "3pm",
                                                                                        "4pm", "5pm"]:
                print(lecture_arr[lecture_id].name + " takes place friday afternoon")
                total = total - 1
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
                print("Lecturer " + str(lecturer.id) + " has gap of " + str(gap))
                total = total - 1
            if run > 3:
                print("Lecturer " + str(lecturer.id) + " has run of " + str(run))
                total = total - 1

    else:
        print("Hard requirements not passed")
    return total

