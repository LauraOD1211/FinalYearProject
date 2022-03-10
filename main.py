# Helper functions

# Timetable: stored as dict with lectures as key and time,place as value
# lectures, lecturers and locations will be stored as classes
import math
import random
import database


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


def getTimes():
    times = []
    for x in range(1, 6):
        for y in range(1, 9):
            time = "Day " + str(x) + " Time " + str(y)
            times.append(time)
    return times


def main():
    # Generate 1st gen of timetables
    gen1 = list()
    lectures = database.getLectures()
    locations = database.getLocations()
    times = getTimes()
    print(lectures)
    print(locations)
    print(times)
    for i in range(0, 100):
        timetable = generateTimetable(lectures, locations, times)
        gen1.append(timetable)
    # Generate next gen from gen 1
    curr_gen = gen1
    for x in range(0, 10000):
        print(x)
        curr_gen = generateNextFittest(curr_gen, lectures, times, locations)
    print(curr_gen[0])
    print(scoreTimetable(curr_gen[0]))
    print(displayTimetable(curr_gen[0]))


def displayTimetable(timetable):
    time_dict = {}
    for entry in timetable:
        if timetable[entry][1] in time_dict:
            time_dict[timetable[entry][1]].add((entry.name, timetable[entry][0].name))
        else:
            time_dict[timetable[entry][1]] = set({(entry.name, timetable[entry][0].name)})
    for time in getTimes():
        print(time)
        if time in time_dict:
            print(time_dict[time])


def generateNextFittest(curr_gen, lectures, times, locations):
    next_gen = []
    ordered_score_index = []
    # Score generation
    scored_gen = []
    for timetable in curr_gen:
        scored_gen.append(scoreTimetable(timetable))
    # Create new gen of tables
    while len(next_gen) < len(curr_gen):
        # Take random 2, prioritising higher scoring tables
        ordered_score_index = sorted(range(len(scored_gen)), key=lambda i: scored_gen[i], reverse=True)
        # Generate new tables from chosen two
        first_table = curr_gen[ordered_score_index[min(random.randint(0, len(ordered_score_index) - 1),
                                                       random.randint(0, len(ordered_score_index) - 1))]]
        second_table = curr_gen[ordered_score_index[min(random.randint(0, len(ordered_score_index) - 1),
                                                        random.randint(0, len(ordered_score_index) - 1))]]
        # Crossover - reverse each timetable, combine first half of each with back half of other
        new_tables = [{}, {}]
        count = len(lectures) - 1
        cross_point = math.ceil(len(lectures) / 2)
        for lecture in lectures:
            if count > cross_point:
                new_tables[0][lecture] = first_table[lecture]
                new_tables[1][lecture] = second_table[lectures[count]]
            else:
                new_tables[0][lecture] = second_table[lectures[count]]
                new_tables[1][lecture] = first_table[lecture]
            count = count - 1
        # Mutate - randomly reassign one value in each
        for table in new_tables:
            lecture = lectures[random.randint(0, len(lectures) - 1)]
            location = locations[random.randint(0, len(locations) - 1)]
            time = times[random.randint(0, len(times) - 1)]
            table[lecture] = [location, time]
        # Mutate 2 - move time to next/previous timeslot or move room to next/previous room
        #for table in new_tables:
        #    lecture = lectures[random.randint(0, len(lectures) - 1)]
        #    location = locations.index(table[lecture][0])
        #    time = times.index(table[lecture][1])
        #    if random.randint(0,1) == 0:
        #        time = (time + random.randint(-1,1)) % len(times)
        #    else:
        #        location = (location + random.randint(-1,1))  % len(locations)
        #    table[lecture] = [locations[location], times[time]]
        # Add to new gen
        next_gen.extend(new_tables)

    # Score new gen
    scored_next_gen = []
    for timetable in next_gen:
        scored_next_gen.append(scoreTimetable(timetable))
    next_ordered_score_index = sorted(range(len(scored_gen)), key=lambda i: scored_gen[i], reverse=True)

    # Merge curr_gen and next_gen into one based on scores
    final_gen = []
    curr_count = 0
    next_count = 0
    while len(final_gen) < len(curr_gen):
        if scored_gen[ordered_score_index[curr_count]] > scored_next_gen[next_ordered_score_index[next_count]]:
            final_gen.append(curr_gen[ordered_score_index[curr_count]])
            curr_count = curr_count + 1
        else:
            final_gen.append(next_gen[next_ordered_score_index[next_count]])
            next_count = next_count + 1
    return final_gen


def scoreTimetable(timetable):
    score = 1000
    lecturer_times = {}
    class_times = {}
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
                    lecturer_times[lecturer] = lecturer_times[lecturer].add(timetable[lecture][1])
            else:
                if timetable[lecture][1] in lecturer.unavailable_times:
                    score = score - 50
                lecturer_times[lecturer] = set(lecturer.unavailable_times)
                lecturer_times[lecturer] = lecturer_times[lecturer].add(timetable[lecture][1])
        # Check if class group busy at same time
        for group in lecture.class_groups:
            if group in class_times:
                if timetable[lecture][1] in class_times[group]:
                    score = score - 50
                else:
                    class_times[group].add(timetable[lecture][1])
            else:
                class_times[group] = set({timetable[lecture][1]})

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

    return score


main()
