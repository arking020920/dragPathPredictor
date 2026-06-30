__author__ = 'alex'
from . import Adapter
import numpy as np
import os
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

    uv_corr = dict['nodos']
    nu_nodos = len(uv_corr)
    u_int = np.zeros(nu_nodos)
    v_int = np.zeros(nu_nodos)

    for keys in list[::recp]:
        if keys in dict:
            uv_corr = np.column_stack((uv_corr, dict[keys][0], dict[keys][1]))
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

            uv_corr = np.column_stack((uv_corr, u_int, v_int))
    return uv_corr


def Build_Dict(x, y, uv_viento, file_data):
    #importar la libreria para la interpolacion
    from scipy import interpolate
    import pygrib as pgb

    gribfile = pgb.open(file_data)

    grbsU = gribfile.select(name = '10 metre U wind component')
    grbsV = gribfile.select(name = '10 metre V wind component')

    for grbu, grbv in zip(grbsU, grbsV):
        vl_day = grbu.validDate

        u, latu, lonu = grbu.data(lat1= y.min(), lat2= y.max(), lon1= x.min()+360, lon2= x.max()+360)
        v, latv, lonv = grbv.data(lat1= y.min(), lat2= y.max(), lon1= x.min()+360, lon2= x.max()+360)

        lonu -= 360
        lonv -= 360

        #interpolacion espacial de la u y la v en la zona seleccionada
        n = x.size

        intu = interpolate.interp2d(lonu, latu, u)
        unew = [intu(x[j], y[j]) for j in range(n)]

        intv = interpolate.interp2d(lonv, latv, v)
        vnew = [intv(x[j], y[j]) for j in range(n)]

        year = str(vl_day.year)
        month = '0%s' % str(vl_day.month) if vl_day.month < 10 else str(vl_day.month)
        day = '0%s' % str(vl_day.day) if vl_day.day < 10 else str(vl_day.day)
        hour = '0%s' % str(vl_day.hour) if vl_day.hour < 10 else str(vl_day.hour)

        key = year + month + day + hour

        uv_viento.__setitem__(key, [unew, vnew])
    return uv_viento




class GFSAdapter(Adapter.Adapter):

    """
        Adaptador de modelos de ficheros del modelo roms de fisica de la atmosfera *.nc
        clase hija de Adapter para introducir en matriz los datos que
        se van a utilizar segun la fecha introducida y la cantidad de dias
    """
    #constructor
    def __init__(self, dir_esc, model_type, fecha_inicio, cant_dias, model_name, input_data):
        Adapter.Adapter.__init__(self, dir_esc, model_type, fecha_inicio, cant_dias, input_data)
        self.model_name = model_name
        self.inpath = input_data['General']['model_data']
        self.d_time = input_data['Scenario']['d_time']


    #funcion polimorfica que implementa Adapter.GetMAtrix(nodes, dt)
    def GetMatrix(self, nodes, det_recep):
        #importar la lib para la lectura de los netcdf
        #util para buscar el dia siguiente)
        from scipy.io import netcdf
        import datetime as dt

        # obtengo las coordenadas de la zona para despues hallar los extremos
        x = nodes[:, 1]
        y = nodes[:, 2]
        # convierto las coordenadas de planas a geograficas
        y, x = gen.Xy2Ll(x, y, 19.747526, -85.766569)

        #convertir a objeto datetime la fecha introducida
        date = dt.datetime.strptime(self.fecha_inicio,'%d/%m/%Y')

        #buscar el modelo a procesar
        year = str(date.year)
        month = '0%s' % str(date.month) if date.month < 10 else str(date.month)
        day = '0%s' % str(date.day) if date.day < 10 else str(date.day)
        hour = '06'

        folder = year + month + day + hour +'00'
        path = '%s/%s/%s/%s' % (self.inpath, self.model_type, self.model_name, folder)

        uv_viento = {'nodos' : nodes[:, 0]}
        cant_file = 0
        dd = 0

        while dd <= int(self.cant_dias):

            for h in np.arange(0,24,3):
                hf = 8*dd + h
                if hf < 10:
                    hh = ('0%s' % (str(hf)))
                else:
                    hh = (str(hf))

                file_data = '%s/gfs.t%sz.pgrb2full.0p50.f0%s' % (path, folder[-4:-2], hh)
                print(file_data)
                if os.path.isfile(file_data):
                    cant_file += 1

                    # leo el archivo netcdf actual

                    uv_viento = Build_Dict(x, y, uv_viento, file_data)
            dd += 1


        if cant_file == 0:
            print ('data no found')

        else:
            list = model_times(self.fecha_inicio, int(self.cant_dias), self.d_time, det_recep)
            wind = fill_data(uv_viento, list, det_recep)

            # salvar el fichero 'wind.txt'
            np.savetxt('%s/uv_viento.txt' % self.dir_esc, wind)


        return wind



