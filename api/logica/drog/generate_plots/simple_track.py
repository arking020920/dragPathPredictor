# -*- coding: utf-8 -*-

__author__ = 'Lic. Ivan D.P, M.Sc. Dayron Ch.D. & Amilcar C.E., Project PETROMAR-3D. ' \
             'CMM, INSMET. 2018 - 2021.'

import os

import numpy as np
import matplotlib

import scipy.interpolate as sci
import numpy.ma as ma


#from petromar.BlowOut.bubble_class_tester import input_data

matplotlib.use('Agg')
#from simplekml import kml
from datetime import timedelta

from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from mpl_toolkits.basemap import Basemap
from Generic import paths
from Generic import GenericFunctions as gen
from Generic.ColorController import Bcolors

COLORS = ['black',
          'grey',
          'red']
#          'brown']

CAPTIONS = ['Mass Center',
            u'Slick area',
            'Contact with shoreline']
#                'Spill location']

def fill_shp(sph_info, sph_data, pro='', ax=None):
    """
    rellena los poligonos del shapefile
    """
    patches = []
    patchesin = []

    for info, shape in zip(sph_info, sph_data):
        #if info['PROVINCIA'] != pro:
        if info['SIGLA'] != pro:
            patches.append(Polygon(np.array(shape), True))
        else:
            patchesin.append(Polygon(np.array(shape), True))

    ax.add_collection(PatchCollection(patches, facecolor='#52be80', edgecolor='k', linewidths=1., zorder=1))
    ax.add_collection(PatchCollection(patchesin, facecolor=None, edgecolor='k', linewidths=0.3, zorder=1))

