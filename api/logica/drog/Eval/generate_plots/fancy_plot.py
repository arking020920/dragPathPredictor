__author__ = 'carlosr'

import os
import matplotlib.pyplot as plt
import numpy as np
import scipy.interpolate as sci
from ..Generic import GenericFunctions as gen
from ..generate_plots.simple_all import fill_shp
from mpl_toolkits.basemap import Basemap
from petromar import geo_dir


def fancy_plot(out_list=None, path=None, zone=None):
    nodes = np.loadtxt(os.path.join(geo_dir, zone, zone + '.nod'))
    # nodes = np.loadtxt(os.path.join(geo_dir, zone, zone + '.nod'))
    nlats, nlons = gen.Xy2Ll(nodes[:, 1], nodes[:, 2], 19.747526, -85.766569)

    fig = plt.figure(figsize=(16, 9), dpi=255)
    plt.title('Posicion temporal de la mancha')
    ax = plt.subplot(111)
    mapa = Basemap(llcrnrlon=nlons.min(), llcrnrlat=nlats.min(), urcrnrlon=nlons.max(), urcrnrlat=nlats.max(),
                   projection='merc', resolution=None, ax=ax, fix_aspect=True)

    nx, ny = mapa(nlons, nlats)
    mapa.drawmapboundary(linewidth=0.0, fill_color='#f0f0f0')
    mapa.drawmeridians(np.linspace(nlons.min(), nlons.max(), 10), labels=[0, 0, 0, 1], color='#969696', fontsize=12)
    mapa.drawparallels(np.linspace(nlats.min(), nlats.max(), 10), labels=[1, 0, 0, 0], color='#969696', fontsize=12)
    mapa.drawmapscale(nlons.max() - 0.7, nlats.min() + 0.4,
                      nlons.max(), nlats.min(), 100,
                      barstyle='fancy', labelstyle='simple',
                      fillcolor1='w', fillcolor2='#555555',
                      zorder=5)
    mapa.readshapefile('./petromar/generate_plots/shp/cuba_dpa', 'cub', drawbounds=True, linewidth=0.5, color='#bdbdbd')
    fill_shp(mapa.cub_info, mapa.cub, '', ax=ax)

    for idx, tr in enumerate(out_list):
        tr_lats, tr_lons = gen.Xy2Ll(tr.arr_tracks[:, 0], tr.arr_tracks[:, 1], 19.747526, -85.766569)
        xtr, ytr = mapa(tr_lons, tr_lats)

        # Plotting the mass center
        try:
            masslat, masslon = gen.Xy2Ll(np.array([tr.masscenter[0]]), np.array([tr.masscenter[1]]), 19.747526,
                                         -85.766569)
            masslon, masslat = mapa(masslon, masslat)
            if idx == 0:
                plt.plot(masslon, masslat, 'og', zorder=5, markersize=2)
            elif idx == out_list.__len__() - 1:
                plt.plot(masslon, masslat, 'ob', zorder=5, markersize=2)
            else:
                plt.plot(masslon, masslat, 'ok', zorder=5, markersize=2)
        except:
            pass

        # Plotting Data fill and oil dispersion
        corr = tr.arr_corr
        wind = tr.arr_wind

        lats_array = np.linspace(nlats.min(), nlats.max(), 38)
        lons_array = np.linspace(nlons.min(), nlons.max(), 38)
        xx, yy = np.meshgrid(lons_array, lats_array)
        lons_arraym, lats_arraym = mapa(xx, yy)
        corr_int = sci.griddata((nlons,nlats), corr, (xx, yy), method='linear')
        wind_int = sci.griddata((nlons, nlats), wind, (xx, yy), method='linear')
        t = mapa.scatter(xtr, ytr, marker='o', color='#a4a6a7', zorder=1)
        p = 5
        corr_quiver = mapa.quiver(lons_arraym, lats_arraym, corr_int[:, :, 0], corr_int[:, :, 1], color='blue',
                                      width=0.001,  scale = 1 / 0.016)
        ck = plt.quiverkey(corr_quiver, 0.9, 0.9, 2, r'$Corriente$', labelpos='E',
                           coordinates='figure')

        wind_quiver = mapa.quiver(lons_arraym[::p, ::p], lats_arraym[::p, ::p], wind_int[::p/10, ::p, 0], wind_int[::p, ::p, 1],
                                  color='black', width=0.0024, scale=1 / 0.0055)
        wk = plt.quiverkey(wind_quiver, 0.9, 0.85, 2, r'$Viento$', labelpos='E',
                           coordinates='figure')
        plt.savefig(path + '/images/Fancy_Plot_{0} .png'.format(idx))
        wk.remove()
        ck.remove()
        corr_quiver.remove()
        wind_quiver.remove()



    print 'END fancy_plot'