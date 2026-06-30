# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
from Generic import GenericFunctions as gen
from Generic import paths
import os

def plot_lost(out_list=None, path=None, zone=None):
    nodes = np.loadtxt(os.path.join(paths.geo_dir(),zone,zone+'.nod'))
    nlats, nlons = gen.Xy2Ll(nodes[:, 1], nodes[:, 2], 19.747526, -85.766569)

    time = np.array([])
    lost = np.array([])
    cant = np.array([])
    sumlost = 0

    #mapa = Basemap(llcrnrlon=nlons.min(), llcrnrlat=nlats.min(), urcrnrlon=nlons.max(), urcrnrlat=nlats.max(),
     #              projection='merc', resolution='c', ax=ax, fix_aspect=True)

    for idx, tr in enumerate(out_list):
        # plot normal track
        # plot las particulas que se pierden del dominio
        time = np.append(time, idx)
        #sumlost += tr.arr_lost.size
        lost = np.append(lost, tr.arr_lost.size)
        cant = np.append(cant, tr.arr_lost.size*np.average(tr.arr_density)*60./802.)

    fig = plt.figure(figsize=(16, 9), dpi=255)
    ax = plt.subplot(111)
    plt.plot(time, lost)
    plt.xlabel('horas')
    plt.ylabel(u'Cant de partículas')

    plt.title('Contacto con la costa')

    print ('simplelost_all.png')# % (str(tr.time_init), str(tr.time_end), str(count))
    plt.savefig(path+'/images/simple_lost.png')

    fig = plt.figure(figsize=(16, 9), dpi=255)
    ax = plt.subplot(111)
    plt.plot(time, cant)
    plt.xlabel('horas')
    plt.ylabel('[kg]')

    plt.title('Contacto con la costa')

    print ('simplelcant_all.png')  # % (str(tr.time_init), str(tr.time_end), str(count))
    plt.savefig(path + '/images/simple_cant.png')
    plt.close()