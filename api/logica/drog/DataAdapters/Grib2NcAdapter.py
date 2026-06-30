__author__ = 'root'
import os

from Generic import GenericFunctions as gen
import numpy as np

from . import Adapter


def BuildMatrices(x,y, variables, path, file_data, date, dir_esc):

    #convierto a un vector 1D
    #Tomar las coordenadas especificas cuando vayamos a arreglar

    latu = variables['LAUV_P0_L1_G0'][:].flatten()
    lonu = variables['LOUV_P0_L1_G0'][:].flatten()
    latv = variables['LAVV_P0_L1_G0'][:].flatten()
    lonv = variables['LOVV_P0_L1_G0'][:].flatten()
    u = (variables['UOGRD_P0_2L105_G0'][:]).flatten()
    v = (variables['VOGRD_P0_2L105_G0'][:]).flatten()







    u, v = u.copy(), v.copy()
    u[np.where(u == 1.00000002e+20)[0]] = 0
    v[np.where(v == 1.00000002e+20)[0]] = 0
    temp_datau = np.column_stack((latu, lonu, u))
    temp_datav = np.column_stack((latv, lonv, v))
    #eliminar las filas de velocidad 1.00000002e+20

    datau = gen.FindMatrixInExtrmes(x,y,temp_datau)
    datav = gen.FindMatrixInExtrmes(x,y,temp_datav)

    np.savetxt(dir_esc + '/temp/' + file_data.split('.')[0] + 'u.txt', datau)
    np.savetxt(dir_esc + '/temp/' + file_data.split('.')[0] + 'v.txt', datav)


class Grib2NcAdapter(Adapter.Adapter):
    def __init__(self,dir_esc, model_type, fecha_inicio, cant_dias, model_name):
        Adapter.Adapter.__init__(self,dir_esc,model_type,fecha_inicio,cant_dias)
        self.model_name = model_name

    def GetMatrix(self, nodes):
        import datetime as dt
        from scipy.io import netcdf

        path = 'Datos/' + self.model_type + '/' + self.model_name[0:len(self.model_name)]
        fecha = dt.datetime.strptime(self.fecha_inicio,'%d/%m/%Y')
        matrix, count = [],0

        if os.path.isdir(path):
            name_files = []
            #bool_missing = False
            x = nodes[:,1]
            y = nodes[:,2]
            y,x = gen.Xy2Ll(x, y, 19.747526,-85.766569)
            if not os.path.isdir(self.dir_esc + '/temp'):
                os.mkdir(self.dir_esc + '/temp')
            count, days = 0, 0
            for file_data in sorted(os.listdir(path)):
            #step = 8 if not bool_missing else 16
                date1 = dt.datetime.strptime(file_data[0:8],'%Y%m%d')
                hour = 0
                if fecha == date1 and days < int(self.cant_dias):
                    datenum = date1.toordinal()
                    ncfile = netcdf.netcdf_file(path + '/' + file_data)
                    variables = ncfile.variables
                    BuildMatrices(x, y, variables, path, file_data, date1, self.dir_esc)
                    count += 3
                else:
                    break
                if count == 24:
                    days += 1
                    count = 0
                    fecha = dt.datetime.fromordinal(datenum + 1)
        name_files = sorted(os.listdir(self.dir_esc + '/temp'))
        fecha_final = dt.datetime.strptime((name_files[-1][0:8]),'%Y%m%d')
        final_day = '0' + str(fecha_final.day) if fecha_final.day < 10 else str(fecha_final.day)
        final_month = '0' + str(fecha_final.month) if fecha_final.month < 10 else str(fecha_final.month)
        fecha_final = final_day + '/' + final_month + '/' + str(fecha_final.year)
        return None, name_files, fecha_final


    def Interpola(self, nodes, destino, name_files, matrix, model_type, dt):
        from scipy import interpolate
        import shutil as sh

        uv_corr = nodes[:,0]
        xnod = nodes[:, 1]
        ynod = nodes[:, 2]
        temp_path = destino + '/temp/'
        for file_data in name_files:
            data = np.loadtxt(temp_path + file_data)
            z = data[:, 2]
            longs, lats = gen.Ll2Xy(data[:, 0], data[:, 1], 19.747526, -85.766569)
            znew = interpolate.griddata(np.column_stack((longs, lats)), z, (xnod, ynod), method='linear', fill_value=999)
            #interp_obj = interpolate.interp2d(longs, lats, z, kind='linear')
            #interp_obj = interpolate.RectBivariateSpline(long, lats, z)


            #znew = interp_obj(xnod, ynod)

            uv_corr = np.column_stack((uv_corr, znew))

        uv_corr = gen.VelInterp_Interm(uv_corr, dt)
        np.savetxt(destino + '/uv_'+model_type+'.txt', uv_corr)
        sh.rmtree(temp_path)






    #def GetModelInNodes(self, nodes, destino, name_files, matrix):
    #    temp_path = destino + '/temp/'
    #    for file_data in name_files:
    #        data = np.loadtxt(temp_path + file_data)
    #    #se hallan los extremos de la nueva matriz
    #        xmin = min(data[:,1])
    #        ymin = min(data[:,0])
    #        xmax = max(data[:,1])
    #        ymax = max(data[:,0])
    #        #nx = ((xmin - xmax) / 0.1325) + 3
    #        #ny = ((ymin - ymax) / 0.0678) + 3
    #        #en realidad es 3 pero probaremos con 4
    #        nx = int(((xmax - xmin) / 0.1325) + 4)
    #        ny = int(((ymax - ymin) / 0.0678) + 4)
    #        #no procede ya q estan en m/s
    #        #data[:,2] = data[:,2] / 100
    #        #implementar un FormarMatrizUV que considere y devuelva solo la u o la v
    #        data = gen.FormarMatrizUorV(nx, ny, data,xmin,ymin,0.1325,0.0678)
    #
    #        sz = data.shape
    #
    #        longs, lats = gen.Ll2Xy(data[1:sz[0],0], (data[0,1:sz[1]]).transpose(), 19.747526, -85.766569)
    #
    #        # se sustituyen las coordenadas planas en las matrices
    #        data[0,1:sz[1]] = longs.transpose()
    #        data[1:sz[0], 0] = lats
    #        np.savetxt(temp_path + file_data, data)
    #    return temp_path







