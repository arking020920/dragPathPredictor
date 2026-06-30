# -*- coding: utf-8 -*-
__author__ = 'ivand'

import os
import numpy as np
from matplotlib.colors import ListedColormap
from matplotlib.patches import Polygon, PathPatch
from matplotlib.collections import PatchCollection
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from mpl_toolkits.basemap import Basemap
from ..Generic import GenericFunctions as gen
from petromar import geo_dir
from petromar import shp_dir


def fill_shp(sph_info, sph_data, pro='', ax=None):
    """
    rellena los poligonos del shapefile
    """

    patches = []
    patchesin = []
    for info, shape in zip(sph_info, sph_data):
        if info['PROVINCIA'] != pro:
            patches.append(Polygon(np.array(shape), True))
        else:
            patchesin.append(Polygon(np.array(shape), True))

    ax.add_collection(PatchCollection(patches, facecolor='#bdbdbd', edgecolor='k', linewidths=1., zorder=1))
    ax.add_collection(PatchCollection(patchesin, facecolor=None, edgecolor='k', linewidths=0.3, zorder=1))


colors = ['black',
          'grey',
          'red']


# def attri_color(wave, thickness):
#     colors = {
#         'Centro de masa': 'black',
#         u'Área del derrame': 'grey',
#         'Contacto con la costa': 'red',
#         u'Centro geométrico': 'blue',
#     }
#     if thickness >= 0.0068 and wave <= 3.0:
#         return colors.get('Burn+Mechanical', 'black')
#     elif thickness >= 0.0025 and wave <= 6.8:
#         return colors.get('Mechanical', 'black')
#     elif thickness >= 0.0025 and wave >= 6.8:
#         return colors.get('Dispersant', 'black')
#     elif thickness < 0.0025:
#         return colors.get('nada', 'black')


coption = ['Centro de masa',
           u'Área del derrame',
           'Contacto con la costa']


def simple_track(out_list=None, path=None, zone=None):
    nodes = np.loadtxt(os.path.join(geo_dir, zone, zone + '.nod'))
    nlats, nlons = gen.Xy2Ll(nodes[:, 1], nodes[:, 2], 19.747526, -85.766569)

    count = 0

    for tr in out_list:

        fig = plt.figure(figsize=(16, 9), dpi=255)
        ax = plt.subplot(111)
        mapa = Basemap(llcrnrlon=nlons.min(), llcrnrlat=nlats.min(), urcrnrlon=nlons.max(), urcrnrlat=nlats.max(),
                       projection='merc', resolution=None, ax=ax, fix_aspect=True)

        nx, ny = mapa(nlons, nlats)
        mapa.drawmapboundary(linewidth=0.0, fill_color='#f0f0f0')
        mapa.drawmeridians(np.arange(-90, -70, 0.5), labels=[0, 0, 0, 1], color='#969696', fontsize=12)
        mapa.drawparallels(np.arange(15, 30, 0.5), labels=[1, 0, 0, 0], color='#969696', fontsize=12)
        mapa.drawmapscale(nlons.max() - 0.7, nlats.min() + 0.4,
                          nlons.max(), nlats.min(), 100,
                          barstyle='fancy', labelstyle='simple',
                          fillcolor1='w', fillcolor2='#555555',
                          zorder=5)

        mapa.readshapefile(os.path.join(shp_dir, 'cuba_dpa'), 'cub', drawbounds=True, linewidth=0.5, color='#bdbdbd')
        fill_shp(mapa.cub_info, mapa.cub, '', ax=ax)


        # plot normal track
        tr_lats, tr_lons = gen.Xy2Ll(tr.arr_tracks[:, 0], tr.arr_tracks[:, 1], 19.747526, -85.766569)
        xtr, ytr = mapa(tr_lons, tr_lats)

        #       get thikness and wave h
        colors_reg = list()

        if tr.radio is not None:
            t = mapa.scatter(xtr, ytr, marker='o', color='#555555', s=tr.radio, zorder=2)
        else:
            t = mapa.scatter(xtr, ytr, marker='o', color='#555555', zorder=2)

        # plt mass center
        if len(tr.masscenter.shape) == 2:
            masslat, masslon  = gen.Xy2Ll(np.array([tr.masscenter[0][0]]), np.array([tr.masscenter[1][0]]), 19.747526, -85.766569)
            masslon, masslat = mapa(masslon, masslat)
            plt.plot(masslon, masslat, 'ok', zorder=5, markersize=5)
        else:
            masslat, masslon  = gen.Xy2Ll(np.array([tr.masscenter[0]]), np.array([tr.masscenter[1]]), 19.747526, -85.766569)
            masslon, masslat = mapa(masslon, masslat)
            plt.plot(masslon, masslat, 'ok', zorder=5, markersize=5)
        # plot las particulas que se pierden del dominio
        if tr.arr_lost.size > 0:
            lost_lats, lost_lons = gen.Xy2Ll(tr.arr_lost[:, 0], tr.arr_lost[:, 1], 19.747526, -85.766569)
            xlost, ylost = mapa(lost_lons, lost_lats)
            s = mapa.scatter(xlost, ylost, marker='o', color='r', s=100, zorder=3)

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

        print 'simpletrack_from_%s_to_%s_%s.png' % (str(tr.time_init), str(tr.time_end), str(count))
        plt.savefig('%s/images/simpletrack_from_%s_to_%s_%s.png' % (path, str(tr.time_init), str(tr.time_end), str(count)))

        t.remove()
   #     mass.remove()
        count += 1

        # strplt.remove()

        # plt.clf()
        # plt.cla()
        plt.close()


print 'end2'
