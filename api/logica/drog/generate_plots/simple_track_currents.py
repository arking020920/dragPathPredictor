# -*- coding: utf-8 -*-

__author__ = 'Lic. Ivan Delgado de la Paz and M.Sc. Dayron Chang Dominguez, Project PETROMAR-3D. ' \
             'CMM, INSMET. 2018 - 2021.'

import numpy as np
import scipy.interpolate as sci
import os
import matplotlib
import numpy.ma as ma
matplotlib.use('Agg')
from datetime import datetime, timedelta
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from matplotlib import ticker, cm
from mpl_toolkits.basemap import Basemap
from Generic import paths
from Generic import GenericFunctions as gen

COLORS = ['black',
          'grey',
          'red']

CAPTIONS = ['Centro de masa',
            u'Área del derrame',
            'Contacto con la costa']



def simple_track(out_list=None, path=None, zone=None):
    #  ADVISORY: This plotter assume that all time-steps of the results yielded by Petromar-3D have a step delta
    #            time of 1 hour!

    # load the mesh nodes from the .nod file in the Geodata folder of Petromar-3D
    shp_dir = paths.shp_dir()
    geo_dir = paths.geo_dir()
    nodes = np.loadtxt(os.path.join(geo_dir, zone, zone + '.nod'))

    # Convert nodes from xy Petromar-3D format into latitude-longitude
    nlats, nlons = gen.Xy2Ll(nodes[:, 1], nodes[:, 2], 19.747526, -85.766569)

    # This datetime index will be used for the name of each plot.
    datetime_index = out_list[0].time_init + timedelta(hours=1)

    # Iterating by all time intervals. particles_tk represents the particles at the time k.
    for particles_tk in out_list:
        # Create the figure
        plt.figure(figsize=(16, 9), dpi=600)
        ax = plt.subplot(111)

        # Preparing the canvas for the map setting up their boundaries and the projection in which it will be displayed.
        mapa = Basemap(llcrnrlon=nlons.min(), llcrnrlat=nlats.min(), urcrnrlon=nlons.max(), urcrnrlat=nlats.max(),
                       projection='merc', resolution=None, ax=ax, fix_aspect=True)

        # Streams Plot

        # Plotting Data fill and oil dispersion
        corr = particles_tk.arr_corr # TODO: Pass the real array of currents from the scenario without the coefs.
        # wind = tr.arr_wind

        lats_array = np.linspace(nlats.min(), nlats.max(), 38)
        lons_array = np.linspace(nlons.min(), nlons.max(), 38)

        XX, YY = np.meshgrid(lons_array, lats_array)

        lons_arraym, lats_arraym = mapa(XX, YY)
        corr_int = sci.griddata((nlons, nlats), corr, (XX, YY), method='linear', fill_value=0.0)

        U = corr_int[:, :, 0]
        V = corr_int[:, :, 1]

        U_mask = ma.masked_where((U < 0) | (U >= 30.0), U)
        V_mask = ma.masked_where((V < 0) | (V >= 30.0), V)

        # speed = np.sqrt(U ** 2 + V ** 2)
        speed = np.sqrt(U_mask ** 2 + V_mask ** 2)

        # corr_quiver = mapa.quiver(lons_arraym, lats_arraym, corr_int[:, :, 0], corr_int[:, :, 1], color='blue',
        #                               width=0.001,  scale = 1 / 0.016)

        cs = ax.contourf(lons_arraym, lats_arraym, speed, cmap='Blues', alpha=0.2,
                         zorder=2) # locator=ticker.LogLocator(),

        lw = 5 * speed / speed.max()
        # ax.streamplot(lons_arraym, lats_arraym, U_mask, V_mask, density=1.0, linewidth=lw, color='k')
        ax.streamplot(lons_array, lats_array, U_mask, V_mask, density=1.0, color='k')
        ax.set_title('Varying Line Width')

        # Painting the map elements
        # mapa.drawmapboundary(linewidth=0.0, fill_color='#f0f0f0')
        mapa.drawmeridians(np.arange(-90, -70, np.abs(mapa.llcrnrlon - mapa.urcrnrlon) / 6.0), labels=[0, 0, 0, 1],
                           color='#969696', fontsize=12)
        mapa.drawparallels(np.arange(15, 30, np.abs(mapa.llcrnrlat - mapa.urcrnrlat) / 6.0), labels=[1, 0, 0, 0],
                           color='#969696', fontsize=12)


        # Drawing the scale of the map
        mapa.drawmapscale(nlons.max() - 0.7, nlats.min() + 0.4,
                          nlons.max(), nlats.min(), 100,
                          barstyle='fancy', labelstyle='simple',
                          fillcolor1='w', fillcolor2='#555555', zorder=10)

        # Getting the latitude and longitude of the particles at time k from the Petromar-3D xy format
        particles_lats, particles_lons = gen.Xy2Ll(particles_tk.arr_tracks[:, 0], particles_tk.arr_tracks[:, 1],
                                                   19.747526, -85.766569)

        # Getting the xy position of particles over the canvas cartesian space
        map_particles_x, map_particles_y = mapa(particles_lons, particles_lats)

        # Deciding the radio and color that each particle will be drawn
        if particles_tk.radio is not None:
            mapa.scatter(map_particles_x, map_particles_y, marker='o', color='#555555', s=particles_tk.radio,
                         zorder=2)
        else:
            mapa.scatter(map_particles_x, map_particles_y, marker='o', color='#555555', zorder=2)

        # Drawing the center of mass of particles
        if len(particles_tk.masscenter.shape) == 2:
            masslats, masslons = gen.Xy2Ll(np.array([particles_tk.masscenter[0][0]]),
                                           np.array([particles_tk.masscenter[1][0]]), 19.747526,
                                           -85.766569)
            masslons, masslats = mapa(masslons, masslats)
            plt.plot(masslons, masslats, 'ok', zorder=5, markersize=5)
        else:
            masslats, masslons = gen.Xy2Ll(np.array([particles_tk.masscenter[0]]),
                                           np.array([particles_tk.masscenter[1]]), 19.747526,
                                           -85.766569)
            masslons, masslats = mapa(masslons, masslats)
            plt.plot(masslons, masslats, 'ok', zorder=5, markersize=5)

        # Drawing the particles with are for some reason out of the domain (over land or in the boundary).
        if particles_tk.arr_lost.size > 0:
            lost_lats, lost_lons = gen.Xy2Ll(particles_tk.arr_lost[:, 0], particles_tk.arr_lost[:, 1], 19.747526,
                                             -85.766569)
            xlosts, ylosts = mapa(lost_lons, lost_lats)
            mapa.scatter(xlosts, ylosts, marker='o', color='r', s=100, zorder=3)

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
        legend = plt.legend(legend_indicators,
                            CAPTIONS,
                            numpoints=1,
                            fontsize=16,
                            loc="best",
                            shadow=True)

        # Adding the legend to the canvas
        plt.gca().add_artist(legend)

        print ('%s_simpletrackcurrents.png' % (datetime_index.strftime('%Y%m%d-%H%M'),))

        # Saving the result to the disk specifying the name based on the corresponding time-step datetime.
        plt.savefig('%s/images/%s_simpletrackcurrents.png' % (path, datetime_index.strftime('%Y%m%d-%H%M')))

        # Incrementing the datetime
        datetime_index += timedelta(hours=1)

        plt.close()


        # !!! Code for waves and thickness !!! #
        #          not completed yet.

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
