__author__ = 'alex'

from . import Adapter
import numpy as np
import os
from scipy.io import netcdf
from Generic import GenericFunctions as gen

def find_lim(a, b, delta = 0):
    __doc____ = 'esta funcion devuelve los limites del menor subdominio del meshgrid de b[0][:] y b[1][:] siendo estos ' \
                'arreglos que contenga el meshgrid de a[0][:] y a[1][:] siendo estos dos arreglos'

    import numpy as np

    lim = [[np.where(b[0][:] <= np.min(a[0][:]) - delta)[0][-1], np.where(b[0][:] >= np.max(a[0][:]) + delta)[0][0]],
           [np.where(b[1][:] <= np.min(a[1][:]) - delta)[0][-1], np.where(b[1][:] >= np.max(a[1][:]) + delta)[0][0]]]

    return lim

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


def Build_Dict(x, y, uv_viento, file_data):
    # importar la libreria para la interpolacion
    from scipy import interpolate
    import pygrib as pgb
    variables = netcdf.netcdf_file(file_data).variables
    
    long_tmp = variables['XLONG'][0, :]
    lat_tmp = variables['XLAT'][:, 0]

    # Se escogen los datos del dominio de interes
    vert = find_lim([x, y], [long_tmp, lat_tmp], 0.62)
    lon = long_tmp[vert[0][0]:vert[0][1]]
    lat = lat_tmp[vert[1][0]:vert[1][1]]

    hour = 0
    # Se recorren la u y la v por los tiempos entre el dia actual
    
    # Se obtiene la u y la v del netcdf desde el dia actual y el horario correspodiente en el dominio de interes
    u = variables['U10'][0, vert[1][0]:vert[1][1], vert[0][0]:vert[0][1]]
    v = variables['V10'][0, vert[1][0]:vert[1][1], vert[0][0]:vert[0][1]]

    # interpolacion espacial de la u y la v en la zona seleccionada
    n = x.size

    intu = interpolate.interp2d(lon, lat, u)
    unew = [intu(x[j], y[j]) for j in range(n)]

    intv = interpolate.interp2d(lon, lat, v)
    vnew = [intv(x[j], y[j]) for j in range(n)]

    uv_viento.__setitem__(file_data[-22:-18]+file_data[-17:-15]+file_data[-14:-12]+file_data[-11:-9], [unew, vnew])

    return uv_viento


class WrfAdapter(Adapter.Adapter):
    """
        Adaptador de modelos de ficheros del modelo wrf de fisica de la atmosfera *.nc
        clase hija de Adapter para introducir en matriz los datos que
        se van a utilizar segun la fecha introducida y la cantidad de dias
    """
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
        datenum_end = datenum + int(self.cant_dias)

        while det_recep*datenum_end >= det_recep*datenum:

            fecha = dt.datetime.fromordinal(datenum)

            month = '0%s' % str(fecha.month) if fecha.month < 10 else str(fecha.month)
            day = '0%s' % str(fecha.day) if fecha.day < 10 else str(fecha.day)

            for hour in range(0, 24, 3):
                file_name = '%s-%s-%s_0%s' % (str(fecha.year), str(month), str(day), str(hour))if hour < 10 else '%s-%s-+%s_%s' % (str(fecha.year), str(month), str(day), str(hour))
                file_data = '%s/wrfout_d01_%s_00_00.nc' % (path, file_name)

                if os.path.isfile(file_data):
                    cant_file += 1

                    # leo el archivo netcdf actual

                    uv_viento = Build_Dict(x, y, uv_viento, file_data)
            datenum += det_recep

        if cant_file == 0:
            print ('data no found')

        else:
            list = model_times(self.fecha_inicio, int(self.cant_dias), self.d_time, det_recep)
            wind = fill_data(uv_viento, list, det_recep)

            # salvar el fichero 'wind.txt'
            np.savetxt('%s/uv_viento.txt' % self.dir_esc, wind)

        if fecha.month < 10:
            mm ='0%s' % str(fecha.month)
        else:
            mm = str(fecha.month)

        if fecha.day < 10:
            date ='0%s/%s/%s' % (str(fecha.day),  str(mm), str(fecha.year))
        else:
            date = '%s/%s/%s' % (str(fecha.day),  str(mm), str(fecha.year))
        
        return wind

