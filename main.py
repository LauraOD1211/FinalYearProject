# Helper functions

# Timetable: stored as dict with lectures as key and time,place as value
# lectures, lecturers and locations will be stored as classes
import math
import random
import time as t

import database
import matplotlib.pyplot as plt
import files
import rewrite


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


def generateTimetable(lectures, locations, times):
    timetable = {}
    for lecture in lectures:
        location = locations[random.randint(0, len(locations) - 1)]
        time = times[random.randint(0, len(times) - 1)]
        timetable[lecture] = [location, time]
    return timetable


def main():
    # Generate 1st gen of timetables
    gen1 = list()
    lectures = database.getLectures()
    locations = database.getLocations()
    times = database.getTimes()
    for i in range(0, 100):
        timetable = generateTimetable(lectures, locations, times)
        gen1.append(timetable)
    # Generate next gen from gen 1
    curr_gen = gen1
    curr_scores = []
    avg = []
    best = []
    for x in range(0, 100000):
        curr_gen, curr_scores = generateNextFittest(curr_gen, curr_scores, lectures, times, locations)
        avg.append(getAverageScore(curr_scores))
        best.append(max(curr_scores))
        if x % 100 == 0:
            print(best[x])
            print(curr_scores[-1])

    # Print results for all gens
    plt.plot(avg)
    plt.show()
    plt.plot(best)
    plt.show()
    # Display lecturer, class and room tables from best (if hard reqs met) to show results
    if curr_scores[0] > 0:
        # displayTimetable(curr_gen[0])
        for lecturer in database.getLecturers():
            files.printLecturerTimetableToCSV(curr_gen[0], lecturer)
        for group in database.getClasses():
            files.printClassTimetableToCSV(curr_gen[0], group)
        for location in locations:
            files.printClassTimetableToCSV(curr_gen[0], location)
    files.printTimetableToCSV(curr_gen[0])
    files.exportTimetable(curr_gen[0], "output/timetable.out")
    scoreTimetableDesc(curr_gen[0])


def generateNextFittest(curr_gen, curr_scores, lectures, times, locations):
    next_gen = []
    ordered_score_index = []
    # Score generation
    scored_gen = []
    if not curr_scores:
        for timetable in curr_gen:
            scored_gen.append(scoreTimetable(timetable))
    else:
        scored_gen = curr_scores

    ordered_score_index = sorted(range(len(scored_gen)), key=lambda i: scored_gen[i], reverse=True)
    # Create new gen of tables
    while len(next_gen) < 1000:
        # Create new gen of tables
        # Take random table out of 5, prioritising higher scoring tables
        first_table = curr_gen[ordered_score_index[min(random.randint(0, len(ordered_score_index) - 1),
                                                       random.randint(0, len(ordered_score_index) - 1),
                                                       random.randint(0, len(ordered_score_index) - 1),
                                                       random.randint(0, len(ordered_score_index) - 1),
                                                       random.randint(0, len(ordered_score_index) - 1))]]
        second_table = curr_gen[ordered_score_index[min(random.randint(0, len(ordered_score_index) - 1),
                                                        random.randint(0, len(ordered_score_index) - 1),
                                                        random.randint(0, len(ordered_score_index) - 1),
                                                        random.randint(0, len(ordered_score_index) - 1),
                                                        random.randint(0, len(ordered_score_index) - 1))]]
        # Crossover - reverse second timetable, combine one with other
        new_tables = [{},{}]
        count = len(lectures) - 1
        cross_point = math.ceil(len(lectures) / 2)
        for lecture in lectures:
            if count > cross_point:
                new_tables[0][lecture] = first_table[lecture]
                new_tables[1][lecture] = second_table[lecture]
            else:
                new_tables[0][lecture] = second_table[lectures[count]]
                new_tables[1][lecture] = first_table[lectures[count]]
            count = count - 1
            # Mutate - find time/location combination that isn't present in timetable, add it at random
            # Mutate 5 times for increased randomness
            for i in range(5):
                location = random.randint(0, len(locations) - 1)
                start_time = random.randint(0, len(times) - 1)
                time = start_time
                mutant = [locations[location], times[time]]
                # if mutant already in table, change time
                while mutant in new_tables[0].values():
                    time = (time + 1) % len(times)
                    if time == start_time:
                        location = (location + 1) % len(locations)
                    mutant = [locations[location], times[time]]
                lecture = lectures[random.randint(0, len(lectures) - 1)]
                new_tables[0][lecture] = mutant
        next_gen.append(new_tables[0])
        next_gen.append(new_tables[1])

    # Score new gen
    scored_next_gen = []
    for timetable in next_gen:
        scored_next_gen.append(scoreTimetable(timetable))
    next_ordered_score_index = sorted(range(len(scored_next_gen)), key=lambda i: scored_next_gen[i], reverse=True)
    # Merge curr_gen and next_gen into one based on scores
    final_gen = []
    final_scores = []
    curr_count = 0
    next_count = 0
    while len(final_gen) < len(curr_gen):
        if scored_gen[ordered_score_index[curr_count]] > scored_next_gen[next_ordered_score_index[next_count]]:
            final_gen.append(curr_gen[ordered_score_index[curr_count]])
            final_scores.append(scored_gen[ordered_score_index[curr_count]])
            curr_count = curr_count + 1
        else:
            final_gen.append(next_gen[next_ordered_score_index[next_count]])
            final_scores.append(scored_next_gen[next_ordered_score_index[next_count]])
            next_count = next_count + 1
    return final_gen, final_scores

