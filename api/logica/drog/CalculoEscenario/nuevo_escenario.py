import os
import numpy as np
import CalculoEscenario.VelocidadTotal as calc_uv
from Generic import paths
from scipy.io import netcdf as nc


# import GenericFunctions as gen
# import esc_class


def scenario_creator(input_data):
    """ Creacion del Escenario de Petromar """
    # leer el fichero de configuracion "NuevoEscenario.conf"
    # nombre_escenario, dir_escenario, fecha_inic, cant_dias, zona_s, corriente, viento, oleaje, det_recep = ReadNuevoEscenario.ReadNeConf()
    nombre_escenario = input_data['Scenario']['nombre_escenario']
    dir_escenario = input_data['General']['output_data']
    fecha_inic = input_data['Scenario']['fecha_inic']
    cant_dias = input_data['Scenario']['cant_dias']
    zona_s = input_data['Scenario']['zona_s']
    corriente = input_data['Scenario']['corriente']
    viento = input_data['Scenario']['viento']
    oleaje = input_data['Scenario']['oleaje']
    det_recep = input_data['Scenario']['det_recep']
    bool_temperature = False
    bool_viento = False

    # cargar los datos de la zona seleccionada
    geo_dir = paths.geo_dir()
    if os.path.isdir(os.path.join(geo_dir,zona_s)):
        nodes = np.loadtxt(os.path.join(geo_dir,zona_s,zona_s+'.nod'))
    else:
        raise IOError("No zone")
    esc_path = '%s/%s' % (dir_escenario, nombre_escenario)

    # Creacion de los objetos segun el tipo de modelo
    # modelos de corriente
    if corriente == 'coastwatch':
        from DataAdapters import CoastwatchAdapter as Coastwatch
        # convertir los ficheros al dato comun para comenzar a crear el escenario
        xyuv = Coastwatch.CoastwatchAdapter(esc_path, 'Ocean', fecha_inic, cant_dias, corriente, input_data)

    if corriente == 'Delft3D2':
        from DataAdapters import Delft3D2Adapter as Delft3D2
        # convertir los ficheros al dato comun para comenzar a crear el escenario
        xyuv = Delft3D2.Delft3D2Adapter(esc_path, 'Ocean', fecha_inic, cant_dias, corriente, input_data)

    elif corriente == 'PHY_003_024':
        from DataAdapters import PHY_003_024Adapter as PHY_003_024
        xyuv = PHY_003_024.PHY_003_024Adapter(esc_path, 'Ocean', fecha_inic, cant_dias, corriente, input_data)
        bool_temperature = True

    elif corriente == 'ncom':
        from DataAdapters import NcomNCAdapter as ncom
        xyuv = ncom.NcomNCAdapter(esc_path, 'Ocean', fecha_inic, cant_dias, corriente, input_data)
        bool_temperature = True

    elif corriente == 'GLOPHY004':
        from ..DataAdapters import GLOPHY004Adapter as GLOPHY004
        xyuv = GLOPHY004.GLOPHY004Adapter(esc_path, 'Ocean', fecha_inic, cant_dias, corriente, input_data)

    elif corriente == 'GLOPHY030':
        from DataAdapters import GLOPHY030Adapter as GLOPHY030
        xyuv = GLOPHY030.GLOPHY030Adapter(esc_path, 'Ocean', fecha_inic, cant_dias, corriente, input_data)
        bool_temperature = True

    elif corriente == 'hycom':
        from DataAdapters import HycomAdapter as hycom
        xyuv = hycom.HycomAdapter(esc_path, 'Ocean', fecha_inic, cant_dias, corriente, input_data)

    elif corriente == 'hycm':
        from ..DataAdapters import HycmAdapter as hycm
        xyuv = hycm.HycmAdapter(esc_path, 'Ocean', fecha_inic, cant_dias, corriente, input_data)
        bool_temperature = True

    elif corriente == 'roms':
        from DataAdapters import RomsNcAdapter as roms
        xyuv = roms.RomsNcAdapter(esc_path, 'Ocean', fecha_inic, cant_dias, corriente, input_data)
        bool_temperature = True

    elif corriente == 'grib2nc':
        from DataAdapters import Grib2NcAdapter as grib2
        xyuv = grib2.Grib2NcAdapter(esc_path, 'Ocean', fecha_inic, cant_dias, corriente)

    elif corriente == 'btsantos':
        from DataAdapters import BTSantosAdapter as btsantos
        xyuv = btsantos.BTSantosAdapter(esc_path, 'Ocean', fecha_inic, cant_dias, corriente, input_data)

    elif corriente == 'NEBrasil':
        from DataAdapters import AmazonasAdapter as amazonas
        xyuv = amazonas.AmazonasAdapter(esc_path, 'Ocean', fecha_inic, cant_dias, corriente, input_data)
    # else el restante cuando tengamos cubierto bastante modelos

    # modelos de viento
    if viento == 'wrf':
        from DataAdapters import WrfAdapteras as Wrf
        xyuv_wind = Wrf.WrfAdapter(esc_path, 'wind', fecha_inic, cant_dias, viento, input_data)
        bool_viento = True

    if viento == 'CFS':
        from DataAdapters import CFSAdapter as CFS
        xyuv_wind = CFS.CFSAdapter(esc_path, 'wind', fecha_inic, cant_dias, viento, input_data)
        bool_viento = True
    elif viento == 'Nam':
        from DataAdapters import NamAdapter as Nam
        xyuv_wind = Nam.NamAdapter(esc_path, 'wind', fecha_inic, cant_dias, viento, input_data)
        bool_viento = True

    elif viento == 'GFS':
        from DataAdapters import GFSAdapter as GFS
        xyuv_wind = GFS.GFSAdapter(esc_path, 'wind', fecha_inic, cant_dias, viento, input_data)
        bool_viento = True
        
    elif viento == 'GFS':
        from DataAdapters import GFS_diagAdapter as GFS
        xyuv_wind = GFS.GFSAdapter(esc_path, 'wind', fecha_inic, cant_dias, viento, input_data)
        bool_viento = True

    elif viento == 'CMEMS':
        from DataAdapters import CMEMSWindAdapter as CMEMSWind
        #xyuv_wind = CFSAdapter.CFSAdapter(esc_path, 'wind', fecha_inic, cant_dias, viento, input_data)
        xyuv_wind = CMEMSWind.CMEMSAdapter(esc_path, 'wind', fecha_inic, cant_dias, viento, input_data)
        bool_viento = True

    # crear el directorio del escenario
    if not os.path.isdir(esc_path):
        os.mkdir(esc_path)
        os.mkdir('%s/tracks' % esc_path)
        # os.mkdir('%s/tracks/images' % esc_path)

    # obtener los ficheros de los modelos a utilizar segun la fecha seleccionada y la cantidad de dias
    if bool_temperature:
        temperature, final_date, interp_time, init_date, corr = xyuv.GetMatrix(nodes, det_recep)
    else:
        final_date, interp_time, init_date, corr = xyuv.GetMatrix(nodes, det_recep)

    if bool_viento:
        wind = xyuv_wind.GetMatrix(nodes, det_recep)
        #wind = xyuv_wind.GetMatrix(nodes, 1, det_recep)

    vel_corr = calc_uv.CalcVelTotal(esc_path, det_recep, zona_s, cant_dias)
    # list_time_model = gen.GetTimeModels(init_date, final_dt, vel_corr, nodes, cant_dias)
    # escenary = esc_class.Escenary(nombre_escenario, init_date, cant_dias, final_dt, zona_s, corriente, viento, oleaje, 1, list_time_model)
    dim_vel_corr = len(vel_corr)
    sz_zone = len(zona_s)


    # Creacion del netcdf para guardar los datos del escenario
    # crear el netcdf con libreria scipy ya q es la q hemos estado usando
    f = nc.netcdf_file('%s/%s.nc' % (esc_path, nombre_escenario), 'w')
    # variable historica o descriptiva del netcdf
    f.history = 'Archivo de configuracion del escenario creado'

    # crear dimensiones del netcdf (obligatorio, hay q estudiar mejor la estructura de los netcdf a la hora d crearlos)
    nc_name = f.createDimension('dim_esc_name', len(nombre_escenario))
    nc_current = f.createDimension('dim_current', len(corriente))
    if bool_viento:
        nc_wind = f.createDimension('dim_wind', len(viento))
    nc_corr = f.createDimension('dim_corr', len(corr))
    nc_wave = f.createDimension('dim_wave', 2)
    if bool_temperature:
        nc_temp = f.createDimension('dim_temp', len(temperature))
    nc_is_forecast = f.createDimension('dim_is_forecast', 1)

    nc_time = f.createDimension('dim_time', 2)
    nc_zone = f.createDimension('dim_zone', sz_zone)
    nc_uvshape = f.createDimension('dim_uvshape', 2)
    nc_final_speed = f.createDimension('dim_uv', dim_vel_corr)
    nc_corr_type = f.createDimension('dim_corr_type', len(corriente))

    # creacion de las variables del netcdf (hay q estudiar mejor la estructura de los netcdf a la hora d crearlos)
    var_name = f.createVariable('esc_name', 'c', ('dim_esc_name',))
    var_current = f.createVariable('current', 'c', ('dim_current',))
    if bool_viento:
        var_wind = f.createVariable('wind', 'c', ('dim_wind',))
    var_corr = f.createVariable('corr', 'c', ('dim_corr',))
    var_wave = f.createVariable('wave', 'c', ('dim_wave',))
    if bool_temperature:
        var_temp = f.createVariable('temp', 'c', ('dim_temp',))
    var_is_forecast = f.createVariable('is_forecast', 'b', ('dim_is_forecast',))

    var_zone = f.createVariable('zone', 'c', ('dim_zone',))
    var_time = f.createVariable('time', 'd', ('dim_time',))
    var_uvshape = f.createVariable('uvshape', 'd', ('dim_uvshape',))
    var_final_speed = f.createVariable('uv', 'd', ('dim_uv',))
    var_corr_type = f.createVariable('corr_type', 'c', ('dim_corr_type',))

    # asignacion de las variables del netcdf, se manejan parecido a estructuras en matlab
    var_name.name = nombre_escenario
    var_current.name = corriente
    if bool_viento:
        var_wind.name = 'wind'
        var_wind.data = wind
    var_corr.name = 'corr'
    var_corr.data = corr
    var_wave.name = oleaje
    if bool_temperature:
        var_temp.name = 'temp'
        var_temp.data = temperature
    var_is_forecast.det_recep = bool(det_recep)

    var_zone.name = zona_s
    var_time.inic = fecha_inic
    var_time.end = final_date
    var_time.days_count = cant_dias
    var_uvshape.dims = vel_corr.shape
    var_final_speed.uv = vel_corr
    var_corr_type.name = corriente

    f.close()

    # imprimir fichero .esc a ver si al final se utiliza de la misma forma
    # esc = open(esc_path+'/'+nombre_escenario+'.esc', 'w')
    esc = open('%s/%s.esc' % (esc_path, nombre_escenario), 'w')
    # esc.write(zona_s + '-' + fecha_inic+'-'+final_date + '-')
    # Para Matlab!!!!!
    if det_recep:
        esc.write('%s-%s-%s-' % (zona_s, fecha_inic, final_date))
    else:
        esc.write('%s-%s-%s-2-' % (zona_s, fecha_inic, final_date))

    print("Nuevo escenario creado")

    '''
    times=[]
    for idx, tr in enumerate(vel_corr):
        times = np.append(times, idx)


    # Creacion del netcdf para guardar los datos del escenario
    from netCDF4 import Dataset
    f = Dataset('%s/%s.nc' % (esc_path, nombre_escenario), mode='w', format='NETCDF4_CLASSIC')

    # creando dimensiones del netcdf
    times_dim = f.createDimension('times', None)

    # variable historica o descriptiva del netcdf
    f.history = 'Archivo de configuracion del escenario creado'

    time = f.createVariable('time', np.float64, ('times',))
    time.units = 'hours since 1950-01-01'
    time.standard_name = 'time'

    esc_name = f.createVariable('esc_name', np.float64, ('1'))
    esc_name.units = 'none'
    esc_name.standard_name = 'esc_name'

    if bool_viento:
        wind = f.createVariable('wind', np.float64, (temperature.shape[0], temperature.shape[1]))
        wind.units = 'm/s'
        wind.standard_name = 'wind'

    corr = f.createVariable('corr', np.float64, vel_corr.shape)
    corr.units = 'm/s'
    corr.standard_name = 'current'

    wave = f.createVariable('wave', np.float64, ('times',))
    wave.units = 'm'
    wave.standard_name = 'wave'

    if bool_temperature:
        temp = f.createVariable('temp', np.float64, temperature.shape)
        temp.units = 'k'
        temp.standard_name = 'temperature'

    is_forecast = f.createVariable('is_forecast', bool, 1)
    is_forecast.units = 'none'
    is_forecast.standard_name = 'is_forecast'

    zone = f.createVariable('zone', str, 1)
    zone.units = 'none'
    zone.standard_name = 'zone'

    uvshape = f.createVariable('uvshape2', np.int, 2)
    uvshape.units = 'none'
    uvshape.standard_name = 'dimension_velocidad'

    uv = f.createVariable('uv', np.float64, vel_corr.shape)
    uv.units = 'm/s'
    uv.standard_name = 'corriente'

    corr_type = f.createVariable('corr_type', np.float64, ('times',))
    corr_type.units = 'none'
    corr_type.standard_name = 'corr_type'

    times.calendar = 'Julian'

    # asignacion de las variables del netcdf, se manejan parecido a estructuras en matlab
    esc_name = nombre_escenario
    if bool_viento:
        wind.data = wind
    corr.data = corr
    if bool_temperature:
        temp.data = temperature
    if det_recep==1:
        is_forecast.det_recep = True
    else:
        False

    zone.data = zona_s
    uvshape.dims = vel_corr.shape
    uv.data = vel_corr

    wave.data = oleaje
    corr_type.data = corriente

    from datetime import datetime
    from datetime import timedelta
    from netCDF4 import num2date, date2num

    date_now = datetime.strptime(fecha_inic, '%d/%m/%Y')
    print(date_now)
    list_dates = []
    for x in range(1,vel_corr.shape[1], 3):
        date_now = date_now + det_recep*timedelta(hours=1)
        list_dates.append(date_now)
    times[:] = date2num(list_dates, times.units)
    for item in list_dates:
        print('Fecha del proceso:', item)

    # Sincronizar y cerrar
    f.sync()
    f.close()


    # imprimir fichero .esc a ver si al final se utiliza de la misma forma
    # esc = open(esc_path+'/'+nombre_escenario+'.esc', 'w')
    esc = open('%s/%s.esc' % (esc_path, nombre_escenario), 'w')
    # esc.write(zona_s + '-' + fecha_inic+'-'+final_date + '-')
    # Para Matlab!!!!!
    if det_recep==1:
        esc.write('%s-%s-%s' % (zona_s, fecha_inic, final_date))
    else:
        esc.write('%s-%s-%s-2' % (zona_s, fecha_inic, final_date))

    print "Nuevo escenario creado"
    '''
