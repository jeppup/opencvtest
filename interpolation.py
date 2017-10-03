import numpy as np
import matplotlib.pyplot as plt
import math


def interpolate(data, desired_points):
    data_points = len(data)
    interpolated = np.empty(desired_points)
    interpolated_x = range(0, desired_points)
    y_data = np.random.rand(data_points)
    x_data = range(0,data_points)



    solution_m = np.matrix([[0,0,0,1],
                            [1,1,1,1],
                            [0,0,1,0],
                            [3,2,1,0]])
    inv_solution_m= np.linalg.inv(solution_m)

    interpolation_intermediate_points = desired_points / data_points

    for i in range(len(y_data)-2):
        t_1 = y_data[i] - y_data[i+1]
        t_2 = y_data[i+1] - y_data[i+2]
        rhs = np.array([[y_data[i]], [y_data[i+1]], [t_1], [t_2]])
        coefficients = inv_solution_m * rhs

        u = np.arange(0, 1, 1/float(interpolation_intermediate_points))
        u_idx = 0
        print(coefficients)
        for j in range(i*interpolation_intermediate_points, i*interpolation_intermediate_points + interpolation_intermediate_points):
            interpolated[j] = coefficients[0]*math.pow(u[u_idx],3) + coefficients[1]*math.pow(u[u_idx],2) + coefficients[2]*u[u_idx] + coefficients[3]
            u_idx += 1

    x_data = range(0, desired_points, interpolation_intermediate_points)
    plt.plot(x_data, y_data, color = "red", marker='x', linestyle='-')
    plt.plot(interpolated_x, interpolated, color = "green", linestyle='-')
    plt.show()
