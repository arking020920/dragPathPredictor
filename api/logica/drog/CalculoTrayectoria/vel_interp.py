__author__ = 'root'
import matplotlib.tri as tri


def InterpolaVel(grid, x, y, j, time_model, time_model_next, t):
    #it1 = np.where(t <= timevec)[0][0]
    #it2 = np.where(t >= timevec)[0][0]
    #if it1 == it2:
    #calculo provisional de tfac1 e tfac2, arreglar despues
    #it1, it2 = 1, 0

    tfac1 = float(time_model_next.t_hour - t) / float(time_model_next.t_hour - time_model.t_hour)
    tfac2 = 1 - tfac1



    u1, u2, v1, v2 = time_model_next.xyuv[:, 3], time_model.xyuv[:, 3], time_model_next.xyuv[:, 4], time_model.xyuv[:, 4]

    trap_finder = grid.trap_finder

    if j.size > 150:
        #interpolacion en tiempo
        uu = tfac1 * u2 + tfac2 * u1
        vv = tfac1 * v2 + tfac2 * v1
        #interpolacion en el espacio
        #usando como prueba el metodo de interpolacion de matplotlib "LinearTriInterpolator" el cual
        #da el mismo resultado de
        #matlab, que seria interp_scalar

        interp_u = tri.LinearTriInterpolator(trap_finder._triangulation, uu, trifinder=trap_finder)
        interp_v = tri.LinearTriInterpolator(trap_finder._triangulation, vv, trifinder=trap_finder)
        u = interp_u(x, y)
        v = interp_v(x, y)
    else:
    #    primero interpolacion en el espacio
    #    interpolacion cubica
    #    interp_u1 = tri.CubicTriInterpolator(trisurface, u1, trifinder=trap_finder)
    #    interp_v1 = tri.CubicTriInterpolator(trisurface, v1, trifinder=trap_finder)
    #    interp_u2 = tri.CubicTriInterpolator(trisurface, u2, trifinder=trap_finder)
    #    interp_v2 = tri.CubicTriInterpolator(trisurface, v2, trifinder=trap_finder)
    #    interpolacion linear
        interp_u1 = tri.LinearTriInterpolator(trap_finder._triangulation, u1, trifinder=trap_finder)
        interp_v1 = tri.LinearTriInterpolator(trap_finder._triangulation, v1, trifinder=trap_finder)
        interp_u2 = tri.LinearTriInterpolator(trap_finder._triangulation, u2, trifinder=trap_finder)
        interp_v2 = tri.LinearTriInterpolator(trap_finder._triangulation, v2, trifinder=trap_finder)
        uu1 = interp_u1(x, y)
        vv1 = interp_v1(x, y)
        uu2 = interp_u2(x, y)
        vv2 = interp_v2(x, y)
    #    despues en el tiempo
        u = tfac1 * uu2 + tfac2 * uu1
        v = tfac1 * vv2 + tfac2 * vv1

    #print "END InterpolaVel"
    return u, v
