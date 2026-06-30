__author__ = 'frank'
import numpy as np
import scipy.interpolate as scint

def FindMatrixInExtrmes(x, y, model):

    # encontrar los limites del .nod(zona seleccionada)
    x0 = min(x)
    x1 = max(x)
    y1 = min(y)
    y0 = max(y)
    # encontrar los indices que cumplan con los limites en y(esto en matlab se hace con un simple find(), pero en python..........)
    #el valor "0.62" es en realidad el paso de x 'y' y + 0.05
    ind1 = (np.where((model[:,0] >= (y1 - 0.62)) == True))[0]
    ind2 = (np.where((model[:,0] <= (y0 + 0.62)) == True))[0]
    # encontrar las coincidencias de los indices en y
        #se utiliza la fun set , despues hay q llevarlos a numpy arrays
    similars = np.array(list(set(ind1).intersection(ind2)))
    # se encuentra el modelo por las y
    model_in_y = model[similars]
    # encontrar los indices que cumplan con los limites en x(esto en matlab se hace con un simple find(), pero en python..........)

    ind1 = (np.where((model_in_y[:,1] + 0.62) >= (x0 - 0.62)))[0]
    ind2 = (np.where(model_in_y[:,1] <= (x1 + 0.62)))[0]
    similars = np.array(list(set(ind1).intersection(ind2)))
    model_final = model_in_y[similars]
    return model_final

def FormarMatrizUV(nx, ny, grid, x0, y0, dx, dy):

    # si se fueran a utilizar las 2 dimensiones usar shape como abajo
    # sz = grid.shape[0]
    # sz = len(grid)
    # este valor '550' puede entrar por parametro segun el modelo o la zona seleccionado(a)
    # datau = np.zeros((550,550))
    # datav = np.zeros((550,550))
    datau = np.zeros([nx, ny])
    datav = np.zeros([nx, ny])

    for row in grid:
        x = row[1]
        y = row[0]
        z1 = row[2]
        z2 = row[3]
        x = float(str((x - x0)/dx)[0:(str((x - x0)/dx).find('.'))])
        y = float(str((y - y0)/dy)[0:(str((y - y0)/dy).find('.'))])
        if datau[x + 1,0] == 0:
            datau[x + 1,0] = row[1]
            datav[x + 1,0] = row[1]
        if datau[0,y + 1] == 0:
            datau[0,y + 1] = row[0]
            datav[0,y + 1] = row[0]
        datau[x+1,y+1] = z1
        datav[x+1,y+1] = z2

    ind1 = np.where(datau[0,:] != 0)[0]
    ind1 = np.concatenate((np.array([0]),ind1))
    ind2 = np.where(datau[:,0] != 0)[0]
    ind2 = np.concatenate((np.array([0]),ind2))

    datau = datau[:,ind1]
    datau = (datau[ind2,:]).transpose()
    datav = datav[:,ind1]
    datav = (datav[ind2,:]).transpose()
    return datau,datav

def FormarMatrizUorV(nx, ny, grid, x0, y0, dx, dy):

    # si se fueran a utilizar las 2 dimensiones usar shape como abajo
    # sz = grid.shape[0]
    # sz = len(grid)
    # este valor '550' puede entrar por parametro segun el modelo o la zona seleccionado(a)
    # datau = np.zeros((550,550))
    #data = np.zeros((100, 100))
    data = np.zeros((nx, ny))
    for row in grid:
        x = row[1]
        y = row[0]
        z1 = row[2]
        x = float(str((x - x0)/dx)[0:(str((x - x0)/dx).find('.'))])
        y = float(str((y - y0)/dy)[0:(str((y - y0)/dy).find('.'))])
        if data[x + 1,0] == 0:
            data[x + 1,0] = row[1]
        if data[0,y + 1] == 0:
            data[0,y + 1] = row[0]
        data[x+1,y+1] = z1
    ind1 = np.where(data[0,:] != 0)[0]
    ind1 = np.concatenate((np.array([0]),ind1))
    ind2 = np.where(data[:,0] != 0)[0]
    ind2 = np.concatenate((np.array([0]),ind2))
    data = data[:,ind1]
    data = (data[ind2,:]).transpose()
    #np.savetxt('data.txt', data)

    return data

def GetVars(string):
    pos = string.find(":")
    bk_slhr = string.find('\r')
    resp = len((string[pos + 1:]).replace(" ","")) != 1 and (string[pos + 1:]).replace(" ","") or ""
    return resp[0:len(resp) - 2] if bk_slhr != -1 else resp[0:len(resp) - 1]


def InsertZero(self, value):
    return '0' + str(value) if value < 0 else str(value)



