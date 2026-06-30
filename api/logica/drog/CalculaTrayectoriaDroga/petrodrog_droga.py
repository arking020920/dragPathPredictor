__author__ = 'root'

from ..CalculoTrayectoria import belint
from ..CalculoTrayectoria import find_triangle as tri
import numpy as np
import track_droga
from ..CalculoTrayectoria import ExpandClass as expand
from ..CalculoTrayectoria import descomponer

def PetroDrog(grid, t1, t2, dt, xi, yi, V, time_init):
    timemin = V[0].time
    timemax = V[1].time
    timevec = np.array([timemin, timemax])

    if grid.A is None or grid.B is None or grid.AO is None or grid.T is None:
    #implementacion de la funcion de matlab belint
        grid = belint.BelInt(grid)

    j = grid.trap_finder.__call__(xi, yi)
    sh = (xi.size, len(range(t1, t2 + 1, dt))) if xi.size > 1 else len(range(t1, t2 + 1, dt))

    xx = np.empty(sh)
    yy = np.empty(sh)
    dtsecs = dt
    time = time_init

    print "print Intervalo desde: %s  hasta %s" % (str(time), str(t2))
    jlast = np.array([])
    time_lost = np.zeros(xi.shape)
    iterator = 0
    while time < t2:
        xnow = xx[:, iterator]
        ynow = yy[:, iterator]
        xnew, ynew = xnow, ynow
        igood = np.where(j != -1)[0][0] if j.size == 1 else np.where(j != 1)[0]

        if igood.size == 0:
            print 'Todas las drogas fueron eliminadas!!!'
            print 'Terminando intervalo desde' + "Intervalo desde: " + str(time) + " hasta " + str(t2)
            return
        if j.size == 1:
            #asignar variables en una sola linea
            jgood, xgood, ygood = (j, xnow, ynow)
        else:
            jgood, xgood, ygood = (j[igood], xnow[igood], ynow[igood])

        xnext, ynext, jnext = track_droga.Track(grid, jgood, xgood, ygood, V, timevec, time, dtsecs)
        if j.size == 1:
            #j, xnew, ynew = (jnext, xnext, ynext)
            j, xnew, ynew = (jnext, xnext, ynext)
        else:
            j[igood] = jnext
            xnew[igood] = xnext
            ynew[igood] = ynext

#        arreglar time_lost para almacenar el tiempo en que se pierden las particulas
#       codigo de matlab
#        if ~isempty(jlast)
#            time_lost(find(~isnan(jlast)&isnan(j))) = time;
#        end
        jlast = j
        time += dt
        iterator += 1
        xx[:, iterator] = xnew
        yy[:, iterator] = ynew

    print 'Terminando intervalo ' + str(V[0].time) + ' hasta ' + str(t2)
    return xx, yy, j, time_lost
