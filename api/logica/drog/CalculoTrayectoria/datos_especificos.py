from __future__ import print_function
from __future__ import print_function
from __future__ import print_function
import _pickle as cPickle
from generate_plots import plot_track, plot_all, plot2_all, plot2_track, coptions, simple_track, simple_all, plot_lost, weathering_plot, plot_mariel
import os
import sys
###
from netCDF4 import Dataset
###
import numpy as np
from scipy.io import netcdf

from CalculoTrayectoria import loadgrid as lg
from Generic import paths
#TODO Fix Blowout imports and plots
from BlowOut import bubble_class as bbc
# from BlowOut import plot as bbc_plot
# from BlowOut import hy_adapter as bbc_hy_adapt
from BlowOut import rooms_adapter as bbc_ra
from CalculoEscenario import esc_class
from Generic import GenericFunctions as gen


def datos_especifico(input_data, data_front):
    #input_data = reader.ReadCtConf()

    # file = open('../Datos/Escenarios/' + nombre_escenario + '/' + nombre_escenario + '.esc')
    # line = file.readline()
    # esc_nc = netcdf.netcdf_file('../Datos/Escenarios/'+input_data.nombre_escenario+'/'+input_data.nombre_escenario+'.nc', 'r')
    # Para trabajar con escenario particular, comentar esc_nameee y poner nombre de escenario
    zoneee = selet_zone(data_front['lat'], data_front['lon'])
    esc_nameee = name_esc(data_front['startDate'], zoneee, data_front['reverse'])
    #esc_nameee = 'ENE2024-040506'
    esc_nc = netcdf.netcdf_file('%s/%s/%s.nc' % (input_data['General']['output_data'], esc_nameee, esc_nameee),
                                'r')
    track_path = '%s/%s/tracks/%s' % (input_data['General']['output_data'], esc_nameee, input_data['Model']['nombre_trayectoria'])
    esc_f = open('%s/%s/%s.esc' % (input_data['General']['output_data'], esc_nameee, esc_nameee), 'r')
    esc_conf = esc_f.readline().split('-')
    esc_f.close()
    #date_ini = input_data['Scenario']['fecha_inic']
    import datetime
    date_str = data_front['startDate']
    # Convertir la cadena de fecha y hora al objeto datetime
    date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
    # Convertir solo la fecha (ignorando la hora) al formato 'DD/MM/YYYY'
    date_ini = date_obj.strftime('%d/%m/%Y')
    #print(date_ini)
    #time_ini = input_data['Model']['hora_inicio']

    if not os.path.exists(track_path):
        os.mkdir(track_path)
        os.mkdir('%s/images' % track_path)

    if np.float64(input_data['Model']['profundidad_p']) > 0:
        ad = bbc_ra.rooms_adapter(input_data, esc_nc.variables['time'].inic)
        lat_m, lon_m, nivel_m, u_m, v_m, tt, ss = ad.vars()
        cv = bbc.OilBubbleTracking(input_data)
        cv.StepIntergation(u_m, v_m, tt, ss, nivel_m, lat_m, lon_m)
        cv.SaveVar()
        h_t, b_t, x_t, y_t, z_t, w_t, v_t, u_t, wl_t, vl_t, ul_t, T_t, T_T, dty_def, E = cv.GetVar()
        lat_in, lon_in, b_in, v_in, d_t = cv.PetromInput()
        input_data.x = lon_in
        input_data.y = lat_in
        input_data.volumen = v_in/d_t
        input_data.radio_v = 200
        #os.chdir('../Datos/Escenarios/' + input_data.nombre_escenario + '/tracks/' + input_data.nombre_trayectoria)
        #bbc_plot.PlotPlume(b_t, x_t, y_t, z_t, w_t, v_t, u_t, E)
        #bbc_plot.PlotCurves(b_t, x_t, y_t, z_t, w_t, v_t, u_t, wl_t, vl_t, ul_t, T_t, E)
        #bbc_plot.PLotVelocities(w_t, T_T, x_t, E)
        #bbc_plot.PlotRadio(b_t, T_T, z_t, E)
        #bbc_plot.PlotDensity(dty_def, T_T, x_t, E)
        #bbc_plot.Plotconcentracion(b_t, T_T, E)
        #bbc_plot.Plotxy(x_t, y_t, z_t, E)
        #os.chdir('../../../../../CalculoTrayectoria/')


    # capturar el resto aki!!!!
    esc_name = ((esc_nc.variables['esc_name']).name).decode()
    init_date = ((esc_nc.variables['time']).inic).decode()
    days_count = (esc_nc.variables['time']).days_count

    zone = ((esc_nc.variables['zone']).name).decode()
    uv = (esc_nc.variables['uv']).uv
    dims_uv = (esc_nc.variables['uvshape']).dims
    corr_type = ((esc_nc.variables['corr_type']).name).decode()
    nodes = np.loadtxt(os.path.join(paths.geo_dir(), esc_conf[0], esc_conf[0]+'.nod'))

    corr = (esc_nc.variables['uv']).uv
    dift = input_data['Scenario']['d_time']
    uv = np.reshape(uv, dims_uv)
    corr = np.reshape(corr, dims_uv)


    if 'temp' in esc_nc.variables:
        if corr_type == 'ncomjjj':
            temp = (esc_nc.variables['temp']).data
            temp = np.reshape(temp, [dims_uv[0], dims_uv[1] / 2 - 1])
        else:
            temp = (esc_nc.variables['temp']).data
            temp = np.reshape(temp, [dims_uv[0], int((dims_uv[1] + 1)/2 )])

    if 'wind' in esc_nc.variables:
        wind = (esc_nc.variables['wind']).data
        wind = np.reshape(wind, dims_uv)

    if 'wind' in esc_nc.variables and 'temp' in esc_nc.variables:
        list_time_model = gen.GetTimeModels(init_date, dift, uv, nodes, days_count, temp=temp, wind=wind, corr=corr)
        escenary = esc_class.Escenary(esc_name, init_date, days_count, dift, zone, corr_type, 'wrf', None, 'roms', 1,
                                    list_time_model)
    elif 'temp' in esc_nc.variables:
        list_time_model = gen.GetTimeModels(init_date, dift, uv, nodes, days_count, temp=temp, wind=None, corr=corr)
        escenary = esc_class.Escenary(esc_name, init_date, days_count, dift, zone, corr_type, None, None, 'roms', 1,
                                    list_time_model)
    elif 'wind' in esc_nc.variables:
        list_time_model = gen.GetTimeModels(init_date, dift, uv, nodes, days_count, temp=None, wind=None, corr=corr)
        escenary = esc_class.Escenary(esc_name, init_date, days_count, dift, zone, corr_type, 'wrf', None, None, 1,
                                    list_time_model)
    else:
        list_time_model = gen.GetTimeModels(init_date, dift, uv, nodes, days_count, temp=None, wind=None, corr=corr)
        escenary = esc_class.Escenary(esc_name, init_date, days_count, dift, zone, corr_type, None, None, None, 1,
                                    list_time_model)

    # cargar los ficheros q hay en la carpeta de la zona en variables intento de la funcion de matlab "loadgrid"


    grid = lg.LoadGrid(zone, nodes)
    # x0, y0, x1, y1 = gen.GetExtremos(grid.gridx, grid.gridy)
    # u_by_xy, v_by_xy = gen.GetUvByXy(grid.trap_finder, 70, -84, 25, escenary.list_time_model)

    x0, y0, x1, y1 = gen.GetExtremos(grid.trap_finder._triangulation.x, grid.trap_finder._triangulation.y)

    if not input_data['Model']['es_droga']:
        x = np.float64(data_front['lat'])
        y = np.float64(data_front['lon'])
        if x0 < x < x1 and y0 > y > y1:

            # if mag_vol == 'litros':
            #    volumen /= 1000
            # elif mag_vol == 'barriles':
            #    volumen /= 6.28981

            # duda de por q se intercambian las "x" y las "y"
            x, y = gen.Ll2Xy(y, x, 19.747526, -85.766569)
            #if input_data['Model']['peso'] == 'grado api':
            if input_data['Model']['peso'] == 'densidad':
                api = (141.5 / np.float(input_data['Model']['valor_peso'])) * 1000 - 131.5
            elif input_data['Model']['peso'] == 'api':
                api = np.float64(input_data['Model']['valor_peso'])
            if api < 6.2:
                print("Wrong simulation!!!!: oil sinks")
            elif api > 55:
                print("Wrong simulation!!!!: oil doesn't exis")
            else:
                # points = np.array([[1, x, y]])
                tf = 0.15 * np.sqrt(np.float64(input_data['Model']['volumen']))
                x, y = np.array(x), np.array(y)
                # ndrogue = points.shape
                if input_data['Model']['indole'] == 'instantaneo':
                    from . calcula_trayectoria import CalculaTrayectoria as ct
                    # ct(uv, points, grid, 6, 1, tf, volumen, densidad_mar, valor_peso, viscocidad, coef_tension)
                    out_list = ct(uv, x, y, grid, dift, 1, tf, input_data, escenary, data_front)
                    # probando rk1 con dt = 3
                    # out_list, all_tracks, track_path = ct(uv, points, grid, dift, 3, tf, input_data, escenary)
        else:
            print("Something is wrong with init coords")
            sys.exit(1)
    else:
        #    validar las coordenadas de alguna forma

        from CalculaTrayectoriaDroga import CalculaTrayectoria as ctd

        points = np.loadtxt(input_data['Model']['points_file'])
        ctd(uv, points, grid, dift, 1, input_data, data_front)

    file = open(track_path+'/save.pk','wb')
    p = cPickle.Pickler(file)
    p.dump(out_list)


    times=[]
    longitude=[]
    latitude=[]
    xcenter=[]
    ycenter=[]
    volevap=[]
    voldisp=[]
    oilrho=[]
    oilvis=[]
    waterc=[]

    for idx, tr in enumerate(out_list):

        times = np.append(times, idx)
        masslat, masslon  = gen.Xy2Ll(np.array([tr.masscenter[0]]), np.array([tr.masscenter[1]]), 19.747526, -85.766569)
        xcenter = np.append(xcenter, masslon)
        ycenter = np.append(ycenter, masslat)

        tr_lats, tr_lons = gen.Xy2Ll(tr.arr_tracks[:, 0], tr.arr_tracks[:, 1], 19.747526, -85.766569)
        longitude = np.append(longitude, tr_lons)
        latitude = np.append(latitude, tr_lats)
        if escenary.wind is not None and escenary.temp is not None:
            volevap = np.append(volevap, np.average(tr.arr_volumeEvap))
            voldisp = np.append(voldisp, np.average(tr.arr_volumeNatDisp))
	
            oilrho = np.append(oilrho, np.average(tr.arr_density))
            oilvis = np.append(oilvis, np.average(tr.arr_viscosity))
            waterc = np.append(waterc, np.average(tr.arr_WaterCont))


    print('Creando el archivo netcdf')
    #f = nc.netcdf_file('%s/oiltrakparticles.nc' % (track_path), mode='w', format='NETCDF3_CLASSIC')
    f = Dataset('%s/oiltrakparticles.nc' % (track_path), mode='w', format='NETCDF4_CLASSIC')

    # creando dimensiones del netcdf
    times_dim = f.createDimension('times', None)
    #for dim in f.dimensions.items():
    #     print(dim)

    # Creando atributos globales
    f.title = 'Deriva y meteorizacion en un derrame'
    #print(f.title)
    f.subtitle = 'Archivo preliminar'
    #print(f.subtitle)
    f.history = 'Created 01/03/2023'
    #f.source = 'netCDF3 python example'
    #print(f)

    # Definiendo 5 variables
    times = f.createVariable('times', np.float64, ('times',))
    times.units = 'hours since 1950-01-01'
    times.long_name = 'times'
    volevap2 = f.createVariable('volevap2', np.float64, ('times'))
    volevap2.units = 'm3'
    volevap2.standard_name = 'Volumen_evaporado'
    voldisp2 = f.createVariable('voldisp2', np.float64, ('times',))
    voldisp2.units = 'm3'
    voldisp2.standard_name = 'Volumen_dispersado'
    oilrho2 = f.createVariable('oilrho', np.float64, ('times',))
    oilrho2.units = 'Kg/m3'
    oilrho2.standard_name = 'Densidad_petroleo'
    oilvis2 = f.createVariable('oilvis', np.float64, ('times',))
    oilvis2.units = 'cSt/m2'
    oilvis2.standard_name = 'Viscosidad_petroleo'
    waterc2 = f.createVariable('waterc', np.float64, ('times',))
    waterc2.units = '%'
    waterc2.standard_name = 'Agua_contenida_en_petroleo'
    times.calendar = 'Julian'
    
    # Atribuyendo datos a las variables creadas
    volevap2[:] = volevap[0:len(out_list)]
    voldisp2[:] = voldisp[0:len(out_list)]
    oilrho2[:] = oilrho[0:len(out_list)]
    oilvis2[:] = oilvis[0:len(out_list)]
    waterc2[:] = waterc[0:len(out_list)]
    #print('data asignada volevap:', volevap2.shape)
    #print('dimension:', volevap2.ndim)
    #print('data asignada voledisp:', voldisp2.shape)
    #print('dimension:', voldisp2.ndim)

    from datetime import datetime
    from datetime import timedelta
    from netCDF4 import num2date, date2num

    date_now = datetime.strptime(date_ini, '%d/%m/%Y')

    list_dates = []
    list_dates2 = []
    for x in range(0,len(out_list)):
        date_now = date_now + timedelta(hours=1)
        list_dates.append(date_now)
        if x == 0:
            datetime_index = out_list[0].time_init
            ahora = datetime_index.strftime('%Y%m%d-%H%M')
        else:
            datetime_index += timedelta(hours=1)
            ahora = datetime_index.strftime('%Y%m%d-%H%M')
        list_dates2.append(ahora)


    times.data = date2num(list_dates, times.units)

    # Sincronizar y cerrar
    f.sync()
    f.close()

    print("END datos_especificos")
    
