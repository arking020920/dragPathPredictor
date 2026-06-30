__author__ = 'frank'
import os
import numpy as np
from . import Adapter
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


def Build_Dict(x, y, uv_corr, file_data):
    # importar la libreria para la interpolacion
    from scipy import interpolate

    model = np.loadtxt(file_data)

    # hallo los extremos del modelo segun la zona seleccionada
    # esto ayuda que el dato sea mas ligero a la hora de interpolar
    data = gen.FindMatrixInExtrmes(x, y, model)
    # matrix.append(data)
    lat = data[:, 0]
    lon = data[:, 1]
    # divido por 100 las velocidades en u y v, aplicable en el caso de coastwatch
    u = data[:, 2] / 100
    v = data[:, 3] / 100

    # interpolacion espacial de la u y la v en la zona seleccionada
    n = x.size

    intu = interpolate.interp2d(lon, lat, u)
    unew = [intu(x[j], y[j]) for j in range(n)]

    intv = interpolate.interp2d(lon, lat, v)
    vnew = [intv(x[j], y[j]) for j in range(n)]

    key = file_data[-20:-10]

    uv_corr.__setitem__(key, [unew, vnew])
    return uv_corr


class CoastwatchAdapter(Adapter.Adapter):
    """
        Adaptador de modelos de ficheros del modelo
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
        # importar objeto tipo fecha (util a la hora de sumar 1 a la fecha buscando
        # el dia siguiente)
        # y la libreria para la interpolacion respectivamente
        import datetime as dt
        from scipy import interpolate

        # buscar el modelo a procesar
        path = '%s/%s/%s' % (self.inpath, self.model_type, self.model_name)
        # convertir a objeto datetime la fecha introducida
        fecha = dt.datetime.strptime(self.fecha_inicio, '%d/%m/%Y')
        init_date = fecha
        matrix = []
        count = 0
        # verificare si el directorio de los modelos existe
        if os.path.isdir(path):
            # print sorted(os.listdir(path))
            # obtengo las coordenadas de la zona para despues hallar los extremos
            x = nodes[:, 1]
            y = nodes[:, 2]
            # convierto las coordenadas de planas a geograficas
            y, x = gen.Xy2Ll(x, y, 19.747526, -85.766569)
            list_time_model = []

            datenum = fecha.toordinal()

            uv_corr = {'nodos': nodes[:, 0]}
            cant_file = 0
            datenum_ini = datenum

            while det_recep*(datenum-datenum_ini) <= int(self.cant_dias+1):

                fecha = dt.datetime.fromordinal(datenum)

                if fecha.month < 10:
                    file_name = '%s0%s' % (str(fecha.year), str(fecha.month))
                else:
                    file_name = '%s%s' % (str(fecha.year), str(fecha.month))

                if fecha.day < 10:
                    file_data = '%s/%s0%s00_0000m.txt' % (path, file_name, str(fecha.day))
                else:
                    file_data = '%s/%s%s00_0000m.txt' % (path, file_name, str(fecha.day))


                if os.path.isfile(file_data):
                    cant_file += 1

                    # leo el archivo actual

                    uv_corr = Build_Dict(x, y, uv_corr, file_data)
                datenum +=det_recep

            if cant_file == 0:
                print ('data no found')

            else:
                list = model_times(self.fecha_inicio, int(self.cant_dias), self.d_time, det_recep)
                uv_corr = fill_data(uv_corr, list, det_recep)

                # salvar el fichero 'corr.txt'
                np.savetxt('%s/uv_corr.txt' % self.dir_esc, uv_corr)
                
        if fecha.month < 10:
            mm ='0%s' % str(fecha.month)
        else:
            mm = str(fecha.month)

        if fecha.day < 10:
            date ='0%s/%s/%s' % (str(fecha.day),  str(mm), str(fecha.year))
        else:
            date = '%s/%s/%s' % (str(fecha.day),  str(mm), str(fecha.year))

        return fecha, self.d_time, init_date, uv_corr
