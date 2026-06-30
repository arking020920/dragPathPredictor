__author__ = 'root'
import numpy as np
from . import petrodrog as ptd
from OilWeathering import Weathering as weath


# def CalculaTrayectoria(file,points,grid,time_init, dift, dt, tf, volumen, densidad_mar, valor_peso, viscocidad, coef_tension):
def CalculaTrayectoria(uv, xi, yi, grid, dift, dt, tf, input_data, escenary, data_front):
    # trackx = np.array(xi)
    # tracky = np.array(yi)
    # trackr = np.array(0)
    # trackc = np.array(1)

    entro_expand = False
    bool_cambio_hora = False
    #time_init = input_data['Model']['hora_inicio']
    
    from datetime import datetime
    fecha_obj = datetime.strptime(data_front['startDate'], '%Y-%m-%dT%H:%M') # Convertir la fecha y hora de entrada a un objeto datetime
    #hora = fecha_obj.strftime('%H:%M') # Obtener la hora en formato HH:MM
    inicio_mes = fecha_obj.replace(day=1, hour=0, minute=0, second=0, microsecond=0) # Crear un objeto datetime para el primer día del mes a las 00:00
    diferencia = fecha_obj - inicio_mes # Calcular la diferencia en horas desde el inicio del mes
    time_init = int(diferencia.total_seconds() / 3600)  # Convertir segundos a horas
    #print("Horas desde el inicio del mes:", time_init)
    
    mag_vol = input_data['Model']['mag_vol']
    volumen = np.float64(input_data['Model']['volumen'])
    valor_peso = np.float64(input_data['Model']['valor_peso'])
    oilvis = np.float64(input_data['Model']['oilvis'])
    oilvisreftem = np.float64(input_data['Model']['oilvisreftem'])
    nele = np.float64(input_data['Model']['nele'])
    tinit2 = time_init
    time_step = np.array([0])

    ind = int(time_init / dift)
    list_time_model = escenary.list_time_model[ind:]
    # TODO verificar la inicializacion de weathering
    if mag_vol == 'barriles':
        vol = 0.15898729 * volumen
    elif mag_vol == 'm3':
        vol = volumen
    if escenary.wind is not None and escenary.temp is not None:
        oilweath = weath.Weathering(Volume=vol / nele, inAPI=valor_peso, inVis=oilvis,
                                    visRefTemp=oilvisreftem)
        oilweath.SetEnvironment(list_time_model[0].wind[0, 3], list_time_model[0].temp[0, 3])
    out_list = []
    for i, time_model in enumerate(list_time_model):
        try:
            time_model_next = list_time_model[i + 1]
        except Exception:
            break
        if bool_cambio_hora:
            continue
        if escenary.wind is not None and escenary.temp is not None:
            entro_expand, expand, out_list, nele, flag = ptd.PetroDrog(data_front, grid, time_model, time_model_next, dt, xi, yi, time_init,
                                                            input_data, entro_expand, out_list, escenary, tinit2,
                                                            oilweath)
            '''
            if flag:
                oilweath = weath.Weathering(Volume=vol / nele, inAPI=valor_peso, inVis=oilvis,
                                        visRefTemp=oilvisreftem)
                oilweath.SetEnvironment(list_time_model[0].wind[0, 3], list_time_model[0].temp[0, 3])
            '''
        else:
            entro_expand, expand, out_list, nele, flag = ptd.PetroDrog(data_front, grid, time_model, time_model_next, dt, xi, yi, time_init,
                                                            input_data, entro_expand, out_list, escenary, tinit2, None)

        if flag:
            input_data['Model']['nele'] = str(nele)

        xi, yi = out_list[-1].arr_tracks[:, 0], out_list[-1].arr_tracks[:, 1]
        time_init = None
        
    return out_list

