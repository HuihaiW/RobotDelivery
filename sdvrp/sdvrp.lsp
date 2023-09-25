use io;

/* Read instance data */
function input() {
    usage = "Usage: localsolver sdvrp.lsp " + 
            "inFileName=inputFile [solFileName=outputFile] [lsTimeLimit=timeLimit]";
    
    if (inFileName == nil) throw usage;
    readInputSdvrp();
    
    // Compute distance matrix
    computeDistanceMatrix();
}

/* Declare the optimization model */
function model () {
    // Sequence of customers visited by each truck
    customersSequences[k in 0...nbTrucks] <- list(nbCustomers);
    
    // All customers must be visited at least by one truck
    constraint cover[k in 0...nbTrucks](customersSequences[k]);

    // Quantity carried by each truck for each customer
    quantity[k in 0...nbTrucks][i in 0...nbCustomers] <- float(0, demands[i]);

    for [k in 0...nbTrucks] {
        local sequence <- customersSequences[k];
        local c <- count(sequence);
    
        // The quantity needed in each route must not exceed the truck capacity
        routeQuantity[k] <- sum(sequence, j => quantity[k][j]);
        constraint routeQuantity[k] <= truckCapacity;

        // A truck is used if it visits at least one customer
        trucksUsed[k] <- c > 0;

        // Distance traveled by truck k
        routeDistances[k] <- sum(1...c,
                i => distanceMatrix[sequence[i-1]][sequence[i]]) + (trucksUsed[k] ?
                (distanceDepot[sequence[0]] + distanceDepot[sequence[c-1]]) :
                0);
    }

    for [i in 0...nbCustomers] {
        // Each customer must receive at least its demand
        quantityServed[i] <- sum[k in 0...nbTrucks](quantity[k][i]
                * contains(customersSequences[k], i));
        constraint quantityServed[i] >= demands[i];
    }

    totalDistance <- sum[k in 0...nbTrucks](routeDistances[k]);

    // Objective: minimize the distance traveled
    minimize totalDistance;
}

/* Write the solution in a file with the following format:
    * - Each line k contains the customers visited by the truck k */
function output () {
    if (solFileName == nil) return;
    local outfile = io.openWrite(solFileName);

    outfile.println(totalDistance.value);
    for [customer in 0...nbCustomers] {
        outfile.print(customer + 1, ": ");
        for [k in 0...nbTrucks] {
            if (trucksUsed[k].value != 1) continue;
            if ((customersSequences[k].value).contains(customer))
                outfile.print(k + 1, " ");
        }
        outfile.println();
    }
}

/* Parametrize the solver */
function param () {
    if (lsTimeLimit == nil) lsTimeLimit = 20;
}

function readInputSdvrp() {
    local inFile = io.openRead(inFileName);
    nbCustomers = inFile.readInt();
    truckCapacity = inFile.readInt();
    nbTrucks = nbCustomers;
    
    // Extracting the demand of each customer
    demands[i in 0...nbCustomers] = inFile.readInt(); 
    
    // Extracting the coordinates of the depot and the customers
    for [i in 0...nbCustomers + 1] {
        nodesX[i] = inFile.readDouble();
        nodesY[i] = inFile.readDouble();
    }
}

function computeDistanceMatrix() {
    // Computing the distance between customers
    for [i in 0...nbCustomers] {
        distanceMatrix[i][i] = 0;
        for [j in i+1...nbCustomers] {
            // +1 because computeDist expected original data indices,
            // with customers in 1...nbCustomers+1
            local localDistance = computeDist(i+1, j+1);
            distanceMatrix[j][i] = localDistance;
            distanceMatrix[i][j] = localDistance;
        }
    }
    // Computing the distance between depot and customers
    for [i in 0...nbCustomers] {
        local localDistance = computeDist(0, i+1);
        distanceDepot[i] = localDistance;
    }
}

function computeDist(i, j) {
    local exactDist = sqrt(pow((nodesX[i] - nodesX[j]), 2) + pow((nodesY[i] - nodesY[j]), 2));
    return floor(exactDist + 0.5);
}
