__author__ = 'alex'

from . import Adapter
import numpy as np
import os
from Generic import GenericFunctions as gen


def model_times(fecha_inicio, cant_dias, d_time, det_recep):
    import datetime as dt
    
    fecha_inicio = dt.datetime.strptime(fecha_inicio, '%d/%m/%Y')
    datenum = fecha_inicio.toordinal()
    lis_time = []
    for days in range(cant_dias + 1):
        
        fecha = dt.datetime.fromordinal(datenum + det_recep * days)
        year = str(fecha.year)
        month = '0%s' % str(fecha.month) if fecha.month < 10 else str(fecha.month)
        day = '0%s' % str(fecha.day) if fecha.day < 10 else str(fecha.day)
        
        if det_recep == 1:
            hours = range(0, 24, d_time)
        else:
            hours = range(24, -1, -1 * d_time)[1:]
            if days == cant_dias: break
        for h in hours:
            hour = '0%s' % str(h) if h < 10 else str(h)
            lis_time.append(year + month + day + hour)
            if days == cant_dias: break
    
    return lis_time


def fill_data(dict, list, recp=1):
    import numpy as np
    
    uv_viento = dict['nodos']
    nu_nodos = len(uv_viento)
    u_int = np.zeros(nu_nodos)
    v_int = np.zeros(nu_nodos)
    
    for keys in list[::recp]:
        if keys in dict:
            uv_viento = np.column_stack((uv_viento, dict[keys][0], dict[keys][1]))
        else:
            n = 0
            while keys != list[n]:
                n += 1

            n1 = n - 1
            while not list[n1] in dict:
                n1 -= 1

            n2 = n + 1
            while not list[n2] in dict:
                n2 += 1
            
            for i in range(nu_nodos):
                u_int[i] = 1. * (n2 - n) / (n2 - n1) * dict[list[n1]][0][i] + 1. * (n - n1) / (n2 - n1) * \
                           dict[list[n2]][0][i]
                v_int[i] = 1. * (n2 - n) / (n2 - n1) * dict[list[n1]][1][i] + 1. * (n - n1) / (n2 - n1) * \
                           dict[list[n2]][1][i]
            
            uv_viento = np.column_stack((uv_viento, u_int, v_int))
    return uv_viento


def Build_Dict(x, y, uv_viento, file_data, datenum_ini, cant_dias, det_recep):
    # importar la libreria para la interpolacion
    from scipy import interpolate
    from scipy.io import netcdf
    import datetime as dt
    
    variables = netcdf.netcdf_file(file_data).variables
        
    v = variables['vo'][:,0,:,:]
    u = variables['uo'][:,0,:,:]
    lat = variables['latitude'][:]
    lon = variables['longitude'][:]

    # print u,v
    # u[np.where(u == -30)] = 0
    # v[np.where(v == -30)] = 0
    if det_recep == 1:
        ind = range(np.shape(u)[0]-1)
    else:
        ind = range(np.shape(u)[0]-2, -1, det_recep)
        
    for i in ind:
        num_day = int(i/8)+1
        num_hour = 3*np.mod(i, 8)
        day = '0%s' % str(num_day) if num_day < 10 else str(num_day)
        fecha = dt.datetime.strptime(file_data[-9:-3] + day, '%Y%m%d')
        datenum = fecha.toordinal()
        if det_recep*(datenum-datenum_ini) <= int(cant_dias+1) and det_recep*(datenum-datenum_ini)>=0:
            # interpolacion espacial de la u y la v en la zona seleccionada
            n = x.size
            
            intu = interpolate.interp2d(lon, lat, u[i,:,:])
            unew = [intu(x[j], y[j]) for j in range(n)]
            
            intv= interpolate.interp2d(lon, lat, v[i,:,:])
            vnew = [intv(x[j], y[j]) for j in range(n)]
            
            hour = '0%s' % str(num_hour) if num_hour < 10 else str(num_hour)
            key = file_data[-9:-3] + day + hour
            
            uv_viento.__setitem__(key, [unew, vnew])
    return uv_viento, datenum + det_recep


class GLOPHY004Adapter(Adapter.Adapter):
    """
        Adaptador de modelos de ficheros del modelo roms de fisica de la atmosfera *.nc
        clase hija de Adapter para introducir en matriz los datos que
        se van a utilizar segun la fecha introducida y la cantidad de dias
    """
    
    # constructor
    def __init__(self, dir_esc, model_type, fecha_inicio, cant_dias, model_name, input_data):
        Adapter.Adapter.__init__(self, dir_esc, model_type, fecha_inicio, cant_dias, input_data)
        self.model_name = model_name
        self.inpath = input_data['General']['model_data']
        self.d_time = input_data['Scenario']['d_time']
    
    # funcion polimorfica que implementa Adapter.GetMAtrix(nodes, dt)
    def GetMatrix(self, nodes, det_recep):
        # importar la lib para la lectura de los netcdf
        # util para buscar el dia siguiente)
        import datetime as dt
        
        # obtengo las coordenadas de la zona para despues hallar los extremos
        x = nodes[:, 1]
        y = nodes[:, 2]
        # convierto las coordenadas de planas a geograficas
        y, x = gen.Xy2Ll(x, y, 19.747526, -85.766569)

        # buscar el modelo a procesar
        path = '%s/%s/%s' % (self.inpath, self.model_type, self.model_name)

        # convertir a objeto datetime la fecha introducida
        fecha = dt.datetime.strptime(self.fecha_inicio, '%d/%m/%Y')
        datenum = fecha.toordinal()
        
        uv_viento = {'nodos': nodes[:, 0]}
        cant_file = 0
        datenum_ini = datenum
        
        while det_recep*(datenum-datenum_ini) <= int(self.cant_dias+1):
            
            fecha = dt.datetime.fromordinal(datenum)

            if fecha.month < 10:
                file_name = 'current%s0%s' % (str(fecha.year), str(fecha.month))
            else:
                file_name = 'current%s%s' % (str(fecha.year), str(fecha.month))
            
            file_data = '%s/%s.nc' % (path, file_name)
            
            if os.path.isfile(file_data):
                cant_file += 1
                
                # leo el archivo netcdf actual
                uv_viento, datenum = Build_Dict(x, y, uv_viento, file_data, datenum_ini, self.cant_dias, det_recep)
        
        if cant_file == 0:
            print ('data no found')
        
        else:
            list = model_times(self.fecha_inicio, int(self.cant_dias), self.d_time, det_recep)
            corr = fill_data(uv_viento, list, det_recep)
            
            # salvar el fichero 'wind.txt'
            np.savetxt('%s/uv_corr.txt' % self.dir_esc, corr)

        if fecha.month < 10:
            mm ='0%s' % str(fecha.month)
        else:
            mm = str(fecha.month)

        if fecha.day < 10:
            date ='0%s/%s/%s' % (str(fecha.day),  str(mm), str(fecha.year))
        else:
            date = '%s/%s/%s' % (str(fecha.day),  str(mm), str(fecha.year))
        
        return date, 3, self.fecha_inicio, corr
