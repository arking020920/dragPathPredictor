__author__ = 'root'

import numpy as np
import petromar.CalculoTrayectoria.PDVclass as pdvc
import petrodrog_droga as ptdd
import petromar.CalculoTrayectoria.out_data_class as out_class
import os

def CalculaTrayectoria(uv, points, grid, dift, dt, input_data):
    xi = points[:, 0]
    yi = points[:, 1]
    trackx = np.array(xi)
    tracky = np.array(yi)

    init1 = points.shape[0]
    init1 += 1
    time_init = input_data.hora_inicio
    t1 = time_init
    t2 = t1 + dift
    ly = uv.shape[1]
    init_ind = int(time_init / dift)
    t1 = init_ind * dift
    t2 = (init_ind + 1) * dift
    init_ind = init_ind * 2 + 1
    u1 = uv[:, init_ind]
    v1 = uv[:, init_ind + 1]
    time_lost = np.zeros([1, init1 - 1])
    out_list = []
    for i in xrange(init_ind + 2, ly - 1, 2):
        u2 = uv[:, i]
        v2 = uv[:, i + 1]
        list_v = [pdvc.PetroDrogVClass(u1, v1, t1), pdvc.PetroDrogVClass(u2, v2, t2)]
        xx, yy, j, time_j = ptdd.PetroDrog(grid, t1, t2, dt, xi, yi, list_v, time_init)
        try:
            time_lost[np.where(time_j != 0)[0]] = time_j[np.where(time_j != 0)[0]]
        except Exception:
            time_lost = np.zeros((init1, 1))

        trackx = np.concatenate((trackx, np.ravel(xx[:,1:], order='F'))) if trackx.size > 1 else np.ravel(xx, order='F')
        tracky = np.concatenate((tracky, np.ravel(yy[:,1:], order='F'))) if tracky.size > 1 else np.ravel(yy, order='F')

        jnan = np.where(j != -1)[0]
        if jnan.size == 0:
            break
        else:
            time_init, t1, t2, u1, v1 = (t2, t2, t2 + dift, u2, v2)
        szt = trackx.size
        xi = trackx[szt - 802:szt]
        yi = tracky[szt - 802:szt]
        for k in xrange(1, xx[:, 1:].shape[1] + 1):
            plot_data = out_class.OutDataClass(t1, t2, np.column_stack((xx[:, k], yy[:, k])), np.column_stack((u1, v1)))
            out_list.append(plot_data)
            del plot_data
    del j, jnan, list_v, u1, u2, v1, v2, uv, xx, yy

    ind = np.where(time_lost > 0)[0]
    min_t = np.min(time_lost[ind]) if ind.size > 0 else 0
    max_t = np.max(time_lost[ind]) if ind.size > 0 else 0
    prom_t = np.average(time_lost[ind]) if ind.size > 0 else 0
    moda_t = 0

    txt2 = np.array([[xi.size, input_data.hora_inicio], [min_t, max_t], [prom_t, moda_t]])




    print "End"
