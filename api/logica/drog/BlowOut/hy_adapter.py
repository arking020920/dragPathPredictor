__author__ = 'carlos'

import scipy.io as sio
import numpy as np


class hy_adap(object):

    def __init__(self, input_data):

        self.fecha = input_data.fecha


    def vars(self):
        path = '../Datos/CORRIENTES/3d_hycom/HYCOM_' + self.fecha
        wrfile = sio.netcdf_file(path,'r')

        lat_m =wrfile.variables['Latitude'][:,:]
        lon_m=wrfile.variables['Longitude'][:,:]
        nivel_m = wrfile.variables['Depth'][0:32]

        u_m = wrfile.variables['u'][0]
        v_m = wrfile.variables['v'][0]
        u_m = np.nan_to_num(u_m)
        v_m = np.nan_to_num(v_m)

        tt = wrfile.variables['temperature'][0]
        tt = np.nan_to_num (tt)
        ss = wrfile.variables['salinity'][0]
        ss = np.nan_to_num (ss)
        return lat_m, lon_m, nivel_m, u_m, v_m, tt, ss
