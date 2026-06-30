__author__ = 'root'
from . import Adapter
import numpy as np
import os
from Generic import GenericFunctions as gen


def GetCoords():
    """coordenadas especificas para el modelo roms de fisica
    u
    xdef xi_u 545 linear -87.68 0.028
    ydef eta_rho 258 linear 18.26 0.028

    v
    xdef xi_rho 546 linear -87.68 0.028
    ydef eta_v 257 linear 18.26 0.028

    temperature
    xdef xi_rho 546 linear -87.68 0.028
    ydef eta_rho 258 linear 18.26 0.028
    """
    #coords for u & v
    lons_temp_u = np.linspace(-87.68, -87.68 + (545 * 0.028), 545)
    lats_temp_u = np.linspace(18.26, 18.26 + (258 * 0.028), 258)
    lons_temp_v = np.linspace(-87.68, -87.68 + (546 * 0.028), 546)
    lats_temp_v = np.linspace(18.26, 18.26 + (257 * 0.028), 257)

    #coord for temperature
    lons_tmp_temper = np.linspace(-87.68, -87.68 + (546 * 0.028), 546)
    lats_tmp_temper = np.linspace(-18.26, 18.26 + (258 * 0.028), 258)



    lonsu, latsu = np.meshgrid(lons_temp_u, lats_temp_u)
    lonsv, latsv = np.meshgrid(lons_temp_v, lats_temp_v)
    lons_temper, lats_temper = np.meshgrid(lons_tmp_temper, lats_tmp_temper)
    latsu = latsu.flatten()
    lonsu = lonsu.flatten()
    latsv = latsv.flatten()
    lonsv = lonsv.flatten()
    lons_temper = lons_temper.flatten()
    lats_temper = lats_temper.flatten()
    return latsu, lonsu, latsv, lonsv, lats_temper, lons_temper


def BuildMatrices(variables, date, latsu, lonsu, latsv, lonsv, lats_temper, lons_temper, start, end, hour, nodes, uv_corr, temperature):
    #importar la libreria para la interpolacion
    from scipy import interpolate
    #obtengo las coordenadas de la zona para despues hallar los extremos
    x = nodes[:, 1]
    y = nodes[:, 2]
    #convierto las coordenadas de planas a geograficas
    y, x = gen.Xy2Ll(x, y, 19.747526, -85.766569)

    #obtengo la u y la v del netcdf desde el dia actual hasta el comienzo del dia sgte
    unc = variables['uz'][start:end, 0, :, :]
    vnc = variables['vz'][start:end, 0, :, :]
    tempernc = variables['tempz'][start:end, 0, :, :]
    str_hour = ''
    #recorro la u y la v por los tiempos entre el dia actual y el sgte
    for i in range(unc.shape[0]):
        str_hour = '0%s' % str(hour) #if hour < 10 else str(hour)
        #tempm = [[lats[j,k], lons[j,k], u[i,j,k], v[i,j,k]] for j in xrange(rng_lat) for k in xrange(rng_lon)]
        u = unc[i, :].flatten()
        v = vnc[i, :].flatten()
        temper = tempernc[i, :].flatten()
        ind = np.where(u > 100)[0]
        if len(ind) > 0:
            print ('Roms file of date %s is corrupted!!!!!' % date)
        u[np.where(u == -999)[0]] = 0
        v[np.where(v == -999)[0]] = 0
        temper[np.where(temper == -999)[0]] = 0
        tempmu = np.column_stack((latsu, lonsu, u))
        tempmv = np.column_stack((latsv, lonsv, v))
        temp_temper = np.column_stack((lats_temper, lons_temper, temper))
        tempmu = gen.FindMatrixInExtrmes(x, y, tempmu)
        tempmv = gen.FindMatrixInExtrmes(x, y, tempmv)
        temp_temper = gen.FindMatrixInExtrmes(x, y, temp_temper)

        #interpolacion espacial de la u y la v en la zona seleccionada
        unew = interpolate.griddata((tempmu[:, 1], tempmu[:, 0]), tempmu[:, 2], (x, y), method='linear', fill_value=999)
        vnew = interpolate.griddata((tempmv[:, 1], tempmv[:, 0]), tempmv[:, 2], (x, y), method='linear', fill_value=999)
        tempernew = interpolate.griddata((temp_temper[:, 1], temp_temper[:, 0]), temp_temper[:, 2], (x, y), method='linear', fill_value=999)
        del tempmu, tempmv, temp_temper
        hour += 3
        uv_corr = np.column_stack((uv_corr, unew, vnew))
        temperature = np.column_stack((temperature, tempernew))
    return uv_corr, date + str_hour, temperature

#def GetMissingFiles(esc_path):




