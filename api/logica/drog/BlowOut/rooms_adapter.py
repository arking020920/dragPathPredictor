import scipy.io as sio
import numpy as np


class rooms_adapter(object):

    def __init__(self, inputdata, fecha):
        self.fecha = fecha
        a, b, c = self.fecha.split('/')
        self.fecha = c + b + a

    def vars(self):  # TODO fix path
        path = '/home/ivand89/Dev/Petropy_data/Ocean/roms/roms_output_' + self.fecha
        wrfile = sio.netcdf_file(path, 'r')

        lons_temp_u = 360 + np.linspace(-87.68, -87.68 + (545 * 0.028), 545)
        lats_temp_u = np.linspace(18.26, 18.26 + (258 * 0.028), 257)
        lon_m, lat_m = np.meshgrid(lons_temp_u, lats_temp_u)
        nivel_m = [0, 5, 10, 15, 20, 30, 40, 60, 80]

        u_m = wrfile.variables['uz'][0][:, :-1, :]
        v_m = wrfile.variables['vz'][0][:, :, :-1]
        ss = wrfile.variables['saltz'][0][:, :-1, :-1]
        tt = wrfile.variables['tempz'][0][:, :-1, :-1]


        u_m = np.nan_to_num(u_m)
        v_m = np.nan_to_num(v_m)
        tt = np.nan_to_num(tt)
        ss = np.nan_to_num(ss)

        return lat_m, lon_m, nivel_m, u_m, v_m, tt, ss
