__author__ = 'root'

class CTInputData:
    def __init__(self, nombre_escenario,es_droga, points_file, nombre_trayectoria, x, y, indole, hora_inicio, hora_fin,
                 volumen, mag_vol, peso, valor_peso, densidad, viscocidad, coef_tension, oilvis, oilvisreftem, salinidad,
                 temperatura_p, profundidad_p, densidad_p, densidad_p15, radio_v, v_p, u_p, w_p, tiempo_final, constante_E, fecha):
        self.nombre_escenario = nombre_escenario
        self.es_droga = es_droga
        self.points_file = points_file
        self.nombre_trayectoria = nombre_trayectoria
        self.x = x
        self.y = y
        self.indole = indole
        self.hora_inicio = hora_inicio
        self.hora_fin = hora_fin
        self.volumen = volumen
        self.mag_vol = mag_vol
        self.peso = peso
        self.valor_peso = valor_peso
        self.densidad = densidad
        self.viscocidad = viscocidad
        self.coef_tension = coef_tension
        self.oilvis = oilvis
        self.oilvisreftem = oilvisreftem
        self.salinidad_p = salinidad
        self.temperatura_p = temperatura_p
        self.profundidad_p = profundidad_p
        self.densidad_p = densidad_p
        self.densidad_p15 = densidad_p15
        self.radio_v = radio_v
        self.v_p = v_p
        self.u_p = u_p
        self.w_p = w_p
        self.tiempo_final = tiempo_final
        self.constante_E = constante_E
        self.fecha = fecha