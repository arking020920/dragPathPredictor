__author__ = 'root'
import numpy as np
#implementacion de la funcion de matlab belint
def BelInt(grid):

    #e = grid.ele.astype(int)
    #x = grid.gridx
    #y = grid.gridy

    e = grid.trap_finder._triangulation.triangles.astype(int)
    x = grid.trap_finder._triangulation.x
    y = grid.trap_finder._triangulation.y
    #etemp = e - 1

    #print e[:,1], e[:,2]

    temp12 = y[e[:,1]] - y[e[:,2]]
    temp20 = y[e[:,2]] - y[e[:,0]]
    temp01 = y[e[:,0]] - y[e[:,1]]
    sz = temp12.shape[0]
    temp12 = np.reshape(temp12, (sz,1))
    temp20 = np.reshape(temp20, (sz,1))
    temp01 = np.reshape(temp01, (sz,1))
    dy = np.concatenate((temp12, temp20, temp01),axis=1)

    ar = (x[e[:,0]] * dy[:,0] + x[e[:,1]] * dy[:,1] + x[e[:,2]] * dy[:,2]) / 2.

    n1 = e[:,0]
    n2 = e[:,1]
    n3 = e[:,2]
    shp = (n1.shape[0], 3)
    A = np.zeros(shp)
    B = np.zeros(shp)
    AO = np.zeros((n1.shape[0], 2))
    T = np.zeros(shp)

    A[:,0] = x[n3] - x[n2]
    A[:,1] = x[n1] - x[n3]
    A[:,2] = x[n2] - x[n1]

    B[:,0] = y[n2] - y[n3]
    B[:,1] = y[n3] - y[n1]
    B[:,2] = y[n1] - y[n2]

    AO[:,0] = .5 * (x[n2] * y[n3] - x[n3] * y[n2])
    AO[:,1] = .5 * (x[n3] * y[n1] - x[n1] * y[n3])

    T[:,0] = AO[:,0] * 2
    T[:,1] = AO[:,1] * 2
    T[:,2] = 2 * ar - T[:,0] - T[:,1]

    grid.A = A
    grid.B = B
    grid.AO = AO
    grid.T = T

    print("END BelInt")
    return grid