class RomsNcAdapter(Adapter.Adapter):
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

    #funcion polimorfica que implementa Adapter.GetMAtrix(nodes, dt)
    def GetMatrix(self, nodes, delta_t, det_recep):
        #importar la lib para la lectura de los netcdf
        #y objeto tipo fecha (util a la hora de sumar 1 a la fecha buscando
        #el dia siguiente)
        from scipy.io import netcdf
        import datetime as dt

        #encontrar las coordenadas de roms segun el archivo de configurfacion del modelo
        latsu, lonsu, latsv, lonsv, lats_temper, lons_temper = GetCoords()

        #buscar el modelo a procesar
        path = '%s/%s/%s' % (self.inpath, self.model_type, self.model_name)

        #convertir a objeto datetime la fecha introducida
        fecha = dt.datetime.strptime(self.fecha_inicio,'%d/%m/%Y')
        init_date = fecha
        matrix, count_days = [], 0
        uv_corr = nodes[:, 0]
        temperature = nodes[:, 0]
        bool_next_day = False
        #verificare si el directorio de los modelos existe
        if os.path.isdir(path):
            #Recorro el directorio del modelo de forma ordenada(sorted(dir)), por alguna razon listdir
            #devuelve los elementos desordenados
            roms = sorted(os.listdir(path))
            loop_counter = 0
            for file_data in roms:

                #obtengo el objeto fecha de cada fichero
                date1 = dt.datetime.strptime(file_data[12:20], '%Y%m%d')
                #comparo si la fecha referencia y la del fichero de la iteracion actual coincide
                if fecha == date1:
                    # leo el archivo netcdf actual
                    ncfile = netcdf.netcdf_file('%s/%s' % (path, file_data))
                    #obtengo sus variables
                    variables = ncfile.variables
                    print ("interpolating file %s" % file_data)
                    #obtengo la uv temporal en el fichero actual y la ultima fecha que va tomando
                    if not bool_next_day:
                        uv_corr, date_last, temperature = BuildMatrices(variables, file_data[12:20], latsu, lonsu, latsv, lonsv, lats_temper, lons_temper, 25, 33, 0, nodes, uv_corr, temperature)
                        print('normal')
                        count_days += 1
                    else:
                        uv_corr, date_last, temperature = BuildMatrices(variables, file_data[12:20], latsu, lonsu, latsv, lonsv, lats_temper, lons_temper, 25, 26, 0, nodes, uv_corr, temperature)
                        print('final')
                        break
                    if count_days < int(self.cant_dias):
                        #aumento la fecha referencia
                        datenum = date1.toordinal()
                        fecha = dt.datetime.fromordinal(datenum + 1)
                        month = '0%s' % str(fecha.month) if fecha.month < 10 else str(fecha.month)
                        day = '0%s' % str(fecha.day) if fecha.day < 10 else str(fecha.day)
                        #date_temp = str(fecha.year) + month + day
                        date_temp = '%s%s%s' % (str(fecha.year), month, day)
                        #bool_missing = True if fe
                        #caso en que no existe el fichero del dia sgte, entonces se toman los intervalos
                        # de la fecha actual(un fichero roms tiene 48 intervalos cada 3 horas; 3 dias antes y despues
                        # de la fecha del fichero) funciona solamente con un solo fichero ausente, hay que
                        # implementarlo lo mas generico posible
                        temp_roms_file = 'roms_output_%s%s%s' % (str(fecha.year), month, day)
                        if not os.path.exists('%s/%s' % (path, temp_roms_file)):
                            uv_corr, date_last, temperature = BuildMatrices(variables, date_temp, latsu, lonsu, latsv, lonsv, lats_temper, lons_temper, 33, 41, 0, nodes, uv_corr, temperature)
                            print('falta uno')
                            #fecha = dt.datetime.fromordinal(datenum + 1)
                            fecha = dt.datetime.strptime(sorted(os.listdir(path))[(loop_counter+1)][12:20], '%Y%m%d')
                            count_days += 1
                    elif count_days == int(self.cant_dias):
                        datenum = date1.toordinal()
                        fecha = dt.datetime.fromordinal(datenum + 1)
                        month = '0%s' % str(fecha.month) if fecha.month < 10 else str(fecha.month)
                        day = '0%s' % str(fecha.day) if fecha.day < 10 else str(fecha.day)
                        bool_next_day = True
                        temp_roms_file = 'roms_output_%s%s%s' % (str(fecha.year), month, day)
                        if os.path.exists('%s/%s' % (path, temp_roms_file)):
                            continue
                        else:
                            uv_corr, date_last, temperature = BuildMatrices(variables, file_data[12:20], latsu, lonsu, latsv, lonsv, lats_temper, lons_temper, 33, 34, 0, nodes, uv_corr, temperature)
                            break

                        #date_temp = str(fecha.year) + month + day

                    else:
                        break
                if loop_counter <= len(os.listdir(path)):
                    loop_counter += 1
                else:
                    break
        #salvar el fichero 'uv_corr.txt'
        #uv_corr, interp_time = gen.VelInterp_Interm(uv_corr, delta_t)
        if not det_recep:
            uv_corr = gen.GetInvertedUv(uv_corr)

        np.savetxt('%s/uv_corr.txt' % self.dir_esc, uv_corr)
        np.savetxt('%s/temperature.txt' % self.dir_esc, temperature)
        #obtener la fecha final para imprimir el escenario.esc
        #valido para la versio de Matlab
        fecha_final = dt.datetime.strptime(date_last,'%Y%m%d%H')
        final_day = '0%s' % str(fecha_final.day) if fecha_final.day < 10 else str(fecha_final.day)
        final_month = '0%s' % str(fecha_final.month) if fecha_final.month < 10 else str(fecha_final.month)
        fecha_final = '%s/%s/%s' % (final_day, final_month, str(date1.year))
        return fecha_final, 3, init_date, temperature, uv_corr








