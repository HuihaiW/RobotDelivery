import java.util.*;
import java.io.*;
import localsolver.*;

public class Sdvrp {
    // LocalSolver
    private final LocalSolver localsolver;

    // Number of customers
    int nbCustomers;

    // Capacity of the trucks
    private int truckCapacity;

    // Demand of each customer
    private long[] demandsData;

    // Distance matrix
    private long[][] distMatrixData;

    // Distances between customers and depot
    private long[] distDepotData;

    // Number of trucks
    private int nbTrucks;

    // Decision variables
    private LSExpression[] customersSequences;

    // Are the trucks actually used
    private LSExpression[] trucksUsed;

    // Quantity carried by each truck
    private LSExpression[][] quantity;

    // Distance traveled by each truck
    LSExpression[] distRoutes;

    // Distance traveled by all the trucks
    private LSExpression totalDistance;

    private Sdvrp(LocalSolver localsolver) {
        this.localsolver = localsolver;
    }

    private void solve(int limit) {
        // Declare the optimization model
        LSModel model = localsolver.getModel();

        trucksUsed = new LSExpression[nbTrucks];
        customersSequences = new LSExpression[nbTrucks];
        distRoutes = new LSExpression[nbTrucks];
        quantity = new LSExpression[nbTrucks][nbCustomers];

        // Sequence of customers visited by each truck
        for (int k = 0; k < nbTrucks; ++k)
            customersSequences[k] = model.listVar(nbCustomers);

        // Quantity carried by each truck for each customer
        for (int k = 0; k < nbTrucks; ++k)
            for (int i = 0; i < nbCustomers; ++i)
                quantity[k][i] = model.floatVar(0, demandsData[i]);

        // Every customer must be visited by at least one truck
        model.constraint(model.cover(customersSequences));

        // Create LocalSolver arrays to be able to access them with "at" operators
        LSExpression distMatrix = model.array(distMatrixData);
        LSExpression distDepot = model.array(distDepotData);

        for (int k = 0; k < nbTrucks; ++k) {
            LSExpression sequence = customersSequences[k];
            LSExpression c = model.count(sequence);

            // A truck is used if it visits at least one customer
            trucksUsed[k] = model.gt(c, 0);

            // The quantity carried in each route must not exceed the truck capacity
            LSExpression quantityArray = model.array(quantity[k]);
            LSExpression quantityLambda = model.lambdaFunction(j -> model.at(quantityArray, j));
            LSExpression routeQuantity = model.sum(sequence, quantityLambda);
            model.constraint(model.leq(routeQuantity, truckCapacity));

            // Distance traveled by truck k
            LSExpression distLambda = model
                .lambdaFunction(i -> model.at(distMatrix, model.at(sequence, model.sub(i, 1)), model.at(sequence, i)));
            distRoutes[k] = model.sum(model.sum(model.range(1, c), distLambda),
                model.iif(trucksUsed[k], model.sum(model.at(distDepot, model.at(sequence, 0)),
                    model.at(distDepot, model.at(sequence, model.sub(c, 1)))), 0));
        }

        for (int i = 0; i < nbCustomers; ++i) {
            // Each customer must receive at least its demand
            LSExpression quantityServed = model.sum();
            for (int k = 0; k < nbTrucks; ++k)
                quantityServed.addOperand(model.prod(quantity[k][i], model.contains(customersSequences[k], i)));
            model.constraint(model.geq(quantityServed, demandsData[i]));
        }

        totalDistance = model.sum(distRoutes);

        // Objective: minimize the distance traveled
        model.minimize(totalDistance);

        model.close();

        // Parameterize the solver
        localsolver.getParam().setTimeLimit(limit);

        localsolver.solve();
    }

    private void readInstance(String fileName) throws IOException {
        try (Scanner input = new Scanner(new File(fileName))) {
            nbCustomers = input.nextInt();
            truckCapacity = input.nextInt();
            nbTrucks = nbCustomers;
            input.nextLine();
            demandsData = new long[nbCustomers];
            for (int n = 1; n <= nbCustomers; ++n) {
                demandsData[n - 1] = input.nextInt();
            }

            input.nextLine();

            int[] customersX = new int[nbCustomers];
            int[] customersY = new int[nbCustomers];
            int depotX = input.nextInt();
            int depotY = input.nextInt();
            input.nextLine();
            for (int n = 1; n <= nbCustomers; ++n) {
                customersX[n - 1] = input.nextInt();
                customersY[n - 1] = input.nextInt();
                input.nextLine();
            }

            computeDistanceMatrix(depotX, depotY, customersX, customersY);
        }
    }

    // Compute the distance matrix
    private void computeDistanceMatrix(int depotX, int depotY, int[] customersX, int[] customersY) {
        distMatrixData = new long[nbCustomers][nbCustomers];
        for (int i = 0; i < nbCustomers; ++i) {
            distMatrixData[i][i] = 0;
            for (int j = i + 1; j < nbCustomers; ++j) {
                long dist = computeDist(customersX[i], customersX[j], customersY[i], customersY[j]);
                distMatrixData[i][j] = dist;
                distMatrixData[j][i] = dist;
            }
        }

        distDepotData = new long[nbCustomers];
        for (int i = 0; i < nbCustomers; ++i) {
            distDepotData[i] = computeDist(depotX, customersX[i], depotY, customersY[i]);
        }
    }

    private static long computeDist(int xi, int xj, int yi, int yj) {
        double exactDist = Math.sqrt(Math.pow(xi - xj, 2) + Math.pow(yi - yj, 2));
        return (long) Math.floor(exactDist + 0.5);
    }

    public static void main(String[] args) {
        if (args.length < 1) {
            System.err.println("Usage: java Sdvrp inputFile [outputFile] [timeLimit]");
            System.exit(1);
        }

        try (LocalSolver localsolver = new LocalSolver()) {
            String instanceFile = args[0];
            String outputFile = args.length > 1 ? args[1] : null;
            String strTimeLimit = args.length > 2 ? args[2] : "20";

            Sdvrp model = new Sdvrp(localsolver);
            model.readInstance(instanceFile);
            model.solve(Integer.parseInt(strTimeLimit));
            if (outputFile != null) {
                model.writeSolution(outputFile);
            }
        } catch (Exception ex) {
            System.err.println(ex);
            ex.printStackTrace();
            System.exit(1);
        }
    }

    /* Write the solution in a file with the following format:
     * - Each line k contains the customers visited by the truck k */
    private void writeSolution(String fileName) throws IOException {
        try (PrintWriter output = new PrintWriter(fileName)) {
            output.println(totalDistance.getValue());
            for (int k = 0; k < nbTrucks; ++k) {
                if (trucksUsed[k].getValue() != 1)
                    continue;
                // Values in sequence are in 0...nbCustomers. +1 is to put it back in 1...nbCustomers+1
                LSCollection customersCollection = customersSequences[k].getCollectionValue();
                for (int i = 0; i < customersCollection.count(); ++i)
                    output.print((customersCollection.get(i) + 1) + " ");
                output.println();
            }
        }
    }
}
