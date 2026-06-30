from __future__ import print_function

import sys
sys.path.append('logica/drog')

from CalculoEscenario import nuevo_escenario
from CalculoTrayectoria import datos_especificos
from Generic.ReadConfig import ReadConfig
from generate_plots import makeplots
import create_config as ctc

def drog(data_front, bool_sat=False, files_poligon= " ", densidades=[1]):
    for densidad in densidades:
        if bool_sat:
            input_data = ctc.create_config(files_poligon, densidad)
        else:
           # try:
            #    input_data = ReadConfig(sys.argv[1]).data
            #except IndexError:
                try:
                    input_data = ReadConfig('logica/drog/config.cfg').data
                except IOError:
                    print("ERROR: No config found")
                    sys.exit(0)

        if not 'General' in input_data:
            input_data['General'] = {'model_data': './',
                                    'output_data': './'}

        create_esc = input_data['Run']['create_esc']
        get_esc = input_data['Run']['get_esc']
        plot_esc = input_data['Run']['plot_esc']

        if 'Scenario'in input_data and create_esc:
            nuevo_escenario.scenario_creator(input_data)

        if 'Model'in input_data:
            if get_esc:
                datos_especificos.datos_especifico(input_data, data_front)
            if 'plots' in input_data['Model'] and plot_esc:
                kml_file = makeplots.makeplots(input_data)

    print('END MODEL RUN')
    
    # Obtener el contenido del archivo KML como una cadena
    kml_content = kml_file.kml()
    print(kml_content)

    return kml_content
