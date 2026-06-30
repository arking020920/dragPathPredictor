__author__ = 'frank'
import numpy as np
import os
from Generic import paths

def ElAreas(ele, x, y):
    ele = ele.astype(int)
    temp12 = y[ele[:,1]] - y[ele[:,2]]
    temp20 = y[ele[:,2]] - y[ele[:,0]]
    temp01 = y[ele[:,0]] - y[ele[:,1]]
    sz = temp12.shape[0]
    #dy = np.concatenate((y[ele[:,1]] - y[ele[:,2]], y[ele[:,2]] - y[ele[:,0]], y[ele[:,0] - y[ele[:,1]]]),axis=1)
    temp12 = np.reshape(temp12, (sz,1))
    temp20 = np.reshape(temp20, (sz,1))
    temp01 = np.reshape(temp01, (sz,1))
    dy = np.concatenate((temp12, temp20, temp01),axis=1)
    del temp12, temp20, temp01
    ar = (x[ele[:,0]] * dy[:,0] + x[ele[:,1]] * dy[:,1] + x[ele[:,2]] * dy[:,2]) / 2
    print("END ElAreas")
    return ar



def LoadGrid(zone, nodes):
    #cargar las variables necesarias a partir de los ficheros de la carpeta de la zona(*.bat, *.ele, *.nod)
    #load grid de matlab bastante resumido
    from . import GridClass as gc
    import matplotlib.tri as tri

    ele = (np.loadtxt(os.path.join(paths.geo_dir(), zone, zone + '.ele')))[:, 1:4] - 1
    x = nodes[:, 1]
    y = nodes[:, 2]
    z = (np.loadtxt(os.path.join(paths.geo_dir(), zone, zone + '.bat')))[:, 1]
    mytri = tri.Triangulation(x, y, ele)
    trap_finder = tri.TrapezoidMapTriFinder(mytri)
    ar = ElAreas(ele, x, y)
    grid = gc.Grid(trap_finder, z, ar, A=None, B=None, AO=None, T=None)
    print("END LoadGrid")
    return grid