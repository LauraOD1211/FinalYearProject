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
    no_gens = []
    best_scores = []
    for x in range(50):
        best_table, runs = runGA(check_convergence=True, num_gens=20000, min_score=1000)
        best_tables.append(best_table)
        files.printTimetableToCSV(best_table, "bestrun" + str(x))
        best_scores.append(score(best_tables[x]))
        no_gens.append(runs)
    print(best_scores)
    print(no_gens)
    plt.plot(best_scores)
    plt.title("Best scoring table after each run")
    plt.xlabel("Run")
    plt.ylabel("Score")
    plt.show()
    plt.plot(no_gens)
    plt.title("Number of gens before completion")
    plt.xlabel("Run")
    plt.ylabel("Number of gens")
    plt.show()
    # update.main(timetable=best_tables[0])


def runGA(num_gens=20000, min_score=200, check_convergence=True, convergence_count=300):
    global lecture_arr, location_arr, time_arr, lecturer_arr, class_arr
    # Generate initial population
    population = [generateStartingTable() for _ in range(100)]
    best = []
    avg = []
    x = 0
    total_runs = 0
    if check_convergence:
        converged = False
        converged_count = 0
        while score(population[0]) < min_score and x < num_gens and converged is False:
            new_population = generateNextPopulation(population)
            # Check if new generation the same as the previous (convergence)
            if population == new_population:
                converged_count = converged_count + 1
                # If converged but not passing hard requirements, mix up the population
                if converged_count == convergence_count and score(population[0]) < 0:
                    print("oh no " + str(x))
                    new_population = [generateStartingTable() for _ in
                                      range(100)]
                    x = 0
                elif converged_count == convergence_count:
                    converged = True

            else:
                converged_count = 0
            population = new_population
            best.append(score(population[0]))
            avg.append(getAverageScore(population))
            x = x + 1
            total_runs = total_runs + 1
            print(str(x) + " - " + str(best[-1]) + " - " + str(avg[-1]))
        print("done")
    else:
        while score(population[0]) < min_score and x < num_gens:
            population = generateNextPopulation(population)
            best.append(score(population[0]))
            avg.append(getAverageScore(population))
            x = x + 1
            print(best[-1])
    # Print best of final population
    print(population[0])
    print(score(population[0]))
    print(score(population[-1]))
    plt.plot(avg)
    plt.title("Average fitness score")
    plt.xlabel("Generation")
    plt.ylabel("Score")
    plt.show()
    plt.plot(best)
    plt.title("Best fitness score")
    plt.xlabel("Generation")
    plt.ylabel("Score")
    plt.show()
    return population[0], total_runs


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
            # A lecture should not take place in a room that???s too big
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


def generateNextPopulation(curr_pop):
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
        cross_point = random.randint(0, len(lecture_arr) - 1)
        new_table = []
        for x in range(len(lecture_arr)):
            if x < cross_point:
                new_table.append(first_table[x])
            else:
                new_table.append(second_table[len(first_table) - x - 1])
        # Mutation - change table
        # Method - randomly reassign one value
        lecture = random.randint(0, len(lecture_arr) - 1)
        new_entry = [random.randint(0, len(location_arr) - 1), random.randint(0, len(time_arr) - 1)]
        while new_entry in new_table:
            new_entry = [random.randint(0, len(location_arr) - 1), random.randint(0, len(time_arr) - 1)]
        new_table[lecture] = new_entry
        new_pop.append(new_table)

    # Merge new and old populations into final populations
    # Merge old and new tables
    merged_pop = curr_pop + new_pop
    sorted_merged_pop = sorted(merged_pop, key=lambda i: score(i), reverse=True)

    # Take best into final
    final_pop = []
    for x in range(len(curr_pop)):
        final_pop.append(sorted_merged_pop[x])
    # print("Best: "+str(score(final_pop[0]))+"\t\tWorst: "+str(score(final_pop[-1])))
    return final_pop


def generateStartingTable():
    timetable = []
    for x in range(len(lecture_arr)):
        timetable.append([random.randint(0, len(location_arr) - 1), random.randint(0, len(time_arr) - 1)])
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
                if hours[index] in day:
                    if is_gap:
                        is_gap = False
                        if curr_gap > longest_gap:
                            longest_gap = curr_gap
                        curr_gap = 0
                        curr_run = 1
                    else:
                        curr_run = curr_run + 1
                else:
                    if is_gap:
                        curr_gap = curr_gap + 1
                    else:
                        is_gap = True
                        if curr_run > longest_run:
                            longest_run = curr_run
                        curr_run = 0
                        curr_gap = 1
                index = index + 1
            if longest_gap < curr_gap:
                longest_gap = curr_gap
            if longest_run < curr_run:
                longest_run = curr_run
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
        total = 200
        # If possible, the lecture should take place in a relevant building
        for lecture_id in range(len(lecture_arr)):
            if lecture_arr[lecture_id].discipline == location_arr[timetable[lecture_id][0]].discipline:
                total = total + 1
            # A lecture should not take place in a room that???s too big
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
            if time_arr[timetable[lecture_id][1]][0] == "Fri" and time_arr[timetable[lecture_id][1]][1] in ["12pm",
                                                                                                            "1pm",
                                                                                                            "2pm",
                                                                                                            "3pm",
                                                                                                            "4pm",
                                                                                                            "5pm"]:
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


main()
#update.demo()