def simple_track(out_list=None, path=None, zone=None, legend_indicators=None):
    #  ADVISORY: This plotter assume that all time-steps of the results yielded by Petromar-3D have a step delta
    #            time of 1 hour!
    InitialX_coord = 0
    InitialY_coord = 0
    # load the mesh nodes from the .nod file in the Geodata folder of Petromar-3D
    nodes = np.loadtxt(os.path.join(paths.geo_dir(),zone,zone+'.nod'))

    # Convert nodes from xy Petromar-3D format into latitude-longitude
    nlats, nlons = gen.Xy2Ll(nodes[:, 1], nodes[:, 2], 19.747526, -85.766569)

    # This datetime index will be used for the name of each plot.
    datetime_index = out_list[0].time_init + timedelta(hours=1)
    #gen.lahora = gen.lahora + timedelta(hours=1)
    #time_dif = datetime_index - gen.lahora

    
    # Plomarker_sizet settings
    lim_max = np.max(nlons)
    lim_min = np.min(nlons)
    
    fig_size_inch = (16,16*(np.max(nlats)-np.min(nlats))/(np.max(nlons)-np.min(nlons)))
    fig_ppi = 600

    #time_seconds = datetime_index.seconds - out_list.time_init.seconds

    # Iterating by all time intervals. particles_tk represents the particles at the time k.
    for particles_tk in out_list:
        # Create the figure
        #import simplekml

        #kml_file = kml.Kml()
        plt.figure(figsize=fig_size_inch, dpi=fig_ppi)
        ax = plt.subplot(111)

        # Preparing the canvas for the map setting up their boundaries and the projection in which it will be displayed.
        mapa = Basemap(llcrnrlon=nlons.min(), llcrnrlat=nlats.min(), urcrnrlon=nlons.max(), urcrnrlat=nlats.max(),
                       projection='merc', resolution='h', fix_aspect=True)

        # Painting the map elements
        mapa.drawmapboundary(fill_color='aqua')
        mapa.fillcontinents(color='coral', lake_color='aqua')
        mapa.drawmeridians(np.arange(int(nlons.min()), nlons.max()), labels=[0, 0, 0, 1],
                           color='#969696', fontsize=12)
        mapa.drawparallels(np.arange(int(nlats.min()), nlats.max()), labels=[1, 0, 0, 0],
                           color='#969696', fontsize=12)
        #plt.grid(True)
        #mapa.plot(lons_arraym, lats_arraym, marker='o', color='r')

        # Drawing date, logo and others in the map (*** rehubicar en 106***)
        plt.suptitle('OIL SLICK DRIFT', fontsize = 18)
        #plt.title('PETROMAR-3D v2.1G', loc = 'right', fontsize=18, color = 'brown')
        plt.text(mapa.xmin, mapa.ymax, str(datetime_index), fontsize=16, color='black')
        plt.text(mapa.xmin+500000, mapa.ymax-90000, 'PETROMAR-3D v2.1G', fontsize=18, color='brown')

        # Drawing the scale of the map
        try:
            mapa.drawmapscale(nlons.max() - 0.7, nlats.min() + 0.4,
                              nlons.max(), nlats.min(), 100,
                              barstyle='fancy', labelstyle='simple',
                              fillcolor1='w', fillcolor2='#555555', zorder=10)
        except:
            print (Bcolors.WARNING + "WARNING: Map scale will not be drawn because a runtime error!" + Bcolors.ENDC)

        # Getting the latitude and longitude of the particles at time k from the Petromar-3D xy format
        particles_lats, particles_lons = gen.Xy2Ll(particles_tk.arr_tracks[:, 0], particles_tk.arr_tracks[:, 1],
                                                   19.747526, -85.766569)

        #print particles_lats, particles_lons
        # Getting the xy position of particles over the canvas cartesian space
        xf = []
        yf = []
        #Ecuacion que garantiza que vaya incrementando el radio antes de descomponer la mancha en particulas
        #r_int = r_int + int(particles_tk.radio)
        #time_dif = datetime_index - gen.lahora
        #control = datetime.timedelta(hours= gen.time_control_tnow)

        """if time_dif <= control:
            xf, yf = gen.Create_Points(gen.lon_initial, gen.lat_initial, r_int, kml_file, datetime_index)
            #print 'Corriendo adentro', gen.time_control_tnow

        else:
            #print 'Corriendo afuera', gen.time_control_tnow
            for i in range(0,len(particles_lons)):
                if gen.poligonos(particles_lons[i], particles_lats[i]) == True:
                    xf.append(particles_lons[i])
                    yf.append(particles_lats[i])
                    lonlat = particles_lons[i], particles_lats[i]
                    pto = kml_file.newpoint(name='', coords=[lonlat])
                    pto.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/pal4/icon49.png'
                    pto.style.iconstyle.scale = 2"""

        map_particles_x, map_particles_y = mapa(particles_lons, particles_lats)
        #lonxlony = np.column_stack(xf, yf)
        #gen.kml_variable(xf, yf, time_dif)
        #map_particles_x, map_particles_y = mapa(xf, yf)
        import matplotlib.patches as pts

        # Deciding the radio and color that each particle will be drawn

        # Viene el cálculo para las 2 primeras horas

        #if particles_tk.radio is not None:
        if map_particles_x.size == 1:
            mancha = pts.Circle((map_particles_x ,map_particles_y),
                                particles_tk.radio, facecolor='k', zorder=2)
            plt.gca().add_artist(mancha)

        else:
            for map_part_x, map_part_y in zip(map_particles_x, map_particles_y):
                mancha = pts.Circle((map_part_x ,map_part_y), particles_tk.radio, facecolor='k', zorder=2)
                plt.gca().add_artist(mancha)



        # Drawing the center of mass of particles
        if len(particles_tk.masscenter.shape) == 2:
            masslats, masslons = gen.Xy2Ll(np.array([particles_tk.masscenter[0][0]]),
                                           np.array([particles_tk.masscenter[1][0]]), 19.747526,
                                           -85.766569)
            masslons, masslats = mapa(masslons, masslats)
            # plt.plot(masslons, masslats, 'ok', zorder=5, markersize=5)
            #print datetime_index, 'segundo if'
        else:
            masslats, masslons = gen.Xy2Ll(np.array([particles_tk.masscenter[0]]),
                                           np.array([particles_tk.masscenter[1]]), 19.747526,
                                           -85.766569)
            masslons, masslats = mapa(masslons, masslats)
            #print ('Tiempo transcurrido', particles_tk.arr_uv.current_time)

             #plt.plot(masslons, masslats, 'ok', zorder=5, markersize=5)
            #print datetime_index, 'else segundo if'

        # Drawing the particles which are for some reason out of the domain (over land or in the boundary).
        if particles_tk.arr_lost.size > 0:
            lost_lats, lost_lons = gen.Xy2Ll(particles_tk.arr_lost[:, 0], particles_tk.arr_lost[:, 1], 19.747526,
                                             -85.766569)
            xlosts, ylosts = mapa(lost_lons, lost_lats)
            #mapa.scatter(xlosts, ylosts, marker='o', color='#bdbdbd', s=100, zorder=3)
            mapa.scatter(xlosts, ylosts, marker='o', color='red', s=100, zorder=3)

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
        
        print ('%s_simpletrack.png' % (datetime_index.strftime('%Y%m%d-%H%M'),))

        # Saving the result to the disk specifying the name based on the corresponding time-step datetime.
        plt.savefig('%s/images/%s_simpletrack.png' % (path, datetime_index.strftime('%Y%m%d-%H%M')))
        #print '%s_simpletrack.kml' % (datetime_index.strftime('%Y%m%d-%H%M'),)
        #kml_file.save('%s/images/%s_simpletrack.kml' % (path, datetime_index.strftime('%Y%m%d-%H%M')))


        # Incrementing the datetime
        datetime_index += timedelta(hours=1)
        print(datetime_index)
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
