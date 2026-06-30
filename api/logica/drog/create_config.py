def create_config(files_poligon=' ',valor_peso=20):
    a=files_poligon[0].split(':')
    fecha_inic = '%s/%s/%s' % (a[0][:2], a[0][3:5], a[0][6:10])
    hora = int(a[1])
    xo= float(a[2].split('_')[0])
    yo= float(a[2].split('_')[1])
    zona = selet_zone(xo, yo)
    nombre_escenario = files_poligon[0][0:10]
    nombre_trayectoria = 'Ncom_Nam'
    plot = 'email'
    #PLOTEOS CON PROBLEMAS: coption, all(_simpletrackcurrents.png)

    general = {'model_data': '/media/lwc1f3r/MMM/PROYECTO-RECALOS/Datos/', 'output_data': '/media/lwc1f3r/MMM/PROYECTO-RECALOS/Outputs/'}

    scenario = {'fecha_inic':fecha_inic, 'nombre_escenario': nombre_escenario, 'cant_dias': 2, 'zona_s':zona, 'corriente':'ncom',
                'viento':'', 'oleaje':'', 'det_recep':1, 'd_time':3, 'r_particula' : 111}

    model = {'nombre_escenario': nombre_escenario, 'es_droga': 0, 'nombre_trayectoria':nombre_trayectoria, 'numeric_schema':'rk4',
                'nele':1, 'x':xo, 'y':yo, 'indole':'instantaneo', 'hora_inicio': hora, 'hora_fin': hora + 10, 'volumen': 50,
                'mag_vol':'barriles', 'peso':'api', 'valor_peso':20, 'oilvis': 259.0, 'oilvisreftem': 25, 'densidad': 1027,
                'viscosidad': 140.267, 'coef_tension': 27, 'salinidad_p': 27, 'temperatura_p': 35, 'profundidad_p': 0, 'densidad_p': 898,
                'densidad15_p': 892, 'radio_v': 0.0001, 'v_p': -1, 'u_p': 1, 'w_p':2.1, 'tiempo_final': 700, 'constante_E': 0.5, 'plots': plot}

    satelite = {'bool_sat': True, 'files_poligon':files_poligon}

    run = {'create_esc': True, 'get_esc': True, 'plot_esc': True}

    data = {'General': general, 'Model': model, 'Scenario': scenario, 'Satelite': satelite, 'Run': run}
    return data


def selet_zone(xo, yo):
    print('Valores:',xo, yo)
    import matplotlib.path

    pfile=open('./Geodata/Zones/zonas.txt')

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
            return key

    print('El derrame no se encuentra en ninguna zona de interes')