def scoreTimetable(timetable):
    score = 0
    lecturer_times = {}
    class_times = {}
    # Hard requirements - Check for all
    for lecture in timetable:
        # Check if two lectures in same room
        if list(timetable.values()).count(timetable[lecture]) > 1:
            score = score - 50
        # Check if lecturer busy at same time
        for lecturer in lecture.lecturers:
            if lecturer in lecturer_times:
                if timetable[lecture][1] in lecturer_times[lecturer]:
                    score = score - 50
                else:
                    lecturer_times[lecturer].add(timetable[lecture][1])
            else:
                if lecturer.unavailable_times is not None:
                    lecturer_times[lecturer] = set(lecturer.unavailable_times)
                    if timetable[lecture][1] in lecturer.unavailable_times:
                        score = score - 50
                else:
                    lecturer_times[lecturer] = set({})
                lecturer_times[lecturer].add(timetable[lecture][1])

        # Check if class group busy at same time
        for group in lecture.class_groups:
            if group in class_times:
                if timetable[lecture][1] in class_times[group]:
                    score = score - 50
                else:
                    class_times[group].add(timetable[lecture][1])
            else:
                class_times[group] = {timetable[lecture][1]}

        # Check if room free at that time
        if timetable[lecture][0].unavailable_times == timetable[lecture][1]:
            score = score - 50
        # Check if capacity is enough
        if lecture.no_students > timetable[lecture][0].capacity:
            score = score - 50
        # Check if room type is right
        if lecture.room_reqs is not None:
            if lecture.room_reqs != timetable[lecture][0].room_type:
                score = score - 50
    # Soft Requirements - Only check if hard requirements all pass
    if score == 0:
        score = 10000
        # If possible, the lecture should take place in a relevant building
        for lecture in timetable:
            if lecture.discipline == timetable[lecture][0].discipline:
                score = score + 100
                # A lecture should not take place in a room that’s too big
                score = score + 50 - (timetable[lecture][0].capacity - lecture.no_students)
        # Students should not have too many lectures in a row or huge gaps between lectures
        for group in class_times:
            times = class_times[group]
            score = score + 50 - (getBiggestRun(times) * 10)
            score = score + 50 - (getBiggestGap(times) * 10)
        # Lecturers should not have too many lectures in a row or huge gaps between lectures
        for lecturer in lecturer_times:
            times = lecturer_times[lecturer]
            score = score + 50 - (getBiggestRun(times) * 10)
            score = score + 50 - (getBiggestGap(times) * 10)
    return score


