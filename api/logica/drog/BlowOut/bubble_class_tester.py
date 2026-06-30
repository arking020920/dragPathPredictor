# -*- coding: utf-8 -*-
"""
Created on Mon May  2 21:27:09 2016

@author: carlosr

Main for the excecution of blowout model
"""

import plot as pplot
import bubble_class as bbc
import ReadCalculaTrayectoria as reader #TODO fix this import: new config parser
import os
import hy_adapter
import rooms_adapter as ra



fullpath = '../'
os.chdir(fullpath + 'CalculoTrayectoria')
input_data = reader.ReadCtConf()
rooms = ra.rooms_adapter(input_data)
lat_m, lon_m, nivel_m, u_m, v_m, tt, ss = rooms.vars()

cv = bbc.OilBubbleTracking(input_data)
cv.StepIntergation(u_m, v_m, tt, ss, nivel_m, lat_m, lon_m)
cv.SaveVar()
lat_in, lon_in, b_in, m_in, d_t = cv.PetromInput()
h_t, b_t, x_t, y_t, z_t, w_t, v_t, u_t, wl_t, vl_t, ul_t, T_t, T_T, dty_def, E = cv.GetVar()



os.chdir(fullpath + 'Datos/Escenarios/' + input_data.nombre_escenario + '/tracks')

"""
pplot.PlotPlume(b_t, x_t, y_t, z_t, w_t, v_t, u_t, E)
pplot.PlotCurves(b_t, x_t, y_t, z_t, w_t, v_t, u_t, wl_t, vl_t, ul_t, T_t, E)
pplot.PLotVelocities(w_t, T_T, x_t, E)
pplot.PlotRadio(b_t, T_T, z_t, E)
pplot.PlotDensity(dty_def, T_T, x_t, E)
pplot.Plotconcentracion(b_t, T_T, E)
pplot.Plotxy(x_t, y_t, z_t, E)

"""