def selet_zone(xo, yo):
    import matplotlib.path
    print(xo,yo)

    pfile=open('logica/drog/Geodata/Zones/zonas.txt')

    zonas={}
    list_z=[]
    points=[]

    for line in pfile.readlines():
        if line[0]=='z':
            zona=line[:-2]
            list_z.append(zona)
            
            points=[]
        elif line[0]=='[':
            a=line.split('], [')
            p= a[0][2:].split(',')
            points.append((float(p[0]),float(p[1])))
            for xy in a[1:-1]:
                p= xy.split(',')
                points.append((float(p[0]),float(p[1])))
            p= a[-1][:-3].split(',')
            points.append((float(p[0]),float(p[1])))
            zonas.__setitem__(zona, points)

    for key in list_z:
        points=zonas[key]
        path = matplotlib.path.Path(points, closed=True)
        a=[(xo,yo)]
        flag = path.contains_points(a)
        if flag:
            print(key)
            return key
    print('por aca')
    print('El derrame no se encuentra en ninguna zona de interes')
    
from datetime import datetime

def name_esc(date, zone, reverse=False):
    # Diccionario para mapear los nombres de los meses en inglés a español
    meses_es = {
        'JAN': 'ENE', 'FEB': 'FEB', 'MAR': 'MAR', 'APR': 'ABR', 
        'MAY': 'MAY', 'JUN': 'JUN', 'JUL': 'JUL', 'AUG': 'AGO', 
        'SEP': 'SEP', 'OCT': 'OCT', 'NOV': 'NOV', 'DEC': 'DIC'
    }
    
    # Convertir la fecha y hora a objeto datetime con el formato correcto
    try:
        fecha_obj = datetime.strptime(date, '%Y-%m-%dT%H:%M')
    except ValueError as e:
        print(f"Error de formato: {e}")
        return
    
    # Obtener el mes y año en el formato deseado
    mes_en = fecha_obj.strftime('%b').upper()
    mes_es = meses_es.get(mes_en, mes_en)
    anio = fecha_obj.strftime('%Y')
    
    # Verificar si 'zone' no es None y es un string antes de filtrar
    if zone and isinstance(zone, str):
        # Extraer la parte numérica de la zona
        zone_num = ''.join(filter(str.isdigit, zone))
    else:
        raise ValueError("La zona no es válida o es None")
    
    # Formatear la salida con el formato deseado
    escenario = f"{mes_es}{anio}-{zone_num}"
    
    # Añadir "-BACK" si reverse es True
    if reverse:
        escenario += "-BACK"

    return escenario
