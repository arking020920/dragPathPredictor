__author__ = 'frank'
# import Scientific.IO.NetCDF as nc
"""
    Clase padre de los adaptadores de cada modelo
    Cada adaptador debe heredar de esta
"""

class Adapter:
    #Constructor de la clase
    def __init__(self, dir_esc, model_type, fecha_inicio, cant_dias, input_data):
        self.dir_esc = dir_esc
        self.model_type = model_type
        self.fecha_inicio = fecha_inicio
        self.cant_dias = cant_dias

    #Funcion principal que selecciona los ficheros con los que se interpola
    #posteriormente segun la fecha inicial y la cantidad de dias
    def GetMatrix(self, nodes, det_recep):
        pass












