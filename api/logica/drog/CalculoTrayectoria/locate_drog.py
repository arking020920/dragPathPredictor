__author__ = 'root'
import numpy as np


def LocateDrog(grid, xor, yor, j):
    #j = np.array(j) if j.size == 1 else j
    jnew = j

    #belel function start(grid, j, [x, y])##############################################################################
    tol = np.finfo(float).eps * 10 ** 7

    #basis2d function start(grid, xylist, j)#######################################################
    xp, yp = (xor, yor)
    #print j.size
    inan = np.where(j != -1) if j.size != 1 else np.where(j != -1)[0][0]

    phi = np.empty((j.size, 3))
    phi[:] = np.nan

    #n3 = trisurface.triangles[]
    n3 = (grid.trap_finder._triangulation.triangles[j, :] if j.size == 1 else grid.trap_finder._triangulation.triangles[j[inan]])
    x = grid.trap_finder._triangulation.x[n3.astype(int)]
    #x1, x2, x3 = (x[0], x[1], x[2])
    x1 = x[0] if len(x.shape) == 1 else x[:,0]
    x2 = x[1] if len(x.shape) == 1 else x[:,1]
    x3 = x[2] if len(x.shape) == 1 else x[:,2]
    y = grid.trap_finder._triangulation.y[n3.astype(int)]
    y1 = y[0] if len(y.shape) == 1 else y[:,0]
    y2 = y[1] if len(y.shape) == 1 else y[:,1]
    y3 = y[2] if len(y.shape) == 1 else y[:,2]

    area = (grid.ar[j] if j.size == 1 else grid.ar[j[inan]]) - 1
    xptemp = xp if xp.size == 1 else xp[inan]
    yptemp = yp if yp.size == 1 else yp[inan]

    #Basis function1
    a = (x2 * y3 - x3 * y2) / (2.0 * area)
    b = (y2 - y3) / (2.0 * area)
    c = -(x2 - x3) / (2.0 * area)
    phi[inan, 0] = a + b * xptemp + c * yptemp

    #Basis function2
    a = (x3 * y1 - x1 * y3) / (2.0 * area)
    b = (y3 - y1) / (2.0 * area)
    c = -(x3 - x1) / (2.0 * area)
    phi[inan, 1] = a + b * xptemp + c * yptemp

    #Basis function3
    a = (x1 * y2 - x2 * y1) / (2.0 * area)
    b = (y1 - y2) / (2.0 * area)
    c = -(x1 - x2) / (2.0 * area)
    phi[inan, 2] = a + b * xptemp + c * yptemp
    #basis2d function end###############################################################

    #continue belel function########################################################################################
    #phima = phi >= -tol
    #phime = phi <= 1 + tol
    #print (phi >= -tol) and (phi <= 1 + tol)
    test = (np.int_(np.equal(phi >= -tol, phi <= 1 + tol)))
    test = test == 1
    idx = np.int_(test.all(axis=1))
    inotfound = np.where(idx == 0)[0]
    if inotfound.size > 0:
        #jnew[inotfound] = tri.FindTriangleByXy(xor[inotfound],yor[inotfound], grid)[0]

        xor = xor if type(xor) not in [np.ma.core.MaskedArray, np.ndarray] else xor[inotfound]
        yor = yor if type(yor) not in [np.ma.core.MaskedArray, np.ndarray] else yor[inotfound]
        if jnew.size > 1:
            jnew[inotfound] = grid.trap_finder.__call__(xor, yor)
        else:
            jnew = grid.trap_finder.__call__(xor, yor)

    #belel function end################################################################################################
    return jnew
    #print "END LocateDrog"
