__author__ = 'root'
from Generic import GenericFunctions as gen
import numpy as np
from . import locate_drog
#t: tiempo actual
#dt: delta_t del escenario


def rk1(grid, elem_idx, x, y, t, dt, list_time_model):
    u, v = gen.GetUvByXy(grid.trap_finder, t, x, y, list_time_model)
    xnp1, ynp1 = (x + dt * u, y + dt * v)
    return xnp1, ynp1

def rk4(grid, elem_idx, x, y, t, dt, list_time_model):
    u1, v1 = gen.GetUvByXy(grid.trap_finder, t, x, y, list_time_model)

    ku1 = dt * u1
    kv1 = dt * v1
    u2, v2 = gen.GetUvByXy(grid.trap_finder, t+1/2. * dt/3600, x + 1/2.*ku1, y + 1/2. * kv1, list_time_model)
    ku2 = dt * u2
    kv2 = dt * v2
    u3, v3 = gen.GetUvByXy(grid.trap_finder, t+1/2. * dt/3600, x + 1/2.*ku2, y + 1/2. * kv2, list_time_model)
    ku3 = dt * u3
    kv3 = dt * v3
    u4, v4 = gen.GetUvByXy(grid.trap_finder, t + dt/3600, x + ku3, y + kv3, list_time_model)
    ku4 = dt * u4
    kv4 = dt * v4

    xf = x + 1/6. * (ku1 + 2. * ku2 + 2. * ku3 + ku4)
    yf = y + 1/6. * (kv1 + 2. * kv2 + 2. * kv3 + kv4)
    return xf, yf

def trackRks(grid, j, x, y, t, D, escenary, dt=None):
    jnew = j
    dt = escenary.delta_t if dt is None else dt
    #xnew, ynew = rk1(grid, j, x, y, t, dt, escenary.list_time_model)
    xnew, ynew = rk4(grid, j, x, y, t, 3600, escenary.list_time_model)

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
    return np.nan_to_num(np.array(xnew)), np.nan_to_num(np.array(ynew)), jnew

def trackRks1(grid, j, x, y, t, D, escenary, dt=None):
    jnew = j
    dt = escenary.delta_t if dt is None else dt
    xnew, ynew = rk1(grid, j, x, y, t, dt, escenary.list_time_model)
#    xnew, ynew = rk4(grid, j, x, y, t, 3600, escenary.list_time_model)

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
    return np.nan_to_num(np.array(xnew)), np.nan_to_num(np.array(ynew)), jnew



