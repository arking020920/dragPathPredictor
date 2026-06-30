__author__ = 'root'

from . import vel_interp, locate_drog
import numpy as np

def Track(grid, j, x, y, time_model, time_model_next, t, dt, D):
    u,v = vel_interp.InterpolaVel(grid, x, y, j, time_model, time_model_next, t)

    uk1 = dt * u
    vk1 = dt * v
    xinter = x + .5 * uk1
    yinter = y + .5 * vk1
    jinter = locate_drog.LocateDrog(grid, xinter, yinter, j)


    #verificar cdo sea mas de una particula!!!
    jgood = 1 if jinter.size == 1 else np.where(jinter != 1)[0]

    uinter, vinter = vel_interp.InterpolaVel(grid, xinter, yinter, jinter, time_model, time_model_next, t + .5 * dt / 3600)
    uk2 = dt * uinter
    vk2 = dt * vinter
    xnew = xinter + uk2
    ynew = yinter + vk2
    if D > -1:
        D = D / np.sqrt(t + .5 * dt / 3600)
        #continuar cdo D sea mayor que -1
    if x.size > 1:
        #xavg = np.mean(xnew[:-1])
        #yavg = np.mean(ynew[:-1])
        xnew[-1] = np.mean(xnew[:-1])
        ynew[-1] = np.mean(ynew[:-1])
    #    continuar cdo x.size sea mator que 1
    jnew = locate_drog.LocateDrog(grid, xnew, ynew, j)
    inan = np.where(jnew == -1)[0]
    #if inan.size > 0:
    #    implementar la funcion para cdo las particulas se salen del dominio
    #print "END Track"
    return np.array(xnew), np.array(ynew), jnew



