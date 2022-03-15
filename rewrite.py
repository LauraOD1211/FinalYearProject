import random
#import setup_new
import database_new

global lecture_arr, location_arr, time_arr, lecturer_arr, class_arr

lecture_arr = database_new.getLectures()
location_arr = database_new.getLocations()
time_arr = database_new.getTimes()
lecturer_arr = database_new.getLecturers()
class_arr = database_new.getClasses()

def main():
    # Generate initial population
    population = [generateStartingTable(50,30,40) for x in range(100)]
    # Use this to generate new population
    for x in range(5000):
        population = generateNextPopulation(population, 50, 30, 40)
        if x % 1000 == 0:
            print(x)
    # Print best of final population
    print(population[0])
    print(score(population[0]))
    print(score(population[-1]))
    return


def score(timetable):
    total = 0
    # Hard requirements
    # Check if two lectures on in same time and place
    for x in range(len(timetable)):
        lecture = lecture_arr[x]
        if timetable.count(timetable[x])>1:
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
        total = 10000
        # If possible, the lecture should take place in a relevant building
        for lecture_id in range(len(lecture_arr)):
            if lecture_arr[lecture_id].discipline == location_arr[timetable[lecture_id][0]].discipline:
                total = total + 100
                # A lecture should not take place in a room that’s too big
                total = total + 50 - (location_arr[timetable[lecture_id][0]].capacity - lecture_arr[lecture_id].no_students)
        # Students should not have too many lectures in a row or huge gaps between lectures
        for class_group in class_arr:
            lectures = class_group.lectures
            lecture_times = [timetable[lecture][1] for lecture in lectures]
            gap, run = getGapRun(lecture_times)
            if gap > 3:
                total = total - 50
            if run > 3:
                total = total - 50
        # Lecturers should not have too many lectures in a row or huge gaps between lectures
        for lecturer in lecturer_arr:
            lectures = lecturer.lectures
            lecture_times = [timetable[lecture][1] for lecture in lectures]
            gap, run = getGapRun(lecture_times)
            if gap > 3:
                total = total - 50
            if run > 3:
                total = total - 50
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
        first_table_index = random.randint(0,len(curr_pop)-1)
        for x in range(5):
            index = random.randint(0,len(curr_pop)-1)
            if score_dict[index] > score_dict[first_table_index]:
                first_table_index = index
        second_table_index = random.randint(0, len(curr_pop)-1)
        for x in range(5):
            index = random.randint(0, len(curr_pop)-1)
            if score_dict[index] > score_dict[second_table_index]:
                second_table_index = index
        first_table = curr_pop[first_table_index]
        second_table = curr_pop[second_table_index]
        # Cross-over - combine tables
        # Method - pick random cross-point, reverse second table, combine start of one with end of other
        cross_point = random.randint(0, num_lectures-1)
        new_table = []
        for x in range(num_lectures):
            if x < cross_point:
                new_table.append(first_table[x])
            else:
                new_table.append(second_table[len(first_table)-x-1])
        # Mutation - change table
        # Method - randomly reassign one value
        lecture = random.randint(0, num_lectures-1)
        new_table[lecture] = [random.randint(0, num_locations-1), random.randint(0, num_times-1)]
        new_pop.append(new_table)
    for x in range(len(curr_pop)):
        table = curr_pop[x]
    # Merge new and old populations into final populations
    # Merge old and new tables
    merged_pop = curr_pop + new_pop
    # Sort population based on scores
    sorted_merged_pop = sorted(merged_pop, key=lambda i: score(i), reverse=True)
    # Tke best into final
    final_pop = []
    for x in range(len(curr_pop)):
        final_pop.append(sorted_merged_pop[x])
    #print("Best: "+str(score(final_pop[0]))+"\t\tWorst: "+str(score(final_pop[-1])))
    return final_pop


def generateStartingTable(num_lectures, num_locations, num_times):
    timetable = []
    for x in range(0,num_lectures):
        timetable.append([random.randint(0,num_locations-1),random.randint(0, num_times-1)])
    return timetable


def scoreDesc(timetable):
    total = 0
    # Hard requirements
    # Check if two lectures on in same time and place
    for x in range(len(timetable)):
        lecture = lecture_arr[x]
        if timetable.count(timetable[x])>1:
            print("Lecture clash - "+str(x)+" - "+str(timetable[x]))
            total = total - 1
        # Check if room big enough
        location = location_arr[timetable[x][0]]
        if lecture.no_students > location.capacity:
            print("Room too small - "+str(x)+" - "+str(timetable[x]))
            total = total - 1
    # Check if lecturer not free
    for lecturer in lecturer_arr:
        lectures = lecturer.lectures
        lecture_times = [timetable[lecture][1] for lecture in lectures]
        for time in lecture_times:
            if lecture_times.count(time) > 1:
                total = total - 1
                print("Lecturer busy - "+str(x)+" - "+str(timetable[x]))
    # Check if class not free
    for class_group in class_arr:
        lectures = class_group.lectures
        lecture_times = [timetable[lecture][1] for lecture in lectures]
        for time in lecture_times:
            if lecture_times.count(time) > 1:
                total = total - 1
                print("Class busy - "+str(x)+" - "+str(timetable[x]))
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
                    if curr_gap > best_gap:
                        best_gap = curr_gap
                    curr_gap = 0
                    curr_run = 1
                elif x not in day and is_gap:
                    curr_gap = curr_gap + 1
                elif x not in day and not is_gap:
                    if curr_run > best_run:
                        best_run = curr_run
                    curr_run = 0
                    curr_gap = 1
                else:
                    print("thats not good")
    return longest_gap, longest_run