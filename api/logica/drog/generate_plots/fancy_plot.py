import os

__author__ = 'carlosr'

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import scipy.interpolate as sci
from Generic import paths
import matplotlib.lines as mlines
from mpl_toolkits.basemap import Basemap
from Generic import GenericFunctions as gen
import numpy.ma as ma
from datetime import timedelta


COLORS = ['black',
          'grey',
          'red']
#          'brown']

CAPTIONS = ['Mass Center',
            u'Slick area',
            'Contact with shoreline']
#                'Spill location']

def fancy_plot(out_list=None, path=None, zone=None):
    nodes = np.loadtxt(os.path.join(paths.geo_dir(),zone,zone+'.nod'))
    nlats, nlons = gen.Xy2Ll(nodes[:, 1], nodes[:, 2], 19.747526, -85.766569)

    fig_size_inch = (16,16*(np.max(nlats)-np.min(nlats))/(np.max(nlons)-np.min(nlons)))
    fig_ppi = 600

    plt.figure(1, figsize=fig_size_inch, dpi=fig_ppi)
    ax = plt.subplot(111)

    mapa = Basemap(llcrnrlon=nlons.min(), llcrnrlat=nlats.min(), urcrnrlon=nlons.max(), urcrnrlat=nlats.max(),
                   projection='merc', resolution='f')


    nx, ny = mapa(nlons, nlats)
    mapa.shadedrelief()
    mapa.drawmeridians(np.arange(int(nlons.min()), nlons.max()), labels=[0, 0, 0, 1], color='#969696', fontsize=12)
    mapa.drawparallels(np.arange(int(nlats.min()), nlats.max()), labels=[1, 0, 0, 0], color='#969696', fontsize=12)
    mapa.drawmapscale(nlons.max() - 0.7, nlats.min() + 0.4,
                      nlons.max(), nlats.min(), 100,
                      barstyle='fancy', labelstyle='simple',
                      fillcolor1='w', fillcolor2='#555555',
                      zorder=5)

    for idx, tr in enumerate(out_list):
        datetime_index = out_list[0].time_init + timedelta(hours=1)
        # Drawing date, logo and others in the map (*** rehubicar en 106***)
        plt.suptitle('OIL SLICK DRIFT', fontsize = 18)
        #plt.title('PETROMAR-3D v2.1G', loc = 'right', fontsize=18, color = 'brown')
        plt.text(mapa.xmin, mapa.ymax, str(datetime_index), fontsize=16, color='black')
        plt.text(mapa.xmin+500000, mapa.ymax-90000, 'PETROMAR-3D v2.3G', fontsize=18, color='brown')
        tr_lats, tr_lons = gen.Xy2Ll(tr.arr_tracks[:, 0], tr.arr_tracks[:, 1], 19.747526, -85.766569)
        xtr, ytr = mapa(tr_lons, tr_lats)

        corr = tr.arr_corr
        # wind = tr.arr_wind
        lats_array = np.linspace(nlats.min(), nlats.max(), 38)
        lons_array = np.linspace(nlons.min(), nlons.max(), 38)

        XX, YY = np.meshgrid(lons_array, lats_array)
        # kml_variable(XX, YY)

        lons_arraym, lats_arraym = mapa(XX, YY)
        corr_int = sci.griddata((nlons, nlats), corr, (XX, YY), method='nearest', fill_value=0.0)

        U = corr_int[:, :, 0]
        V = corr_int[:, :, 1]

        U_mask = ma.masked_where((U < -100) | (U >= 100.0), U)
        V_mask = ma.masked_where((V < -100) | (V >= 100.0), V)


        ax.quiver(lons_arraym, lats_arraym, U_mask, V_mask, color='blue', width=0.001, scale= 20)

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
        # wind = tr.arr_wind

        lats_array = np.linspace(nlats.min(), nlats.max(), 38)
        lons_array = np.linspace(nlons.min(), nlons.max(), 38)
        xx, yy = np.meshgrid(lons_array, lats_array)

        # wind_int = sci.griddata((nlons, nlats), wind, (xx, yy), method='linear')
        mapa.scatter(xtr, ytr, marker='o', color='#a4a6a7', zorder=1)

        # List for the indicators of each entry of the legend
        legend_indicators = []
        # Iterate over the colors predefined above to create the indicators
        for color_idx in range(len(COLORS)):
            # In order to create the indicators a trick is used. An invisible line of 1 node with o shape is specified.
            legend_indicators.append(mlines.Line2D([0], [0],
                                                   linestyle="none",
                                                   marker="o",
                                                   alpha=1.,
                                                   markersize=15,
                                                   markerfacecolor=COLORS[color_idx]))

        # Legend matching all indicators with their correspondent captions.
        """legend = plt.legend(legend_indicators,
                            CAPTIONS,
                            title='Legend',
                            numpoints=1,
                            fontsize=14,
                            loc="lower right",
                            shadow=True)"""

        legend = plt.legend(legend_indicators,
                            CAPTIONS,
                            title='Legend',
                            numpoints=1,
                            fontsize=12,
                            loc="lower left",
                            borderaxespad=0.1,
                            shadow=True)
        #########plt.subplot_adjust(right=0.85)
        #legend2 = plt.legend(loc='lower left')
        # Adding the legend to the canvas
        plt.gca().add_artist(legend)

        plt.savefig(path + '/images/Fancy_Plot_%s .png'%(idx))
        # print "AAA"
        # wk.remove()
        # ck.remove()
        # corr_quiver.remove()
        # wind_quiver.remove()


    plt.title('Posicion temporal de la mancha')
    print('END fancy_plot')