import cPickle
from datetime import timedelta

import arrow
import numpy as np
import scipy.interpolate as sint
from ..Generic import GenericFunctions as gen
from ..generate_plots import ploteval
from scipy.io import netcdf_file
from unipath import Path


#import  CalculoTrayectoria.out_data_class as out


class DrifterEval(object):

    def __init__(self, driftertype, drifterid, drifterfile, drifpath):
        noaatype = np.dtype(
            [('lat', np.float32), ('lon', np.float32), ('ind', np.int32), ('year', np.int32), ('month', np.int32),
             ('day', np.int32), ('hour', np.int32), ('min', np.int32)])
        noaadata = drifpath + Path('/Drifters/DRIFTERS_NOAA')

        usftype = np.dtype(
            [('ind', np.int32), ('year', np.int32), ('month', np.int32), ('day', np.int32), ('hour', np.int32),
             ('min', np.int32),
             ('sec', np.int32), ('lat', np.float32), ('lon', np.float32), ('sst', np.float32)])
        usfdata = drifpath + Path('./petromar/Datos/Drifters/Drifters_USF')

        self.drifterid = drifterid
        if driftertype == 'noaa':
            self.drifterfile = noaadata+'/'+drifterfile[:4]+'/'+drifterfile
            self.driftertype = noaatype
            self.drifterdata = np.loadtxt(self.drifterfile, dtype=noaatype)
        elif driftertype == 'usf':
            self.drifterfile = usfdata+'/'+drifterfile
            self.driftertype = usftype
            self.drifterdata = np.loadtxt(self.drifterfile, dtype=usftype, skiprows=35)

    @staticmethod
    def loadtrack(scepath, scenario, track):
        escenariopath = scepath
        scenariodata = netcdf_file(escenariopath+'/'+scenario+'/'+scenario+'.nc')
        zone = scenariodata.variables['zone'].name

        trackdata = open(escenariopath+'/'+scenario+'/tracks/'+track+'/save.pk')
        trackdata = cPickle.load(trackdata)
        tracklon = np.zeros(trackdata.__len__())
        tracklat = np.zeros(trackdata.__len__())


        timestart = arrow.get(trackdata[0].time_init)
        timeend = timestart + timedelta(hours=trackdata.__len__())
        tracktime = np.array([])

        for t in arrow.Arrow.range('hour', timestart, timeend):
            tracktime = np.append(tracktime, t.timestamp)
        tracktime = tracktime[:-1]


        for idx, data in enumerate(trackdata):
            tracklon[idx] = data.masscenter[0]
            tracklat[idx] = data.masscenter[1]

        tracklat, tracklon = gen.Xy2Ll(tracklon, tracklat, 19.747526, -85.766569)

        return tracklon, tracklat, tracktime, zone

    def compare(self,scepath, scenario, track, plot=True):
        tracklon, tracklat, tracktime, zone = self.loadtrack(scepath, scenario, track)
        driflon, driflat, driftime = self.normalizer(self.drifterdata, self.drifterid)

        if plot:
            mapa, err, numerr = ploteval.plotmap(driflon, driflat, tracklon, tracklat, driftime, tracktime, zone)
            mapa.savefig(scepath+'/'+scenario+'/tracks/'+track+'/eval.png')
            err.savefig(scepath+'/'+scenario+'/tracks/'+track+'/err.png')
            np.savetxt(scepath+'/'+scenario+'/tracks/'+track+'/numerr.txt', numerr)


    @staticmethod
    def normalizer(drifterdata, drifterid):
        selc_drif = drifterdata[np.where(drifterdata['ind'] == drifterid)]
        time_numeric = np.array([])
        normatime = np.array([])
        for step in selc_drif:
            time = arrow.Arrow(step['year'], step['month'], step['day'], step['hour'], step['min'])
            time_numeric = np.append(time_numeric, time.timestamp)

        normalon = sint.interp1d(time_numeric, selc_drif['lon'], kind='linear', fill_value='extrapolate')
        normalat = sint.interp1d(time_numeric, selc_drif['lat'], kind='linear', fill_value='extrapolate')

        timestart = arrow.Arrow(selc_drif[0]['year'], selc_drif[0]['month'], selc_drif[0]['day'], selc_drif[0]['hour'])
        timeend = arrow.Arrow(selc_drif[-1]['year'], selc_drif[-1]['month'], selc_drif[-1]['day'],
                              selc_drif[-1]['hour'])

        for t in arrow.Arrow.range('hour', timestart, timeend):
            normatime = np.append(normatime, t.timestamp)

        normalon = normalon(normatime)
        normalat = normalat(normatime)
        return normalon, normalat, normatime