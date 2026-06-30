__author__ = 'ivand'

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon
from mpl_toolkits.basemap import Basemap

from ..Generic import GenericFunctions as gen


def fill_shp(sph_info,sph_data,pro='',ax=None):
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

def plot2_track(out_list=None,path=None,zone=None):
    nodes = np.loadtxt('./petromar/Geodata/Zones/%s/%s.nod' % (zone, zone))
    nlats, nlons = gen.Xy2Ll(nodes[:,1], nodes[:,2], 19.747526, -85.766569)

    maxi = np.zeros(len(out_list))
    maxii = np.zeros(len(out_list))
    maxiii = np.zeros(len(out_list))
    count = 0
    for i in out_list:
#        maxi[count] = np.max(i.arr_wind[0]**2+i.arr_wind[1]**2)
        maxii[count] = np.max(i.arr_corr[0]**2+i.arr_corr[1]**2)
        maxiii[count] = np.max(i.arr_uv[0]**2+i.arr_uv[1]**2)
        count += 1
#    max_wind = np.max(maxi)
    max_corr = np.max(maxii)
    max_uv = np.max(maxiii)

    count = 1

    for idx, tr in enumerate(out_list):

        fig = plt.figure(figsize=(16,9),dpi=255)
        ax = plt.subplot(111)
        mapa = Basemap(llcrnrlon=nlons.min(), llcrnrlat=nlats.min(), urcrnrlon=nlons.max(), urcrnrlat=nlats.max(),
                        projection='merc', resolution=None, ax=ax, fix_aspect=True)

        nx, ny = mapa(nlons, nlats)
        mapa.drawmapboundary(linewidth=0.0 ,fill_color='#f0f0f0')
        mapa.drawmeridians(np.arange(-90,-70,0.5),labels=[0,0,0,1],color='#969696',fontsize=12)
        mapa.drawparallels(np.arange(15,30,0.5),labels=[1,0,0,0],color='#969696',fontsize=12)
        mapa.drawmapscale(nlons.max()-0.7, nlats.min()+0.4,
                      nlons.max(), nlats.min(), 100,
                      barstyle='fancy',labelstyle='simple',
                      fillcolor1='w', fillcolor2='#555555',
                      zorder=5)

        mapa.readshapefile('./petromar/generate_plots/shp/cuba_dpa', 'cub', drawbounds=True, linewidth=0.5, color='#bdbdbd')
        fill_shp(mapa.cub_info,mapa.cub,'',ax=ax)


        #plot normal track
        tr_lats, tr_lons  = gen.Xy2Ll(tr.arr_tracks[:, 0], tr.arr_tracks[:, 1], 19.747526, -85.766569)
        xtr, ytr = mapa(tr_lons, tr_lats)
        if tr.radio is not None:
            t = mapa.scatter(xtr, ytr, marker='o', s=tr.radio, color='#555555', zorder=2)
        else:
            t = mapa.scatter(xtr, ytr, marker='o', color='#555555', zorder=2)
            # plt mass center
        if len(tr.masscenter.shape) == 2:
            masslat, masslon = gen.Xy2Ll(np.array([tr.masscenter[0][0]]), np.array([tr.masscenter[1][0]]), 19.747526,
                                         -85.766569)
            masslon, masslat = mapa(masslon, masslat)
            if idx == 0:
                plt.plot(masslon, masslat, 'og', zorder=5, markersize=1)
            elif idx == out_list.__len__() - 1:
                plt.plot(masslon, masslat, 'ob', zorder=5, markersize=1)
            else:
                plt.plot(masslon, masslat, 'ok', zorder=5, markersize=1)

        else:
            masslat, masslon = gen.Xy2Ll(np.array([tr.masscenter[0]]), np.array([tr.masscenter[1]]), 19.747526,
                                         -85.766569)
            masslon, masslat = mapa(masslon, masslat)
            if idx == 0:
                plt.plot(masslon, masslat, 'og', zorder=5, markersize=1)
            elif idx == out_list.__len__() - 1:
                plt.plot(masslon, masslat, 'ob', zorder=5, markersize=1)
            else:
                plt.plot(masslon, masslat, 'ok', zorder=5, markersize=1)
                # plot las particulas que se pierden del dominio
        if tr.arr_lost.size > 0:
            lost_lats, lost_lons = gen.Xy2Ll(tr.arr_lost[:, 0], tr.arr_lost[:, 1], 19.747526, -85.766569)
            xlost, ylost = mapa(lost_lons, lost_lats)
            s = mapa.scatter(xlost, ylost, marker='o', color='r', s=1, zorder=3)
#        if count % 2 == 0 and tr.arr_wind.size > 1:
#        speed_wind = np.sqrt(tr.arr_wind[:, 0]**2 + tr.arr_wind[:, 1]**2)
#        u_wind = tr.arr_wind[:, 0]
#        v_wind = tr.arr_wind[:, 1]
#        q = mapa.quiver(nx[::10], ny[::10], u_wind[::10], v_wind[::10], max_wind, scale=None, headlength=5, cmap=plt.cm.Reds, pivot='tip', zorder=1)
#        cbar = mapa.colorbar(q, ax=ax)
#        print 'hour2wind_from_%s_to_%s_%s.png' % (str(tr.time_init), str(tr.time_end), str(count))
#        plt.savefig('%s/images/hour2wind_from_%s_to_%s_%s.png' % (path, str(tr.time_init), str(tr.time_end), str(count)))
#        cbar.remove()
#        q.remove()
#        else:
#        speed = np.sqrt(tr.arr_uv[:, 0] * tr.arr_corr[:, 0] + tr.arr_uv[:, 1] * tr.arr_uv[:, 1])
        u_corr = tr.arr_corr[:, 0]
        v_corr = tr.arr_corr[:, 1]
        q = mapa.quiver(nx[::10], ny[::10], u_corr[::10], v_corr[::10], max_corr, scale=None, headlength=5, cmap=plt.cm.Blues, pivot='tip', zorder=1)
        cbar = mapa.colorbar(q, ax=ax)
        print 'hour2corr_from_%s_to_%s_%s.png' % (str(tr.time_init), str(tr.time_end), str(count))
        plt.savefig('%s/images/hour2corr_from_%s_to_%s_%s.png' % (path, str(tr.time_init), str(tr.time_end), str(count)))
        cbar.remove()
        q.remove()

        u_uv = tr.arr_uv[:, 0]
        v_uv = tr.arr_uv[:, 1]
        q = mapa.quiver(nx[::10], ny[::10], u_uv[::10], v_uv[::10], max_uv, scale=None, headlength=5, cmap=plt.cm.Greens, pivot='tip', zorder=1)
        cbar = mapa.colorbar(q, ax=ax)
        print 'hour2res_from_%s_to_%s_%s.png' % (str(tr.time_init), str(tr.time_end), str(count))
        plt.savefig('%s/images/hour2res_from_%s_to_%s_%s.png' % (path, str(tr.time_init), str(tr.time_end), str(count)))
        cbar.remove()
        t.remove()
        q.remove()
        count += 1

        #strplt.remove()

        #plt.clf()
        #plt.cla()
        plt.close()

print 'end2'