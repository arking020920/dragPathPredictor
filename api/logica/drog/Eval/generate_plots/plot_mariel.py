# -*- coding: utf-8 -*-
__author__ = 'ivand'

import numpy as np
import numpy as np
from matplotlib.colors import ListedColormap
from matplotlib.patches import Polygon, PathPatch
from matplotlib.collections import PatchCollection
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from mpl_toolkits.basemap import Basemap
from ..Generic import GenericFunctions as gen

colors = ['black',
          'grey',
          'red']


coption = ['Centro de masa',
           u'Área del derrame',
           'Contacto con la costa']


def simple_all(out_list=None, path=None, zone=None):
    nodes = np.loadtxt('./petromar/Geodata/Zones/%s/%s.nod' % (zone, zone))
    nlats, nlons = gen.Xy2Ll(nodes[:, 1], nodes[:, 2], 19.747526, -85.766569)

    count = 0
    for idx, tr in enumerate(out_list):
        fig = plt.figure(figsize=(16, 9), dpi=255)
        ax = plt.subplot(111)

        mapa = Basemap(llcrnrlon=-82.7827495336533, llcrnrlat=23.0039200186729, urcrnrlon=-82.7448096871376, urcrnrlat=23.0207106471062,
                       projection='merc', resolution=None, ax=ax, fix_aspect=True)

        mapa.drawmapscale(nlons.max() - 0.7, nlats.min() + 0.4,
                          nlons.max(), nlats.min(), 100,
                          barstyle='fancy', labelstyle='simple',
                          fillcolor1='w', fillcolor2='#555555',
                          zorder=5)

        image = plt.imread('./petromar/generate_plots/bahia_Mariel/bahia_Mariel.png')
        mapa.imshow(image, origin='upper')
        #mapa.readshapefile('../petromar/generate_plots/shp/cuba_dpa', 'cub', drawbounds=True, linewidth=0.2, color='k')
        #mapa.scatter(nx, ny, s=0.2, color='b')


        # plot normal track
        tr_lats, tr_lons = gen.Xy2Ll(tr.arr_tracks[:, 0], tr.arr_tracks[:, 1], 19.747526, -85.766569)
        xtr, ytr = mapa(tr_lons, tr_lats)

        if tr.radio is not None:
            t = mapa.scatter(xtr, ytr, marker='o', s=1., color='#a4a6a7', zorder=2)
        else:
            t = mapa.scatter(xtr, ytr, marker='o', color='#a4a6a7', zorder=2)
        # plt mass center
        try:
            masslat, masslon  = gen.Xy2Ll(np.array([tr.masscenter[0]]), np.array([tr.masscenter[1]]), 19.747526, -85.766569)
            masslon, masslat = mapa(masslon, masslat)
            if idx == 0:
                plt.plot(masslon, masslat, 'og', zorder=5, markersize=1)
            elif idx == out_list.__len__()-1:
                plt.plot(masslon, masslat, 'ob', zorder=5, markersize=1)
            else:
                plt.plot(masslon, masslat, 'ok', zorder=5, markersize=1)
        except:
            pass
        try:
            masslat, masslon  = gen.Xy2Ll(np.array([tr.masscenter[0]]), np.array([tr.masscenter[1]]), 19.747526, -85.766569)
            masslon, masslat = mapa(masslon, masslat)
            if idx == 0:
                plt.plot(masslon, masslat, 'og', zorder=5, markersize=1)
            elif idx == out_list.__len__()-1:
                plt.plot(masslon, masslat, 'ob', zorder=5, markersize=1)
            else:
                plt.plot(masslon, masslat, 'ok', zorder=5, markersize=1)
        except:
            pass
            # plot las particulas que se pierden del dominio
        if tr.arr_lost.size > 0:
            lost_lats, lost_lons = gen.Xy2Ll(tr.arr_lost[:, 0], tr.arr_lost[:, 1], 19.747526, -85.766569)
            xlost, ylost = mapa(lost_lons, lost_lats)
            s = mapa.scatter(xlost, ylost, marker='o', color='r', s=1, zorder=3)

        # legend 1
        legend1_line2d = list()
        for passo in range(len(colors)):
            legend1_line2d.append(mlines.Line2D([0], [0],
                                                linestyle="none",
                                                marker="o",
                                                alpha=1.,
                                                markersize=15,
                                                markerfacecolor=colors[passo]))

        legend1 = plt.legend(legend1_line2d,
                             coption,
                             numpoints=1,
                             fontsize=16,
                             loc="best",
                             shadow=True)

        plt.gca().add_artist(legend1)

        print 'simpletracksat_'+str(count)+'.png'# % (str(tr.time_init), str(tr.time_end), str(count))
        plt.savefig(path+'/images/simpletracksat_'+str(count)+'.png')

        count += 1
        plt.close()


print 'end2'
