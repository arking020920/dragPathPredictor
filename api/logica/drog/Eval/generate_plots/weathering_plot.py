# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
from ..Generic import GenericFunctions as gen

def plot_thick(out_list=None, path=None, zone=None):

    time = np.array([])
    tick = np.array([])
    sumtick = 0

    fig = plt.figure(figsize=(16, 9), dpi=255)
    ax = plt.subplot(111)
    #mapa = Basemap(llcrnrlon=nlons.min(), llcrnrlat=nlats.min(), urcrnrlon=nlons.max(), urcrnrlat=nlats.max(),
     #              projection='merc', resolution='c', ax=ax, fix_aspect=True)

    for idx, tr in enumerate(out_list):
        # plot normal track
        # plot las particulas que se pierden del dominio
        time = np.append(time, idx)
        tick = np.append(tick, np.average(tr.arr_thickness))

    plt.plot(time[1:], tick[1:])
    plt.xlabel('horas')
    plt.ylabel('[m]')

    plt.title('Grosor superficial')
    print 'simpletick_all.png'# % (str(tr.time_init), str(tr.time_end), str(count))
    plt.savefig(path+'/images/simple_tick.png')

    plt.close()

#def plot_conc(vol, out_list=None, path=None, zone=None ):
def plot_conc(vol, out_list=None, path=None):

    time = np.array([])
    conc = np.array([])
    sumtick = 0

    fig = plt.figure(figsize=(16, 9), dpi=255)
    ax = plt.subplot(111)
    #mapa = Basemap(llcrnrlon=nlons.min(), llcrnrlat=nlats.min(), urcrnrlon=nlons.max(), urcrnrlat=nlats.max(),
     #              projection='merc', resolution='c', ax=ax, fix_aspect=True)

    for idx, tr in enumerate(out_list):
        # plot normal track
        # plot las particulas que se pierden del dominio
        if tr.radio is not None:
            time = np.append(time, idx)
            conc = np.append(conc, np.average(tr.arr_density)*vol/(tr.radio**2*np.pi))
    plt.plot(time[1:], conc[1:])
    plt.xlabel('horas')
    plt.ylabel('[kg/km**2]')

    plt.title(u'Concentracion superficial')

    print 'simpleconc_all.png'# % (str(tr.time_init), str(tr.time_end), str(count))
    plt.savefig(path+'/images/simple_conc.png')

    plt.close()
print 'end2'