def tempscoreTimetable(timetable):
    score = 0
    lecturer_times = {}
    class_times = {}
    # Hard requirements - Check for all
    for lecture in timetable:
        # Check if two lectures in same room
        if list(timetable.values()).count(timetable[lecture]) > 1:
            return -10000
        # Check if lecturer busy at same time
        for lecturer in lecture.lecturers:
            if lecturer in lecturer_times:
                if timetable[lecture][1] in lecturer_times[lecturer]:
                    return -9000
                else:
                    lecturer_times[lecturer].add(timetable[lecture][1])
            else:
                if lecturer.unavailable_times is not None:
                    lecturer_times[lecturer] = set(lecturer.unavailable_times)
                    if timetable[lecture][1] in lecturer.unavailable_times:
                        return -8000
                else:
                    lecturer_times[lecturer] = set({})
                lecturer_times[lecturer].add(timetable[lecture][1])

        # Check if class group busy at same time
        for group in lecture.class_groups:
            if group in class_times:
                if timetable[lecture][1] in class_times[group]:
                    return -7000
                else:
                    class_times[group].add(timetable[lecture][1])
            else:
                class_times[group] = {timetable[lecture][1]}

        # Check if room free at that time
        if timetable[lecture][0].unavailable_times == timetable[lecture][1]:
            return -6000
        # Check if capacity is enough
        if lecture.no_students > timetable[lecture][0].capacity:
            return -5000
        # Check if room type is right
        if lecture.room_reqs is not None:
            if lecture.room_reqs != timetable[lecture][0].room_type:
                print(lecture.room_reqs)
                print(timetable[lecture][0].room_type)
                return -4000
    # Soft Requirements - Only check if hard requirements all pass
    if score == 0:
        score = 10000
        # If possible, the lecture should take place in a relevant building
        for lecture in timetable:
            if lecture.discipline == timetable[lecture][0].discipline:
                score = score + 100
                # A lecture should not take place in a room that’s too big
                score = score + 50 - (timetable[lecture][0].capacity - lecture.no_students)
        # Students should not have too many lectures in a row or huge gaps between lectures
        for group in class_times:
            times = class_times[group]
            score = score + 50 - (getBiggestRun(times) * 10)
            score = score + 50 - (getBiggestGap(times) * 10)
        # Lecturers should not have too many lectures in a row or huge gaps between lectures
        for lecturer in lecturer_times:
            times = lecturer_times[lecturer]
            score = score + 50 - (getBiggestRun(times) * 10)
            score = score + 50 - (getBiggestGap(times) * 10)
    return score


def scoreTimetableDesc(timetable):
    score = 0
    lecturer_times = {}
    class_times = {}
    # Hard requirements - Check for all
    for lecture in timetable:
        # Check if two lectures in same room
        if list(timetable.values()).count(timetable[lecture]) > 1:
            print(timetable[lecture] + " has multiple lectures")
            score = score - 50
        # Check if lecturer busy at same time
        for lecturer in lecture.lecturers:
            if lecturer in lecturer_times:
                if timetable[lecture][1] in lecturer_times[lecturer]:
                    print(lecturer.name + " is busy at " + timetable[lecture][1])
                    score = score - 50
                else:
                    lecturer_times[lecturer].add(timetable[lecture][1])
            else:
                if lecturer.unavailable_times is not None:
                    lecturer_times[lecturer] = set(lecturer.unavailable_times)
                    if timetable[lecture][1] in lecturer.unavailable_times:
                        print(lecturer.name + " is busy at " + timetable[lecture][1])
                        score = score - 50
                else:
                    lecturer_times[lecturer] = set({})
                lecturer_times[lecturer].add(timetable[lecture][1])

        # Check if class group busy at same time
        for group in lecture.class_groups:
            if group in class_times:
                if timetable[lecture][1] in class_times[group]:
                    print(group + " is busy at " + timetable[lecture][1])
                    score = score - 500
                else:
                    class_times[group].add(timetable[lecture][1])
            else:
                class_times[group] = {timetable[lecture][1]}

        # Check if room free at that time
        if timetable[lecture][0].unavailable_times == timetable[lecture][1]:
            print(timetable[lecture][0].name + " is unavailable at " + timetable[lecture][1])
            score = score - 50
        # Check if capacity is enough
        if lecture.no_students > timetable[lecture][0].capacity:
            print(timetable[lecture][0].name + " is not big enough for " + lecture.name)
            score = score - 50
        # Check if room type is right
        if lecture.room_reqs is not None:
            if lecture.room_reqs != timetable[lecture][0].room_type:
                print(timetable[lecture][0].name + " is not right type for " + lecture.name)
                score = score - 50


def getAverageScore(scores):
    total = 0
    for score in scores:
        total = total + score
    return total / len(scores)


def getBiggestRun(times):
    curr_run = 0
    best = 0
    for x in range(1, 6):
        for y in range(1, 9):
            time = "Day " + str(x) + " Time " + str(y)
            if time in times:
                curr_run = curr_run + 1
            else:
                if curr_run > best:
                    best = curr_run
                curr_run = 0
        if curr_run > best:
            best = curr_run
        curr_run = 0
    return best


def getBiggestGap(times):
    curr_gap = 0
    best = 0
    for x in range(1, 6):
        for y in range(1, 9):
            time = "Day " + str(x) + " Time " + str(y)
            if time in times:
                curr_gap = curr_gap + 1
            else:
                if curr_gap > best:
                    best = curr_gap
                curr_gap = 0
    return best


if __name__ == '__main__':
    rewrite.main()