def Ll2Xy(lat, lon, reflat, reflong):
    # convertir de coordenadas geograficas a planas ya que el, funcionalidad copia de la
    # funcion de matlab, buscar en python que hay para usar que sea parecido

    r = 6367500
    reflong = reflong * np.pi / 180.
    reflat = reflat * np.pi / 180.
    xo = r * np.cos(reflat) * reflong
    yo = r * np.cos(reflat) * np.log((1 + np.sin(reflat)) / np.cos(reflat))
    rlong = lon * np.pi / 180.
    rlat = lat * np.pi / 180.
    x = r * np.cos(reflat) * rlong - xo
    y = r * np.cos(reflat) * np.log((1 + np.sin(rlat)) / np.cos(rlat)) - yo
    return x,y
    print ("END Ll2Xy")

def Xy2Ll(x, y, reflat, reflon):
    # import math
    # convertir de coordenadas planas a geograficas ya que el .nod de la zona viene en planas, funcionalidad copia de la
    # funcion de matlab, buscar en python que hay para usar que sea parecido

    reflat = reflat * np.pi / 180
    reflon = reflon * np.pi / 180
    r = 6.3675e+6
    x0 = r * np.cos(reflat) * reflon
    y0 = r * np.cos(reflat) * np.log((1.0 + np.sin(reflat)) / np.cos(reflat))
    rlon = (x + x0) / (r * np.cos(reflat))
    y = y + y0
    tol = 0.0001
    po = reflat * np.ones(np.shape(x))

    for i in range(0,1000):
        p1 = po - ((1.0 + np.sin(po)) / np.cos(po) - np.exp(y / (r * np.cos(reflat)))) / ((1.0 + np.sin(po)) / np.power(np.cos(po),2))
        # print(max(abs(p1 - po)) + '<' + tol)
        if max(abs(p1 - po)) < tol:
            break
        po = p1

    if i == 999:
        i = np.where(max(abs(p1 - po)) < tol)
        p1[i] = np.nan * p1[i]
        rlon[i] = np.nan * rlon[i]
        print ('Did not converge after 1000 iterations, some values NaN')

    rlat = p1
    lon = rlon * 180 / np.pi
    lat = rlat * 180 / np.pi
    return lat, lon

def GetExtremos(gridx,gridy):
    vecy, vecx = Xy2Ll(gridx, gridy, 19.747526, -85.766569)
    x0 = min(vecx)
    x1 = max(vecx)
    y1 = min(vecy)
    y0 = max(vecy)
    return x0, y0, x1, y1

def VelInterp_Interm(vel_interp, dt):
    # interpolar en el tiempo en dependencia del modelo
    result = vel_interp[:,0]
    sy = vel_interp.shape[1]
    interp_time = 6 if dt == 24 else 1
    for j in range(1,sy - 3,2):
        result = np.column_stack([result,vel_interp[:,[j,j+1]]])
        for i in range(interp_time, (dt - (interp_time - 1)), interp_time):

            #tfac1 = float(i/dt)
            #tfac2 = float(1 - tfac1)
            tfac1 = float(i) / float(dt)
            tfac2 = float(1) - tfac1
            ut = tfac1 * vel_interp[:,j+2] + tfac2 * vel_interp[:,j]
            vt = tfac1 * vel_interp[:,j+3] + tfac2 * vel_interp[:,j+1]
            result = np.column_stack([result,ut])
            result = np.column_stack([result,vt])

    result = np.column_stack([result,vel_interp[:,[(vel_interp.shape[1] - 2),vel_interp.shape[1] - 1]]])
    return result, interp_time

def temp_interp(temp, dt):
    newtemp = np.zeros((np.size(temp, 0), (np.size(temp, 1)-2)*dt+2))
    newtemp[:, 0] = temp[:, 0]
    for i in np.arange(np.size(temp, 0)):
        intemp = scint.interp1d(np.arange((np.size(temp, 1)-1))*dt, temp[i, 1:])
        newtemp[i, 1:] = intemp(np.arange((np.size(temp, 1)-2)*dt+1))
    return newtemp

def GetInvertedUv(uv):
    temp_uv = np.zeros(uv.shape)
    impars = uv[:, 1::2]
    pars = uv[:, 2::2]
    impars = np.fliplr(impars)
    pars = np.fliplr(pars)
    temp_uv[:, 1::2] = impars
    temp_uv[:, 2::2] = pars
    np.savetxt('old.txt', uv)
    np.savetxt('new.txt', temp_uv)
    return temp_uv


