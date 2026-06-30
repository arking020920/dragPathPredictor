# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = 'ivand'
import matplotlib.lines as mlines
import matplotlib.pyplot as plt
import numpy as np
import os

from .. import geo_dir
from .. import install_dir
from .. import shp_dir
from ..Generic import GenericFunctions as gen
from matplotlib.collections import PatchCollection
from matplotlib.colors import ListedColormap
from matplotlib.patches import PathPatch
from matplotlib.patches import Polygon
from mpl_toolkits.basemap import Basemap


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


coption = ['Centro de masa',
           u'Área del derrame',
           'Contacto con la costa']


def simple_all(out_list=None, path=None, zone=None):
    nodes = np.loadtxt(os.path.join(geo_dir,zone,zone+'.nod'))
    nlats, nlons = gen.Xy2Ll(nodes[:, 1], nodes[:, 2], 19.747526, -85.766569)

    count = 1

    fig = plt.figure(figsize=(16, 9), dpi=255)
    ax = plt.subplot(111)
    #mapa = Basemap(llcrnrlon=nlons.min(), llcrnrlat=nlats.min(), urcrnrlon=nlons.max(), urcrnrlat=nlats.max(),
     #              projection='merc', resolution='c', ax=ax, fix_aspect=True)
    mapa = Basemap(llcrnrlon=nlons.min(), llcrnrlat=nlats.min(), urcrnrlon=nlons.max(), urcrnrlat=nlats.max(),
                   projection='merc', resolution='i', ax=ax, fix_aspect=True)

    nx, ny = mapa(nlons, nlats)
    mapa.drawcoastlines()
    mapa.drawmapboundary(linewidth=0.0, fill_color='#f0f0f0')
    mapa.drawmeridians(np.linspace(nlons.min(), nlons.max(), 10), labels=[0, 0, 0, 1], color='#969696', fontsize=12)
    mapa.drawparallels(np.linspace(nlats.min(), nlats.max(), 10), labels=[1, 0, 0, 0], color='#969696', fontsize=12)
    mapa.drawmapscale(nlons.max() - 0.7, nlats.min() + 0.4,
                      nlons.max(), nlats.min(), 100,
                      barstyle='fancy', labelstyle='simple',
                      fillcolor1='w', fillcolor2='#555555',
                      zorder=5)
    #mapa.readshapefile(os.path.join(shp_dir, 'cuba_dpa'), 'cub', drawbounds=True, linewidth=0.5, color='#bdbdbd')
    #fill_shp(mapa.cub_info, mapa.cub, '', ax=ax)

    #mapa.scatter(nx, ny)

    count = 0


    for idx, tr in enumerate(out_list):
        # plot normal track
        tr_lats, tr_lons = gen.Xy2Ll(tr.arr_tracks[:, 0], tr.arr_tracks[:, 1], 19.747526, -85.766569)
        xtr, ytr = mapa(tr_lons, tr_lats)


        if tr.radio is not None:
            t = mapa.scatter(xtr, ytr, marker='o', color='#a4a6a7', zorder=2)
        else:
            t = mapa.scatter(xtr, ytr, marker='o', color='#a4a6a7', zorder=2)
        # plt mass center
        try:
            masslat, masslon  = gen.Xy2Ll(np.array([tr.masscenter[0]]), np.array([tr.masscenter[1]]), 19.747526, -85.766569)
            masslon, masslat = mapa(masslon, masslat)
            if idx == 0:
                plt.plot(masslon, masslat, 'og', zorder=5, markersize=2)
            elif idx == out_list.__len__()-1:
                plt.plot(masslon, masslat, 'ob', zorder=5, markersize=2)
            else:
                plt.plot(masslon, masslat, 'ok', zorder=5, markersize=2)
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

    print('simpletrack_all.png')
    plt.savefig(path+'/images/simpletrack_all.png')

    count += 1
    plt.close()
