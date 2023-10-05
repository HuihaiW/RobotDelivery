import localsolver

def SDVRP(truck_capacity, demands, C_C_Matrix, B_C_Matrix, Customer_IDs, str_time_limit, number_trucks):
    demands_data = demands
    nb_customers = C_C_Matrix.shape[0]
    truck_capacity = truck_capacity
    dist_matrix_data = C_C_Matrix.tolist()
    dist_depot_data = B_C_Matrix.tolist()
    nb_trucks = number_trucks

    with localsolver.LocalSolver() as ls:
        model = ls.model
        customers_sequences = [model.list(nb_customers) for _ in range(nb_trucks)]
        
        quantity = [None] * nb_trucks
        for k in range(nb_trucks):
            quantity[k] = [model.int(1, demands_data[i]) for i in range(nb_customers)]
    #     print(quantity[0][0].value)
            
        model.constraint(model.cover(customers_sequences))
        
        dist_matrix = model.array(dist_matrix_data)
        dist_depot = model.array(dist_depot_data)
        
        route_distances = [None] * nb_trucks
        trucks_used = [None] * nb_trucks
        
        for k in range(nb_trucks):
            sequence = customers_sequences[k]
            c = model.count(sequence)
            
            trucks_used[k] = model.count(sequence) > 0
            
            quantity_array = model.array(quantity[k])
            quantity_lambda = model.lambda_function(lambda j: quantity_array[j])
            route_quantity = model.sum(sequence, quantity_lambda)
            model.constraint(route_quantity <= truck_capacity)
            
            dist_lambda = model.lambda_function(lambda i: model.at(dist_matrix, sequence[i - 1], sequence[i]))
            route_distances[k] = model.sum(model.range(1, c), dist_lambda) + model.iif(
                        trucks_used[k],
                        dist_depot[sequence[0]] + dist_depot[sequence[c - 1]], 0)
            
        for i in range(nb_customers):
            # Each customer must receive at least its demand
            quantity_served = model.sum(quantity[k][i] * model.contains(customers_sequences[k], i)
                for k in range(nb_trucks))
        
            model.constraint(quantity_served >= demands_data[i])
                
        total_distance = model.sum(route_distances)
        
        model.minimize(total_distance)
    #     model.close()
        model.close()

        ls.param.time_limit = int(str_time_limit)
        ls.solve()
        
        r_total_distance = total_distance.value
        customer_list = []
        quantity_list = []
        for k in range(nb_trucks):
            c_list = []
            c_list1 = []
            q_list = []
    #         print(trucks_used[k].value)
            if trucks_used[k].value != 1:
                customer_list.append([])
                quantity_list.append([])
                continue

            for customer in customers_sequences[k].value:
                c_list.append(customer)
                c_list1.append(Customer_IDs[customer])

            for c in c_list:
                q_list.append(quantity[k][c].value)
    #             if q.value > 0:
    #                 q_list.append(q.value)
    #             for i in range(len(quantity[k])):
    #                 if q[i].value != 0:
    #                     q_l.append(q[i].value)
    #             q_list.append(q_l)
            customer_list.append(c_list1)
            quantity_list.append(q_list)
    return customer_list, quantity_list, r_total_distance