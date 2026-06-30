# from matplotlib.collections import AsteriskPolygonCollection

from __future__ import print_function

__author__ = 'root'

from . import belint, find_triangle as tri
import numpy as np
from . import track
from . import ExpandClass as expand
from . import descomponer
from . import rks
from datetime import datetime, timedelta
# !!!! importante!!!!!!esta libreria se usa para simular las asignaciones al mismo valor , si no se hace cdo
# modificas una variable que tiene el mismo valor q la otra , la otra tambien se modifica
import copy
from . import out_data_class as out
from Generic.ColorController import Bcolors


# def PetroDrog(grid, t1, t2, dt, xi, yi, ri, ci, V, time_init, volumen, densidad_mar, valor_peso, viscocidad, coef_tension, entro_expand, file, i):
# noinspection PyNoneFunctionAssignment


def PetroDrog(data_front, grid, time_model, time_model_next, dt, xx, yy, time_init, input_data, entro_expand, out_list, escenary,
              tinit2, oilweath=None):
	if grid.A is None or grid.B is None or grid.AO is None or grid.T is None:
		# implementacion de la funcion de matlab belint
		grid = belint.BelInt(grid)
	
	mag_vol = input_data['Model']['mag_vol']
	'''
	fecha_obj = datetime.strptime(data_front['endDate'], '%Y-%m-%dT%H:%M') # Convertir la fecha y hora de entrada a un objeto datetime
	#hora = fecha_obj.strftime('%H:%M') # Obtener la hora en formato HH:MM
	inicio_mes = fecha_obj.replace(day=1, hour=0, minute=0, second=0, microsecond=0) # Crear un objeto datetime para el primer día del mes a las 00:00
	diferencia = fecha_obj - inicio_mes # Calcular la diferencia en horas desde el inicio del mes
	time_end = int(diferencia.total_seconds() / 3600)  # Convertir segundos a horas
    #print("Horas desde el inicio del mes:", time_init)
 	'''
	time_end = input_data['Model']['hora_fin']
	volumen = np.float64(input_data['Model']['volumen'])
	valor_peso = np.float64(input_data['Model']['valor_peso'])
	peso = input_data['Model']['peso']
	densidad = np.float64(input_data['Model']['densidad'])
	viscosidad = np.float64(input_data['Model']['viscosidad'])
	coef_tension = np.float64(input_data['Model']['coef_tension'])
	radio_v = np.float64(input_data['Model']['radio_v'])
	nele = np.int64(input_data['Model']['nele'])
	
	bool_sat = input_data['Satelite']['bool_sat']
	if bool_sat:
		files_poligon = input_data['Satelite']['files_poligon']
	# llamada a la funcion para encontrar elemento(triangulo) dado punto de coordenadas,
	# da un elemeto menos que matlab ya que en python los indices empiezan en 0
	# xx, yy = np.array([xi]), np.array([yi])
	
	arr_lost = np.array([])
	# time_init = input_data.hora_inicio
	# print str(jnan)
	
	iterator = 0
	dtsecs = dt * 3600

	ruta_manual_esc = r'D:\Escenarios\ENE2024-040506-BACK\ENE2024-040506-BACK.esc'   # Define aquí la ruta manual del archivo .esc
    #esc_file = open(ruta_manual_esc, 'r')
	
	escfile = open(ruta_manual_esc, 'r')
	esconf = escfile.readline().split('-')
	escfile.close()
	
	esc_init_time, esc_end_time = esconf[1], esconf[2]
	track_delta_time = timedelta(hours=int(np.int64(input_data['Model']['hora_inicio']))) #time_init
	track_init_time = datetime(*[np.int64(x) for x in esc_init_time.split('/')[::-1]]) + track_delta_time
	t0 = time_model.t_hour if time_init is None else time_init
	time = t0
	t1 = time_model_next.t_hour
	# print("Intervalo desde: " + str(t0) + " hasta " + str(t1))
	if t0 <= time_end:
		if t1 <= time_end:
			print("> Processing time step: " + Bcolors.UNDERLINE + str(t0) + " --> " + str(t1) + Bcolors.ENDC + ' ...')
		else:
			print("> Processing time step: " + Bcolors.UNDERLINE + str(t0) + " --> " + str(time_end) + Bcolors.ENDC + ' ...')
	# if t0 == 18:
	#  print "llego"
	
	time_lost = np.zeros(xx.shape)
	# expand = np.array([])
	
	# TODO ajustar coeficientes dif, k1 y k2 ???
	g, k2, k1, difusion = 9.78, 1.45, 1.14, -1
	if peso == 'api':
		valor_peso = 141.5 / (valor_peso + 131.5) * 1000
	tt1 = 2.617 * pow((volumen * densidad / (g * viscosidad * (
		densidad - valor_peso))), 1. / 3.)
	tt2 = 0.397 * (densidad * (pow(volumen, 2 / 3.)) / coef_tension) * pow(
		(g * viscosidad * (densidad - valor_peso) / densidad), 1. / 3.)
	
	exp = None
	valid_index = min(3, time_model.xyuv.shape[1] - 1)
	curr_u = time_model.xyuv[:, valid_index]
	valid_index = min(4, time_model.xyuv.shape[1] - 1)
	curr_v = time_model.xyuv[:, valid_index]
	if time_model.wind is not None:
		wind_u = time_model.wind[:, 3]
		wind_v = time_model.wind[:, 4]
	valid_index = min(3, time_model.xyuv.shape[1] - 1)
	curr_u = time_model.xyuv[:, valid_index]
	valid_index = min(4, time_model.xyuv.shape[1] - 1)
	curr_v = time_model.xyuv[:, valid_index]
	if time_model.temp is not None:
		temp = time_model.temp[:, 3]
	
	flag = False
	while t0 < t1 and t0 <= time_end:
		#        comenzando por la etapa 1 de expansion
		
		# arr_lost = None
		j = grid.trap_finder(xx, yy)
		try:
			j = np.atleast_1d(j)  # Asegura que j sea al menos 1D
			indices_validos = np.where(j != -1)[0]

			if indices_validos.size == 0:
				print('Todas las partículas salen del dominio')
				break

			igood = indices_validos[0] if indices_validos.size == 1 else indices_validos

		except IndexError:
			print('Todas las particulas salen del dominio')
			break
		
		jnan = np.where(j == -1)[0]
		tnow = t0 - tinit2 + (dtsecs / 3600)
		
		if xx.size == 1:
			if ((tt1 < tnow <= tt2 or np.float64(input_data['Model']['profundidad_p']) > 0) and not entro_expand) or bool_sat:
				# descomposicion de la particula en principio nele
				if np.float64(input_data['Model']['profundidad_p']) > 0 and not entro_expand:
					r = radio_v
				else:
					
					r = (k2 * (
						g * (volumen ** 2) * (tnow ** (3 / 2.)) * (densidad - valor_peso) / (
						densidad * (viscosidad ** (1 / 2.)))) ** (1 / 6.)) * 1000
				entro_expand = True
				
				# exp_xx, exp_yy = xx, yy
				exp_texp = time - tinit2
				exp = expand.Expand(xx, yy, r, 1, time_lost, j, exp_texp)
				
				# new descompos
				r_part = input_data['Scenario']['r_particula']
				if bool_sat:
					r_part /= 111000
					
					xx, yy = descomponer.decom2(files_poligon, 2 * r_part)
					nele = np.size(xx)
					volumen = nele * 4 * np.pi * r_part ** 3 / 3
				else:
					xx, yy = descomponer.decom1(grid.trap_finder, xx, yy, r, 2 * r_part)
					nele = np.size(xx)
				
				flag = True
				arr_lost = np.array([])
				difusion = np.pi * (k2 ** 2) / 32 * (
						((densidad - valor_peso) * g * (volumen ** 2)) / densidad * (viscosidad ** (1 / 2.)))
			
			elif tnow <= tt1 and not np.float(input_data['Model']['profundidad_p']) > 0:
				
				# aumento del radio de la 1ra particula en dependencia del tiempo
				r = (k1 / 2. * pow(
					(g * volumen * pow(tnow, 2) * (densidad - valor_peso) / densidad),
					1 / 4.)) * 1000
				
				
		if igood.size == 1 and igood == 0:
			xgood, ygood, jgood = xx, yy, j
		elif igood.size >= 1:
			if jnan.size > 0:
				# print jnan
				# arr_lost = np.append(arr_lost, out_list[-1].arr_tracks[jnan, :], axis=0)
				arr_lost = out_list[-1].arr_tracks[jnan, :]
			# else:
			xgood, ygood, jgood = xx[igood], yy[igood], j[igood]
		if igood.size == 0:
			break
		if input_data['Model']['numeric_schema'] == 'rk2':
			xnext, ynext, jnext = track.Track(grid, jgood, xgood, ygood, time_model, time_model_next, t0, dtsecs,
			                                difusion)
		elif input_data['Model']['numeric_schema'] == 'rk4':
			xnext, ynext, jnext = rks.trackRks(grid, jgood, xgood, ygood, t0, difusion, escenary, dt=3600)
		elif input_data['Model']['numeric_schema'] == 'rk1':
			xnext, ynext, jnext = rks.trackRks1(grid, jgood, xgood, ygood, t0, difusion, escenary, dt=3600)
		else:
			raise ValueError('wrong numeric schema')
		
		# actualizar los datos
		if entro_expand:
			r = input_data['Scenario']['r_particula']
			
			density = np.zeros(shape=(nele))
			waveh = np.zeros(shape=(nele))
			thickness = np.zeros(shape=(nele))
			volevap = np.zeros(shape=(nele))
			voldisp = np.zeros(shape=(nele))
			oilrho = np.zeros(shape=(nele))
			oilvis = np.zeros(shape=(nele))
			waterc = np.zeros(shape=(nele))
			masscenter = np.array([.0, .0])
			cele = 0
			jm = grid.trap_finder(xnext, ynext)
			for i in np.arange(xnext.size):
				if oilweath is not None:
					ind_wind = np.where(np.abs(np.abs(grid.trap_finder._triangulation.x) - np.abs(xnext[i])) ==
					                    np.min(np.abs(np.abs(grid.trap_finder._triangulation.x) - np.abs(xnext[i]))))
					oilweath.SetEnvironment(np.sqrt(wind_u[ind_wind[0][0]] ** 2 + wind_v[ind_wind[0][0]] ** 2),
					                        temp[ind_wind])
					density[i] = oilweath.getDensity()
					waveh[i] = oilweath.getWave()
					thickness[i] = oilweath.getThickness()
					volevap[i] = oilweath.getVolEvap()
					voldisp[i] = oilweath.getVolNatDisp()
					oilrho[i] = oilweath.getDensity()
					oilvis[i] = oilweath.getViscosity()
					waterc[i] = oilweath.getWaterCont()
				
				if jm[i] != -1:
					masscenter += np.array([xnext[i], ynext[i]])
					cele += 1
			
			# r = (k2 * (g * (volumen ** 2) * (tnow ** (3 / 2.)) * (densidad - valor_peso) /(densidad * (viscosidad ** (1 / 2.)))) ** (1 / 6.)) * 1000
			masscenter /= cele
			# geomcenter =
		else:
			if oilweath is not None:
				ind_wind = np.where(np.abs(np.abs(grid.trap_finder._triangulation.x) - np.abs(xnext)) ==
				                	np.min(np.abs(np.abs(grid.trap_finder._triangulation.x) - np.abs(xnext))))
				oilweath.SetEnvironment(np.sqrt(wind_u[ind_wind[0][0]] ** 2 + wind_v[ind_wind[0][0]] ** 2),
				                    	temp[ind_wind])
				density = oilweath.getDensity()
				waveh = oilweath.getWave()
				thickness = oilweath.getThickness()
				volevap = oilweath.getVolEvap()
				voldisp = oilweath.getVolNatDisp()
				oilrho = oilweath.getDensity()
				oilvis = oilweath.getViscosity()
				waterc = oilweath.getWaterCont()
			masscenter = np.array([xnext, ynext])
			# geomcenter = np.column_stack((xnext, ynext))
		if oilweath is not None:
			out_obj = out.OutDataClass(track_init_time, t1, t0, np.column_stack((xnext, ynext)),
									np.column_stack((curr_u, curr_v)),
									arr_lost,
									temp, np.column_stack((wind_u, wind_v)), np.column_stack((corr_u, corr_v)),
									density,
									waveh, thickness, volevap, voldisp, oilrho, oilvis, waterc,
									radio=r, masscenter=masscenter)
		elif time_model.wind is not None:
			out_obj = out.OutDataClass(track_init_time, t1, t0, np.column_stack((xnext, ynext)),
									np.column_stack((curr_u, curr_v)),
									arr_lost,
									None, np.column_stack((wind_u, wind_v)), np.column_stack((corr_u, corr_v)),
									None, None, None, None,
									None, None, None, None,
									radio=r, masscenter=masscenter)
		elif time_model.temp is not None:
			corr_u = np.array([])
			corr_v = np.array([])
			out_obj = out.OutDataClass(track_init_time, t1, t0, np.column_stack((xnext, ynext)),
									np.column_stack((curr_u, curr_v)),
									arr_lost,
									temp, None, np.column_stack((corr_u, corr_v)),
									None, None, None, None,
									None, None, None, None,
									radio=r, masscenter=masscenter)
		else:
			out_obj = out.OutDataClass(track_init_time, t1, t0, np.column_stack((xnext, ynext)),
									np.column_stack((curr_u, curr_v)),
									arr_lost,
									None, None, np.column_stack((corr_u, corr_v)),
									None, None, None, None,
									None, None, None, None,
									radio=r, masscenter=masscenter)
		if oilweath is not None:
			oilweath.Step(3600 * dt)
		out_list.append(out_obj)
		del out_obj
		arr_lost = np.array([])
		(xx, yy, j) = (
		xnext, ynext, jnext)  # if xnext.size != 1 else (np.array([xnext]), np.array([ynext]), np.array([jnext]))
		# xx, yy = xnext, ynext
		# jnan = np.where(j == -1)[0]
		t0 += dt
		
		# TODO: The following (if) does not have any sense! I commented it
		# if t0 == t1 and exp is None and not entro_expand:
		#     print('Terminando intervalo ' + str(t0) + 'hasta' + str(t1))
	
	# TODO: The following (if) does not have any sense! I commented it
	
	# if salto_interv_tiempo:
	#     print('Terminando intervalo ' + str(time_model.t_hour) + ' hasta ' + str(time_model_next.t_hour))
	# else:
	#     print('Terminando intervalo ' + str(time_model.t_hour) + ' hasta ' + str(time_model_next.t_hour))
	return entro_expand, exp, out_list, nele, flag
