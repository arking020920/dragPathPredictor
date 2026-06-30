__author__ = 'frank'

from ..CalculoTrayectoria import vel_interp, locate_drog
import numpy as np

def Track(grid, j, x, y, V, timevec, t, dt):
    jnew = j
    u, v = vel_interp.InterpolaVel(grid, x, y, j, V, timevec, t)
    uk1 = dt * u
    vk1 = dt * v
    xinter = x + .5 * uk1
    yinter = y + .5 * vk1
    jinter = locate_drog.LocateDrog(grid, xinter, yinter, j)

    if(np.where(jinter != 1)[0]).size > 0:
        xnew = xinter
        ynew = yinter
    else:
        uinter, vinter = vel_interp.InterpolaVel(grid, x, y, j, V, timevec, t)
        uk2 = dt * uinter
        vk2 = dt * vinter
        xnew = xinter + uk2
        ynew = yinter + vk2

    jnew = locate_drog.LocateDrog(grid, xnew, ynew, j)
    inan = np.where(jnew == -1)[0]
    return xnew, ynew, jnew