def GetTimeModels(init_date, dt, uv, nodes, cant_dias, temp=None, wind=None, corr=None):
    from CalculoEscenario import time_model_class
    from datetime import datetime, timedelta

    init_date = datetime.strptime(init_date, '%d/%m/%Y')
    list_time_model = []
    hours = np.arange(0, int(cant_dias) * 24 + 1, dt)
    dates = []
    uv_count = 1
    t_count = 1
    for h in hours:
        current_date = init_date + timedelta(hours=float(h))
        dates.append(current_date)
        if temp is not None and wind is not None:
            time_model = time_model_class.TimeModelClass(h, current_date, np.column_stack((nodes, uv[:, uv_count:uv_count + 2])),
                                                        np.column_stack((nodes, temp[:, t_count])),
                                                        np.column_stack((nodes, wind[:, uv_count:uv_count + 2])),
                                                        np.column_stack((nodes, corr[:, uv_count:uv_count + 2])))
        elif temp is not None:
            time_model = time_model_class.TimeModelClass(h, current_date,
                                                        np.column_stack((nodes, uv[:, uv_count:uv_count + 2])),
                                                        np.column_stack((nodes, temp[:, min(t_count, temp.shape[1] - 1)])),
                                                        None,
                                                        np.column_stack((nodes, corr[:, uv_count:uv_count + 2])))
        elif wind is not None:
            time_model = time_model_class.TimeModelClass(h, current_date, np.column_stack((nodes, uv[:, uv_count:uv_count + 2])),
                                                        None,
                                                        np.column_stack((nodes, wind[:, uv_count:uv_count + 2])),
                                                        np.column_stack((nodes, corr[:, uv_count:uv_count + 2])))
        else:
            time_model = time_model_class.TimeModelClass(h, current_date, np.column_stack((nodes, uv[:, uv_count:uv_count + 2])),
                                                        None,
                                                        None,
                                                        np.column_stack((nodes, corr[:, uv_count:uv_count + 2])))

        list_time_model.append(time_model)
        uv_count += 2
        t_count += 1
    return list_time_model

def GetUvByXy(trap_finder, t, x, y, list_time_model):
    import matplotlib.tri as tri

    #x, y = Ll2Xy(y, x, 19.747526, -85.766569)
    interp_u = interp_v = None
    for i in range(0, len(list_time_model)):
        if list_time_model[i].t_hour == t:
            xyuv = list_time_model[i].xyuv
            interp_u = tri.LinearTriInterpolator(trap_finder._triangulation, xyuv[:, 3], trifinder=trap_finder)(x, y)
            interp_v = tri.LinearTriInterpolator(trap_finder._triangulation, xyuv[:, 4], trifinder=trap_finder)(x, y)
            break
        elif list_time_model[i].t_hour < t < list_time_model[i + 1].t_hour:
            #interpolacion en el tiempo cdo el t introducido no corresponde a los guardados
            tfac1 = float(list_time_model[i].t_hour - t) / float(list_time_model[i].t_hour - list_time_model[i + 1].t_hour)
            tfac2 = 1 - tfac1
            u1 = list_time_model[i].xyuv[:, 3]
            u2 = list_time_model[i + 1].xyuv[:, 3]
            v1 = list_time_model[i].xyuv[:, 4]
            v2 = list_time_model[i + 1].xyuv[:, 4]
            uu = tfac1 * u2 + tfac2 * u1
            vv = tfac1 * v2 + tfac2 * v1
            interp_u = tri.LinearTriInterpolator(trap_finder._triangulation, uu, trifinder=trap_finder)(x, y)
            interp_v = tri.LinearTriInterpolator(trap_finder._triangulation, vv, trifinder=trap_finder)(x, y)
            break

    if interp_u is None and interp_v is None:
        raise Exception('Time passed is not in escenary')
        #return interp_u, interp_v
    elif interp_u.data is np.nan or interp_v.data is np.nan:
        print ('Wrong coords')
        return interp_u, interp_v
    else:
        return interp_u.data, interp_v.data


def get_impossed_data(imposed_type):
    path = './petromar/Datos/Impossed_Data/'
    import numpy as np
    imposed_data = np.loadtxt(path + imposed_type, delimiter=',')
    #not_rainy = np.loadtxt(path + 'poco_lluvioso', delimiter=',')
    #f_frio = np.loadtxt(path + 'frente_frio', delimiter=',')
    #south =  np.loadtxt(path + 'sur', delimiter=',')
    nodes = np.loadtxt(path + 'nodes', delimiter=',')
    #huricane = 1.5 * south
    return nodes, imposed_data


