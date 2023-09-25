#include "localsolver.h"
#include <cmath>
#include <cstring>
#include <fstream>
#include <iostream>
#include <vector>

using namespace localsolver;
using namespace std;

class Sdvrp {
public:
    // LocalSolver
    LocalSolver localsolver;

    // Number of customers
    int nbCustomers;

    // Capacity of the trucks
    int truckCapacity;

    // Demand of each customer
    vector<int> demandsData;

    // Distance matrix
    vector<vector<int>> distMatrixData;

    // Distance between customers and depot
    vector<int> distDepotData;

    // Number of trucks
    int nbTrucks;

    // Decision variables
    vector<LSExpression> customersSequences;

    // Are the trucks actually used
    vector<LSExpression> trucksUsed;

    // Distance traveled by all the trucks
    LSExpression totalDistance;

    // Quantity carried by each truck
    vector<vector<LSExpression>> quantity;

    /* Read instance data */
    void readInstance(const string& fileName) {
        readInputSdvrp(fileName);
        nbTrucks = nbCustomers;
    }

    void solve(int limit) {
        // Declare the optimization model
        LSModel model = localsolver.getModel();

        // Sequence of customers visited by each truck
        customersSequences.resize(nbCustomers);
        for (int k = 0; k < nbTrucks; ++k) {
            customersSequences[k] = model.listVar(nbCustomers);
        }

        // Quantity carried by each truck for each customer
        quantity.resize(nbTrucks);
        for (int k = 0; k < nbTrucks; ++k) {
            quantity[k].resize(nbTrucks);
            for (int i = 0; i < nbCustomers; ++i) {
                quantity[k][i] = model.floatVar(0, demandsData[i]);
            }
        }

        // All customers must be visited by exactly one truck
        model.constraint(model.cover(customersSequences.begin(), customersSequences.end()));

        // Create LocalSolver arrays to be able to access them with "at" operators
        LSExpression distMatrix = model.array();
        for (int n = 0; n < nbCustomers; ++n) {
            distMatrix.addOperand(model.array(distMatrixData[n].begin(), distMatrixData[n].end()));
        }
        LSExpression distDepot = model.array(distDepotData.begin(), distDepotData.end());

        trucksUsed.resize(nbTrucks);
        vector<LSExpression> distRoutes(nbTrucks);

        for (int k = 0; k < nbTrucks; ++k) {
            LSExpression sequence = customersSequences[k];
            LSExpression c = model.count(sequence);

            // A truck is used if it visits at least one customer
            trucksUsed[k] = c > 0;

            // The quantity carried in each route must not exceed the truck capacity
            LSExpression quantityArray = model.array(quantity[k].begin(), quantity[k].end());
            LSExpression quantityLambda = model.createLambdaFunction(
                    [&](LSExpression j) { return quantityArray[j]; });
            LSExpression routeQuantity = model.sum(sequence, quantityLambda);
            model.constraint(routeQuantity <= truckCapacity);

            // Distance traveled by truck k
            LSExpression distLambda = model.createLambdaFunction([&](LSExpression i) {
                return model.at(distMatrix, model.at(sequence, model.sub(i, 1)), model.at(sequence, i));
            });
            distRoutes[k] = model.sum(model.sum(model.range(1, c), distLambda),
                                      model.iif(trucksUsed[k],
                                                model.sum(model.at(distDepot, model.at(sequence, 0)),
                                                          model.at(distDepot, model.at(sequence, c - 1))),
                                                0));
        }

        for (int i = 0; i < nbCustomers; ++i) {
            // Each customer must receive at least its demand
            LSExpression quantityServed = model.sum();
            for (int k = 0; k < nbTrucks; ++k)
                quantityServed.addOperand(quantity[k][i] * model.contains(customersSequences[k], i));
            model.constraint(quantityServed >= demandsData[i]);
        }

        totalDistance = model.sum(distRoutes.begin(), distRoutes.end());

        // Objective: minimize the distance traveled
        model.minimize(totalDistance);

        model.close();

        // Parameterize the solver
        localsolver.getParam().setTimeLimit(limit);

        localsolver.solve();
    }

