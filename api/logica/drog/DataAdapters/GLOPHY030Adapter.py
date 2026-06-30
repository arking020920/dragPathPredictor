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
    
def fill_data(dict, list, list1):
    import numpy as np
    
    uv_viento = dict['nodos']
    nu_nodos = len(uv_viento)
    u_int = np.zeros(nu_nodos)
    v_int = np.zeros(nu_nodos)
    
    for keys in list:
        if keys in dict:
            uv_viento = np.column_stack((uv_viento, dict[keys][0], dict[keys][1]))
        else:
            n = 0
            while keys != list1[n]:
                n += 1
            
            n1 = n - 1
            while not list1[n1] in dict:
                n1 -= 1
            
            n2 = n + 1
            while not list1[n2] in dict:
                n2 += 1
            
            for i in range(nu_nodos):
                u_int[i] = 1. * (n2 - n) / (n2 - n1) * dict[list1[n1]][0][i] + 1. * (n - n1) / (n2 - n1) * \
                           dict[list1[n2]][0][i]
                v_int[i] = 1. * (n2 - n) / (n2 - n1) * dict[list1[n1]][1][i] + 1. * (n - n1) / (n2 - n1) * \
                           dict[list1[n2]][1][i]
            
            uv_viento = np.column_stack((uv_viento, u_int, v_int))
    return uv_viento

def fill_temp(dict, list, list1):
    import numpy as np

    temp = dict['nodos']
    nu_nodos = len(temp)
    t_int = np.zeros(nu_nodos)

    for keys in list:
        if keys in dict:
            temp = np.column_stack((temp, dict[keys]))
        else:
            n = 0
            while keys != list1[n]:
                n += 1

            n1 = n - 1
            while not list1[n1] in dict:
                n1 -= 1

            n2 = n + 1
            while not list1[n2] in dict:
                n2 += 1

            for i in range(nu_nodos):
                t_int[i] = 1. * (n2 - n) / (n2 - n1) * dict[list1[n1]][i] + 1. * (n - n1) / (n2 - n1) * \
                           dict[list1[n2]][i]

            temp = np.column_stack((temp, t_int))
    return temp


def Build_Dict(x, y, uv_corr, temp, file_data, datenum_ini, cant_dias, det_recep):
    # importar la libreria para la interpolacion
    from scipy import interpolate
    from netCDF4 import Dataset
    import datetime as dt
        
    variables = Dataset(file_data)
    v = variables['vo'][:,0,:,:]
    u = variables['uo'][:,0,:,:]
    lat = variables['latitude'][:]
    lon = variables['longitude'][:]
    t = variables['thetao'][:,0,:,:]

    # print u,v
    # u[np.where(u == -30)] = 0
    # v[np.where(v == -30)] = 0
    ind = range(1, np.shape(u)[0])

    for num_day in ind:
        day = '0%s' % str(num_day) if num_day < 10 else str(num_day)
        fecha = dt.datetime.strptime(file_data[-9:-3] + day, '%Y%m%d')
        datenum = fecha.toordinal()
        if det_recep*(datenum-datenum_ini) <= int(cant_dias) and det_recep*(datenum-datenum_ini)>=-1:
            # interpolacion espacial de la u y la v en la zona seleccionada
            n = x.size
            
            intu = interpolate.interp2d(lon, lat, u[num_day-1,:,:])
            unew = [intu(x[j], y[j]) for j in range(n)]
            
            intv= interpolate.interp2d(lon, lat, v[num_day-1,:,:])
            vnew = [intv(x[j], y[j]) for j in range(n)]

            intt= interpolate.interp2d(lon, lat, t[num_day-1,:,:])
            tnew = [intt(x[j], y[j]) for j in range(n)]

            key = file_data[-9:-3] + day + '12'
            
            uv_corr.__setitem__(key, [unew, vnew])
            temp.__setitem__(key, tnew)
    return uv_corr, temp, datenum + det_recep


class GLOPHY030Adapter(Adapter.Adapter):
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
        
        uv_corr = {'nodos': nodes[:, 0]}
        temp = {'nodos': nodes[:, 0]}
        cant_file = 0
        datenum_ini = datenum
        
        while det_recep*(datenum-datenum_ini) <= int(self.cant_dias):



            fecha = dt.datetime.fromordinal(datenum)

            if fecha.month < 10:
                file_name = 'currentRE%s0%s' % (str(fecha.year), str(fecha.month))
            else:
                file_name = 'currentRE%s%s' % (str(fecha.year), str(fecha.month))
            
            file_data = '%s/%s.nc' % (path, file_name)
            
            if os.path.isfile(file_data):
                cant_file += 1
                
                # leo el archivo netcdf actual
                uv_corr, temp, datenum = Build_Dict(x, y, uv_corr, temp, file_data, datenum_ini, self.cant_dias, det_recep)
        
        if cant_file == 0:
            print ('data no found')
        
        else:
            list = model_times(self.fecha_inicio, int(self.cant_dias), self.d_time, det_recep)
            dnum = dt.datetime.strptime(self.fecha_inicio, '%d/%m/%Y').toordinal()
            fcha = dt.datetime.fromordinal(dnum - det_recep)
            year = str(fcha.year)
            month = '0%s' % str(fcha.month) if fcha.month < 10 else str(fcha.month)
            day = '0%s' % str(fcha.day) if fcha.day < 10 else str(fcha.day)

            list1 = model_times('%s/%s/%s'%(day, month, year), int(self.cant_dias)+2, self.d_time, det_recep)
            corr = fill_data(uv_corr, list, list1)
            temp = fill_temp(temp, list, list1)

            
            # salvar el fichero 'wind.txt'
            np.savetxt('%s/uv_corr.txt' % self.dir_esc, corr)
            np.savetxt('%s/temp.txt' % self.dir_esc, temp)
        
        if fecha.month < 10:
            mm ='0%s' % str(fecha.month)
        else:
            mm = str(fecha.month)

        if fecha.day < 10:
            date ='0%s/%s/%s' % (str(fecha.day),  str(mm), str(fecha.year))
        else:
            date = '%s/%s/%s' % (str(fecha.day),  str(mm), str(fecha.year))
        
        return temp, date, 3, self.fecha_inicio, corr
