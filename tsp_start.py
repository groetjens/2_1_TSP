import matplotlib

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import random
import time
import itertools
import math
from collections import namedtuple

# based on Peter Norvig's IPython Notebook on the TSP

City = namedtuple('City', 'x y')


def distance(A, B):
    return math.hypot(A.x - B.x, A.y - B.y)


def try_all_tours(cities):
    # generate and test all possible tours of the cities and choose the shortest tour
    tours = alltours(cities)
    return min(tours, key=tour_length)


def alltours(cities):
    # return a list of tours (a list of lists), each tour a permutation of cities,
    # and each one starting with the same city
    # note: cities is a set, sets don't support indexing
    start = next(iter(cities))
    return [[start] + list(rest) for rest in itertools.permutations(cities - {start})]


def tour_length(tour):
    # the total of distances between each pair of consecutive cities in the tour
    return sum(distance(tour[i], tour[i - 1]) for i in range(len(tour)))


def make_cities(n, width=1000, height=1000):
    # make a set of n cities, each with random coordinates within a rectangle (width x height).

    random.seed(n)  # the current system time is used as a seed
    # note: if we use the same seed, we get the same set of cities

    return frozenset(City(random.randrange(width), random.randrange(height)) for c in range(n))


def plot_tour(tour):
    # plot the cities as circles and the tour as lines between them
    points = list(tour) + [tour[0]]
    plt.plot([p.x for p in points], [p.y for p in points], 'bo-')  # blue circle markers, solid line style
    plt.axis('scaled')  # equal increments of x and y have the same length
    plt.axis('off')
    plt.show()


def plot_tsp(algorithm, cities):
    # apply a TSP algorithm to cities, print the time it took, and plot the resulting tour.
    t0 = time.process_time()
    tour = algorithm(cities)
    t1 = time.process_time()
    print("{} city tour with length {:.1f} in {:.3f} secs for {}"
          .format(len(tour), tour_length(tour), t1 - t0, algorithm.__name__))
    print("Start plotting ...")
    plot_tour(tour)


def nearest_neighbour(cities):
    cities = set(cities)
    last_city = cities.pop()
    tour = [last_city]
    while len(cities) != 0:
        closest_city = City(x=math.inf, y=math.inf)
        for city in cities:
            if distance(last_city, city) < distance(last_city, closest_city):
                closest_city = city
        tour.append(closest_city)
        last_city = closest_city
        cities.remove(closest_city)
    return tour


def get_intersecting_roads(tour):
    intersecting_roads = []
    tour_copy = tour  # copy.deepcopy(tour)

    # controleer van elke weg
    for i in range(len(tour_copy) - 1):
        # of een andere weg deze doorkruist
        for j in range(len(tour_copy) - 1):
            # wegen zijn van city[i] naar city[i+1] en city[j] naar city[j+1]
            roads = ((tour_copy[i], tour_copy[i + 1]), (tour_copy[j], tour_copy[j + 1]))

            # als alle steden uniek zijn en de wegen niet identiek
            if tour_copy[i + 1] != tour_copy[j] and tour_copy[i] != tour_copy[j + 1] and roads[0] != roads[1]:

                # controleer op intersecties
                if do_intersect(roads):
                    added = False
                    # controleer of de weg al is toegevoegd aan intersecting_roads
                    # en anders voeg deze toe
                    for r in intersecting_roads:
                        if roads[0] == r[1]:
                            added = True
                    if not added:
                        intersecting_roads.append(roads)
    return intersecting_roads


def do_intersect(roads):
    dir1 = dir(roads[0][0], roads[0][1], roads[1][0])
    dir2 = dir(roads[0][0], roads[0][1], roads[1][1])
    dir3 = dir(roads[1][0], roads[1][1], roads[0][0])
    dir4 = dir(roads[1][0], roads[1][1], roads[0][1])

    if dir1 != dir2 and dir3 != dir4:
        return True
    if dir1 == 0 and on_line(roads[0], roads[1][0]):
        return True
    if dir2 == 0 and on_line(roads[0], roads[1][1]):
        return True
    if dir3 == 0 and on_line(roads[1], roads[0][0]):
        return True
    if dir4 == 0 and on_line(roads[1], roads[0][1]):
        return True
    return False


def dir(a, b, c):
    # find direction of line segement
    val = (b.y - a.y) * (c.x - b.x) - (b.x - a.x) * (c.y - b.y)
    if val == 0:
        return 0  # collinear
    elif val < 0:
        return 2  # anti-clockwise
    return 1  # clockwise


def on_line(road, city):
    return city.x <= max(road[0].x, road[1].x) and city.x <= min(road[0].x, road[1].x) and city.y <= max(road[0].y,
                                                                                                         road[
                                                                                                             1].y) and city.y <= min(
        road[0].y, road[1].y)


def two_opt_swap(tour, i, j):
    # new_tour = tour[:i]
    # new_tour.extend(reversed(tour[i:j]))
    # new_tour.extend(tour[j:])
    if j <= i:
        print("Cannot swap with reversed nodes, indexes {}, {}".format(i, j))
        return tour
    new_tour = tour[:i]
    new_tour.extend(reversed(tour[i:j + 1]))
    new_tour.extend(tour[j + 1:])
    return new_tour


def two_opt(cities):
    tour = nearest_neighbour(cities)
    intersecting_roads = get_intersecting_roads(tour)
    # print(tour)
    # print(len(tour))
    # print(intersecting_roads, len(intersecting_roads))
    print("intersections: {}".format(len(intersecting_roads)))
    for roads in intersecting_roads:
        min_index = min(tour.index(roads[0][1]), tour.index(roads[1][0]))
        max_index = max(tour.index(roads[0][1]), tour.index(roads[1][0]))
        print("Solving crossing, len = {}".format(len(tour)))
        # min_index = tour.index(roads[0][1])
        # max_index = tour.index(roads[1][0])
        print("min {}, max {}".format(min_index, max_index))
        tour = two_opt_swap(tour, min_index, max_index)
        print("Post-solve, len = {}".format(len(tour)))
        # print(tour)
        # print(len(tour))
    print(len(tour))
    return tour


def two_opt_e(cities):
    tour = nearest_neighbour(cities)
    # iterate over all sets of edges between cities
    iters = 0
    while (True):
        can_better = False
        for i in range(len(tour) - 1):
            for j in range(len(tour) - i - 2):
                # get the nodes
                roads = ((tour[i], tour[i + 1]), (tour[i + j + 1], tour[i + j + 2]))
                min_index = tour.index(roads[0][1])
                max_index = tour.index(roads[1][0])
                # swap them, and check if it is faster
                old_length = distance(roads[0][0], roads[0][1]) + distance(roads[1][0], roads[1][1])
                new_length = distance(roads[0][0], roads[1][0]) + distance(roads[0][1], roads[1][1])
                if (new_length < old_length):
                    tour = two_opt_swap(tour, min_index, max_index)
                    can_better = True
        if not can_better:
            break
        iters += 1
        if iters >= 5:
            break
    return tour


# give a demo with 10 cities using brute force
cities = make_cities(500)
plot_tsp(nearest_neighbour, cities)
plot_tsp(two_opt_e, cities)