def imposed_data(Zone, days, imposed_type):
    from scipy.interpolate import griddata
    Path = './petromar/Datos/Zonas/'
    nodes = np.loadtxt(Path + Zone + '/' + Zone + '.nod')
    new_nodes, data = get_impossed_data(imposed_type)
    new_nodes[:, 0], new_nodes[:, 1] = Ll2Xy(new_nodes[:, 1], new_nodes[:, 0], 19.747526, -85.766569)
    corners = np.array(Ll2Xy(np.array([23.06, 22.98]), np.array([-82.8, -82.73]), 19.747526, -85.766569))
    max_lat = corners[0, 1]
    min_lat = corners[0, 0]
    max_lon = corners[1, 0]
    min_lon = corners[1, 1]
    full_nodes = np.array([[i-1, x, y] for i, x, y in zip(nodes[:, 0], nodes[:, 1], nodes[:, 2])
                                if x > min_lat and x < max_lat and y > min_lon  and y < max_lon])
    var = data
    u = var[:, 0::2]
    v = var[:, 1::2]
    u_int = np.zeros((np.size(full_nodes, axis=0), np.size(u, axis=1)))
    v_int = np.zeros((np.size(full_nodes, axis=0), np.size(u, axis=1)))
    for j in np.arange(np.size(u, axis=1)):
        u_int[:, j] = griddata(new_nodes, u[:, j], full_nodes[:, 1:], fill_value=True, method='nearest')
        v_int[:, j] = griddata(new_nodes, v[:, j], full_nodes[:, 1:], fill_value=True, method='nearest')
    u_int = np.array(u_int)
    v_int = np.array(v_int)

    imposed_vel = np.zeros((np.size(full_nodes, 0), 16*days+2))
    #imposed_vel = np.array([])

    for i in np.arange(1, days+1):
        imposed_vel[:, (i-1)*16:16*i:2] = u_int
        imposed_vel[:, (i-1)*16+1:16*i+1:2] = v_int





    #imposed_vel[:, i:-2:2] = u_int
    #imposed_vel[:, i+1:-1:2] = v_int

    imposed_vel[:, -2] = u_int[:, 0]
    imposed_vel[:, -1] = v_int[:, 0]

    return full_nodes, imposed_vel


def currents_spline_time_interp1d(uv_petromar, petromar_dt, ext_model_dt, total_time):
    """
    This method interpolate the time series of currents uv in the Stack Matrix data structure using Akima Method.

    :argument uv_petromar : The 2D-Array called Stack Matrix which is the data structure created for Petromar-3D
                            to save the scenario information in the form of vertical vectors stacked to the right.
                            The structure is
                            (nodes_id, u0, v0, u1, v1, ... , u_{ext_model_total_time}, v_{ext_model_total_time}).
    :argument petromar_dt : The time step demanded by Petromar-3D as a float value

    :argument total_time : The total time steps to be ran by Petromar-3D as a float value.

    :argument ext_model_dt : The time step in the data assimilated from an external model as a float value

    :rtype : Tuple(1darray of time steps, 2darray of the Stack Matrix of the nodes_id and the uv vectors)

    :author > M.Sc. Dayron Chang Dominguez, Proyecto Petromar-3D v2.1, CMM INSMET, Cuba (Ene 2021)
    """

    # Petromar time steps. These must be with in the interpolation interval ([0, 1, 2, ..., 22, 23] hours)
    petromar_t = np.arange(0, total_time, petromar_dt)

    # External model time steps. An additional time step is been included to guarantee the petromar_t will be
    # within the ext_model_t interval. This is important because NaN values could appear at the end of the interval if
    # this condition does not hold.
    ext_model_t = np.arange(0, total_time + ext_model_dt, ext_model_dt)

    # Initializing the resulting Stack Matrix. This matrix will be composed as follows: column 0 is reserved for the
    # identifiers of the nodes (Increasingly numbers from 1). Then vertical vectors u and v for each petromar time step.
    uv_result = np.zeros((uv_petromar.shape[0], petromar_t.shape[0] * 2 + 1))

    # Copy the nodes to the column 0
    uv_result[:, 0] = uv_petromar[:, 0]

    # For every node do a time interpolation of u and v vectors respectively
    for k_node in range(uv_petromar.shape[0]):
        # Select all the vector components of the u vectors for the k_node row
        u_values = uv_petromar[k_node, 1:ext_model_t.shape[0] * 2:2]
        # Select all the vector components of the v vectors for the k_node row
        v_values = uv_petromar[k_node, 2:ext_model_t.shape[0] * 2 + 1:2]

        # Create an Akima 1D interpolator for the u values
        s_uk = scint.Akima1DInterpolator(ext_model_t, u_values)
        # Create an Akima 1D interpolator for the v values
        s_vk = scint.Akima1DInterpolator(ext_model_t, v_values)

        # Interpolate u
        interp_u = s_uk(petromar_t)
        # Interpolate v
        interp_v = s_vk(petromar_t)

        # update the k_node row of uv_result Stack Matrix with the time interpolated u and v components.
        uv_result[k_node, 1:-1:2] = interp_u
        uv_result[k_node, 2::2] = interp_v

    # Return the Petromar time steps and the Stack Matrix
    return petromar_t, uv_result
