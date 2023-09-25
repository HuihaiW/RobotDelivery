/********** Sdvrp.cs **********/
using System;
using System.IO;
using localsolver;

public class Sdvrp : IDisposable
{
    // LocalSolver
    LocalSolver localsolver;

    // Number of customers
    int nbCustomers;

    // Capacity of the trucks
    int truckCapacity;

    // Demand of each customer
    long[] demandsData;

    // Distance matrix
    long[][] distMatrixData;

    // Distances between customers and depot
    long[] distDepotData;

    // Number of trucks
    int nbTrucks;

    // Decision variables
    LSExpression[] customersSequences;

    // Are the trucks actually used
    LSExpression[] trucksUsed;

    // Distance traveled by each truck
    LSExpression[] distRoutes;

    // Distance traveled by all the trucks
    LSExpression totalDistance;

    // Quantity carried by each truck
    LSExpression[][] quantity;

    public Sdvrp()
    {
        localsolver = new LocalSolver();
    }

    // Read instance data
    void ReadInstance(string fileName)
    {
        ReadInputSdvrp(fileName);
    }

    public void Dispose()
    {
        if (localsolver != null)
            localsolver.Dispose();
    }

    void Solve(int limit)
    {
        // Declare the optimization model
        LSModel model = localsolver.GetModel();

        trucksUsed = new LSExpression[nbTrucks];
        customersSequences = new LSExpression[nbTrucks];
        distRoutes = new LSExpression[nbTrucks];
        quantity = new LSExpression[nbTrucks][];

        // Sequence of customers visited by each truck
        for (int k = 0; k < nbTrucks; ++k)
            customersSequences[k] = model.List(nbCustomers);

        // Quantity carried by each truck for each customer
        for (int k = 0; k < nbTrucks; ++k)
        {
            quantity[k] = new LSExpression[nbCustomers];
            for (int i = 0; i < nbCustomers; ++i)
                quantity[k][i] = model.Float(0, demandsData[i]);
        }

        // Every customer must be visited by at least one truck
        model.Constraint(model.Cover(customersSequences));

        // Create LocalSolver arrays to be able to access them with "at" operators
        LSExpression distMatrix = model.Array(distMatrixData);
        LSExpression distDepot = model.Array(distDepotData);

        for (int k = 0; k < nbTrucks; ++k)
        {
            LSExpression sequence = customersSequences[k];
            LSExpression c = model.Count(sequence);

            // A truck is used if it visits at least one customer
            trucksUsed[k] = c > 0;

            // The quantity carried in each route must not exceed the truck capacity
            LSExpression quantityArray = model.Array(quantity[k]);
            LSExpression quantityLambda = model.LambdaFunction(j => quantityArray[j]);
            LSExpression routeQuantity = model.Sum(sequence, quantityLambda);
            model.Constraint(routeQuantity <= truckCapacity);

            // Distance traveled by truck k
            LSExpression distLambda = model.LambdaFunction(
                i => distMatrix[sequence[i - 1], sequence[i]]
            );
            distRoutes[k] =
                model.Sum(model.Range(1, c), distLambda)
                + model.If(trucksUsed[k], distDepot[sequence[0]] + distDepot[sequence[c - 1]], 0);
        }

        for (int i = 0; i < nbCustomers; ++i)
        {
            // Each customer must receive at least its demand
            LSExpression quantityServed = model.Sum();
            for (int k = 0; k < nbTrucks; ++k)
                quantityServed.AddOperand(
                    quantity[k][i] * model.Contains(customersSequences[k], i)
                );
            model.Constraint(quantityServed >= demandsData[i]);
        }

        totalDistance = model.Sum(distRoutes);

        // Objective: minimize the distance traveled
        model.Minimize(totalDistance);

        model.Close();

        // Parameterize the solver
        localsolver.GetParam().SetTimeLimit(limit);

        localsolver.Solve();
    }

    /* Write the solution in a file with the following format:
     *  - Each line k contains the customers visited by the truck k */
    void WriteSolution(string fileName)
    {
        using (StreamWriter output = new StreamWriter(fileName))
        {
            output.WriteLine(totalDistance.GetValue());
            for (int k = 0; k < nbTrucks; ++k)
            {
                if (trucksUsed[k].GetValue() != 1)
                    continue;
                // Values in sequence are in 0...nbCustomers. +1 is to put it back in 1...nbCustomers+1
                LSCollection customersCollection = customersSequences[k].GetCollectionValue();
                for (int i = 0; i < customersCollection.Count(); ++i)
                    output.Write((customersCollection[i] + 1) + " ");
                output.WriteLine();
            }
        }
    }

    public static void Main(string[] args)
    {
        if (args.Length < 1)
        {
            Console.WriteLine("Usage: Sdvrp inputFile [solFile] [timeLimit]");
            Environment.Exit(1);
        }
        string instanceFile = args[0];
        string outputFile = args.Length > 1 ? args[1] : null;
        string strTimeLimit = args.Length > 2 ? args[2] : "20";

        using (Sdvrp model = new Sdvrp())
        {
            model.ReadInstance(instanceFile);
            model.Solve(int.Parse(strTimeLimit));
            if (outputFile != null)
                model.WriteSolution(outputFile);
        }
    }

    private static string[] SplitInput(StreamReader input)
    {
        string line = input.ReadLine();
        if (line == null)
            return new string[0];
        return line.Split(new[] { ' ' }, StringSplitOptions.RemoveEmptyEntries);
    }

    private void ReadInputSdvrp(string fileName)
    {
        using (StreamReader input = new StreamReader(fileName))
        {
            string[] splitted;
            splitted = SplitInput(input);

            nbCustomers = int.Parse(splitted[0]);
            nbTrucks = nbCustomers;
            truckCapacity = int.Parse(splitted[1]);

            demandsData = new long[nbCustomers];

            splitted = SplitInput(input);
            for (int n = 0; n < nbCustomers; ++n)
                demandsData[n] = int.Parse(splitted[n]);

            splitted = SplitInput(input);
            int depotX = int.Parse(splitted[0]);
            int depotY = int.Parse(splitted[1]);

            int[] customersX = new int[nbCustomers];
            int[] customersY = new int[nbCustomers];
            for (int n = 0; n < nbCustomers; ++n)
            {
                splitted = SplitInput(input);
                customersX[n] = int.Parse(splitted[0]);
                customersY[n] = int.Parse(splitted[1]);
            }

            ComputeDistanceMatrix(depotX, depotY, customersX, customersY);
        }
    }

    // Compute the distance matrix
    private void ComputeDistanceMatrix(int depotX, int depotY, int[] customersX, int[] customersY)
    {
        distMatrixData = new long[nbCustomers][];
        for (int i = 0; i < nbCustomers; ++i)
            distMatrixData[i] = new long[nbCustomers];

        for (int i = 0; i < nbCustomers; ++i)
        {
            distMatrixData[i][i] = 0;
            for (int j = i + 1; j < nbCustomers; ++j)
            {
                long dist = ComputeDist(customersX[i], customersX[j], customersY[i], customersY[j]);
                distMatrixData[i][j] = dist;
                distMatrixData[j][i] = dist;
            }
        }
        distDepotData = new long[nbCustomers];
        for (int i = 0; i < nbCustomers; ++i)
            distDepotData[i] = ComputeDist(depotX, customersX[i], depotY, customersY[i]);
    }

    private static long ComputeDist(int xi, int xj, int yi, int yj)
    {
        double exactDist = Math.Sqrt(Math.Pow(xi - xj, 2) + Math.Pow(yi - yj, 2));
        return (long)Math.Floor(exactDist + 0.5);
    }
}
