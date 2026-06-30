__author__ = 'frank'


class OutDataClass:

    def __init__(self, time_init, time_end, current_time, arr_tracks, arr_uv, arr_lost, temp=None, wind=None, corr=None,
                 density=None, waveh=None, thickness=None, volevap=None, voldisp=None, oilrho=None, oilvis=None,
                 waterc=None, radio=None, masscenter=None, geomcenter=None):
        self.time_init = time_init
        self.time_end = time_end
        self.current_time = current_time
        self.arr_tracks = arr_tracks
        self.arr_uv = arr_uv
        self.arr_temp = temp
        self.arr_wind = wind
        self.arr_corr = corr
        self.arr_density = density
        self.arr_waveh = waveh
        self.arr_thickness = thickness
        self.arr_volumeEvap = volevap
        self.arr_volumeNatDisp = voldisp
        self.arr_density = oilrho
        self.arr_viscosity = oilvis
        self.arr_WaterCont = waterc
        self.arr_lost = arr_lost
        self.radio = radio
        self.masscenter = masscenter
        self.geomcenter = geomcenter