    /* Write the solution in a file with the following format:
     *  - Each line k contains the customers visited by the truck k */
    void writeSolution(const string& fileName) {
        ofstream outfile;
        outfile.exceptions(ofstream::failbit | ofstream::badbit);
        outfile.open(fileName.c_str());

        outfile << totalDistance.getValue() << endl;
        for (int k = 0; k < nbTrucks; ++k) {
            if (trucksUsed[k].getValue() != 1)
                continue;
            // Values in sequence are in 0...nbCustomers. +1 is to put it back in 1...nbCustomers+1
            LSCollection customersCollection = customersSequences[k].getCollectionValue();
            for (int i = 0; i < customersCollection.count(); ++i) {
                outfile << customersCollection[i] + 1 << " ";
            }
            outfile << endl;
        }
    }

private:
    void readInputSdvrp(const string& fileName) {
        ifstream infile(fileName.c_str());
        if (!infile.is_open()) {
            throw std::runtime_error("File cannot be opened.");
        }

        string str;
        char* line;
        istringstream iss;
        getline(infile, str);
        line = strdup(str.c_str());
        iss.str(line);
        iss >> nbCustomers;
        iss >> truckCapacity;
        nbTrucks = nbCustomers;
        getline(infile, str);
        line = strdup(str.c_str());
        istringstream stream(line);
        demandsData.resize(nbCustomers);
        int demand;
        for (int n = 0; n < nbCustomers; ++n) {
            stream >> demand;
            demandsData[n] = demand;
        }
        vector<int> customersX(nbCustomers);
        vector<int> customersY(nbCustomers);
        int depotX, depotY;
        getline(infile, str);
        line = strdup(str.c_str());
        istringstream iss_1(line);
        iss_1 >> depotX;
        iss_1 >> depotY;
        for (int i = 0; i < nbCustomers; ++i) {
            getline(infile, str);
            line = strdup(str.c_str());
            istringstream iss(line);
            iss >> customersX[i];
            iss >> customersY[i];
        }

        computeDistanceMatrix(depotX, depotY, customersX, customersY);

        infile.close();
    }

    // Compute the distance matrix
    void computeDistanceMatrix(int depotX, int depotY, const vector<int>& customersX, const vector<int>& customersY) {
        distMatrixData.resize(nbCustomers);
        for (int i = 0; i < nbCustomers; ++i) {
            distMatrixData[i].resize(nbCustomers);
        }
        for (int i = 0; i < nbCustomers; ++i) {
            distMatrixData[i][i] = 0;
            for (int j = i + 1; j < nbCustomers; ++j) {
                int distance = computeDist(customersX[i], customersX[j], customersY[i], customersY[j]);
                distMatrixData[i][j] = distance;
                distMatrixData[j][i] = distance;
            }
        }

        distDepotData.resize(nbCustomers);
        for (int i = 0; i < nbCustomers; ++i) {
            distDepotData[i] = computeDist(depotX, customersX[i], depotY, customersY[i]);
        }
    }

    static int computeDist(int xi, int xj, int yi, int yj) {
        double exactDist = sqrt(pow((double)xi - xj, 2) + pow((double)yi - yj, 2));
        return floor(exactDist + 0.5);
    }
};

int main(int argc, char** argv) {
    if (argc < 2) {
        cerr << "Usage: Sdvrp inputFile [outputFile] [timeLimit]" << endl;
        return 1;
    }

    const char* instanceFile = argv[1];
    const char* solFile = argc > 2 ? argv[2] : NULL;
    const char* strTimeLimit = argc > 3 ? argv[3] : "20";

    try {
        Sdvrp model;
        model.readInstance(instanceFile);
        model.solve(atoi(strTimeLimit));
        if (solFile != NULL)
            model.writeSolution(solFile);
        return 0;
    } catch (const exception& e) {
        cerr << "An error occurred: " << e.what() << endl;
        return 1;
    }
}
