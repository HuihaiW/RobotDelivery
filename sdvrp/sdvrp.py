import localsolver
import sys
import math


def read_elem(filename):
    with open(filename) as f:
        return [str(elem) for elem in f.read().split()]


def main(instance_file, str_time_limit, sol_file):
    #
    # Read instance data
    #
    nb_customers, truck_capacity, dist_matrix_data, dist_depot_data, demands_data = \
        read_input_sdvrp(instance_file)
    nb_trucks = nb_customers

    with localsolver.LocalSolver() as ls:
        #
        # Declare the optimization model
        #
        model = ls.model

        # Sequence of customers visited by each truck
        customers_sequences = [model.list(nb_customers) for _ in range(nb_trucks)]

        # Quantity carried by each truck for each customer
        quantity = [None] * nb_trucks
        for k in range(nb_trucks):
            quantity[k] = [model.float(0, demands_data[i]) for i in range(nb_customers)]

        # All customers must be visited at least by one truck
        model.constraint(model.cover(customers_sequences))

        # Create LocalSolver arrays to be able to access them with "at" operators
        dist_matrix = model.array(dist_matrix_data)
        dist_depot = model.array(dist_depot_data)

        route_distances = [None] * nb_trucks
        trucks_used = [None] * nb_trucks

        for k in range(nb_trucks):
            sequence = customers_sequences[k]
            c = model.count(sequence)

            # A truck is used if it visits at least one customer
            trucks_used[k] = model.count(sequence) > 0

            # The quantity carried in each route must not exceed the truck capacity
            quantity_array = model.array(quantity[k])
            quantity_lambda = model.lambda_function(lambda j: quantity_array[j])
            route_quantity = model.sum(sequence, quantity_lambda)
            model.constraint(route_quantity <= truck_capacity)

            # Distance traveled by each truck
            dist_lambda = model.lambda_function(
                lambda i: model.at(dist_matrix, sequence[i - 1], sequence[i]))
            route_distances[k] = model.sum(model.range(1, c), dist_lambda) \
                + model.iif(
                    trucks_used[k],
                    dist_depot[sequence[0]] + dist_depot[sequence[c - 1]],
                    0)

        for i in range(nb_customers):
            # Each customer must receive at least its demand
            quantity_served = model.sum(
                quantity[k][i] * model.contains(customers_sequences[k], i)
                for k in range(nb_trucks))
            model.constraint(quantity_served >= demands_data[i])

        total_distance = model.sum(route_distances)

        # Objective: minimize the distance traveled
        model.minimize(total_distance)

        model.close()

        # Parameterize the solver
        ls.param.time_limit = int(str_time_limit)

        ls.solve()

        #
        # Write the solution in a file with the following format:
        # each line k contain the customers visited by the truck k
        #
        if len(sys.argv) >= 3:
            with open(sol_file, 'w') as f:
                f.write("%d \n" % total_distance.value)
                for k in range(nb_trucks):
                    if trucks_used[k].value != 1:
                        continue
                    # Values in sequence are in 0...nbCustomers. +1 is to put it back in 1...nbCustomers+1
                    for customer in customers_sequences[k].value:
                        f.write("%d " % (customer + 1))
                    f.write("\n")


def read_input_sdvrp(filename):
    file_it = iter(read_elem(filename))

    nb_customers = int(next(file_it))
    capacity = int(next(file_it))

    demands = [None] * nb_customers
    for i in range(nb_customers):
        demands[i] = int(next(file_it))

    # Extracting the coordinates of the depot and the customers
    customers_x = [None] * nb_customers
    customers_y = [None] * nb_customers
    depot_x = float(next(file_it))
    depot_y = float(next(file_it))
    for i in range(nb_customers):
        customers_x[i] = float(next(file_it))
        customers_y[i] = float(next(file_it))

    distance_matrix = compute_distance_matrix(customers_x, customers_y)
    distance_depots = compute_distance_depots(depot_x, depot_y, customers_x, customers_y)
    return nb_customers, capacity, distance_matrix, distance_depots, demands


# Compute the distance between two customers
def compute_distance_matrix(customers_x, customers_y):
    nb_customers = len(customers_x)
    distance_matrix = [[None for _ in range(nb_customers)] for _ in range(nb_customers)]
    for i in range(nb_customers):
        distance_matrix[i][i] = 0
        for j in range(nb_customers):
            dist = compute_dist(customers_x[i], customers_x[j], customers_y[i], customers_y[j])
            distance_matrix[i][j] = dist
            distance_matrix[j][i] = dist
    return distance_matrix


# Compute the distances to depot
def compute_distance_depots(depot_x, depot_y, customers_x, customers_y):
    nb_customers = len(customers_x)
    distance_depots = [None] * nb_customers
    for i in range(nb_customers):
        dist = compute_dist(depot_x, customers_x[i], depot_y, customers_y[i])
        distance_depots[i] = dist
    return distance_depots


def compute_dist(xi, xj, yi, yj):
    exact_dist = math.sqrt(math.pow(xi - xj, 2) + math.pow(yi - yj, 2))
    return int(math.floor(exact_dist + 0.5))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python sdvrp.py input_file [output_file] [time_limit]")
        sys.exit(1)

    instance_file = sys.argv[1]
    sol_file = sys.argv[2] if len(sys.argv) > 2 else None
    str_time_limit = sys.argv[3] if len(sys.argv) > 3 else "20"

    main(instance_file, str_time_limit, sol_file)
