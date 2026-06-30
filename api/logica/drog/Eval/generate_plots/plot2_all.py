__author__ = 'ivand'

import os
import numpy as np
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from Generic import GenericFunctions as gen
from Generic.paths import geo_dir
from Generic.paths import shp_dir

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



def plot2_all(out_list=None,path=None,zone=None):
    nodes = np.loadtxt(os.path.join(geo_dir, zone, zone + '.nod'))
    nlats, nlons = gen.Xy2Ll(nodes[:,1], nodes[:,2], 19.747526, -85.766569)

    fig = plt.figure(figsize=(16,9),dpi=255)
    ax = plt.subplot(111)

    mapa = Basemap(llcrnrlon=nlons.min(), llcrnrlat=nlats.min(), urcrnrlon=nlons.max(), urcrnrlat=nlats.max(),
                   projection='merc', resolution=None, ax=ax, fix_aspect=True)
    mapa.drawmapboundary(linewidth=0.0 ,fill_color='#f0f0f0')
    mapa.drawmeridians(np.arange(-90,-70,0.5),labels=[0,0,0,1],color='#969696',fontsize=12)
    mapa.drawparallels(np.arange(15,30,0.5),labels=[0,1,0,0],color='#969696',fontsize=12)
    mapa.drawmapscale(nlons.max()-0.7, nlats.min()+0.4,
                      nlons.max(), nlats.min(), 100,
                      barstyle='fancy',labelstyle='simple',
                      fillcolor1='w', fillcolor2='#555555',
                      zorder=5)

    #mapa.readshapefile('./petromar/generate_plots/shp/cuba_dpa', 'cub', drawbounds=True, linewidth=0.5, color='#bdbdbd')
    mapa.readshapefile(os.path.join(shp_dir, 'cuba_dpa'), 'cub', drawbounds=True, linewidth=0.5, color='#bdbdbd')
    fill_shp(mapa.cub_info,mapa.cub,'',ax=ax)
    all_tracks = np.array([[0, 0]])
    lost_tracks = np.array([[0, 0]])

    for tr in out_list:
        all_tracks = np.concatenate((all_tracks, tr.arr_tracks), axis=0)
        if tr.arr_lost.size > 0:
            lost_tracks = np.concatenate((lost_tracks, tr.arr_lost), axis=0)
     #plot la trayectoria normal
    all_tracks, lost_tracks = all_tracks[1:, :], lost_tracks[1:, :]
    tr_lats, tr_lons = gen.Xy2Ll(all_tracks[1:, 0], all_tracks[1:, 1], 19.747526, -85.766569)
    xtr, ytr = mapa(tr_lons, tr_lats)
    t = mapa.scatter(xtr, ytr, marker='o', color='blue')

    if not lost_tracks.size == 0:
        lost_lats, lost_lons = gen.Xy2Ll(lost_tracks[:, 0], lost_tracks[:, 1], 19.747526, -85.766569)
        xlost, ylost = mapa(lost_lons, lost_lats)
        s = mapa.scatter(xlost, ylost, marker='o', color='red')

    print ("generating all2_tracks.png")
    plt.savefig('%s/images/all2_tracks.png' % path)
    plt.clf()
    plt.cla()
    plt.close()
    return all_tracks, lost_tracks