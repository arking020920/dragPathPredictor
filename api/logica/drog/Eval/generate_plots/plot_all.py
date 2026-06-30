__author__ = 'root'

from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np
from ..Generic import GenericFunctions as gen

def PlotAallTracks(zone, tracks_uv, track_path):
    nodes = np.loadtxt('./petromar/Geodata/Zones/%s/%s.nod' % (zone, zone))
    nlats, nlons = gen.Xy2Ll(nodes[:,1], nodes[:,2], 19.747526, -85.766569)
    m = Basemap(projection='merc', llcrnrlon=nlons.min(), llcrnrlat=nlats.min(), urcrnrlon=nlons.max(), urcrnrlat=nlats.max(),
                resolution='i')
    nx, ny = m(nlons, nlats)
    m.drawcoastlines()
    m.drawmapboundary(fill_color='cyan')
    m.fillcontinents(color='green', lake_color='aqua')
    parallels = np.arange(5., 38, 2.5)
    m.drawparallels(parallels, labels=[False, True, True, False])
    meridians = np.arange(0., 351., 3.)
    m.drawmeridians(meridians, labels=[True, False, False, True])

    all_tracks = np.array([[0, 0]])
    lost_tracks = np.array([[0, 0]])
    for tr in tracks_uv:
        all_tracks = np.concatenate((all_tracks, tr.arr_tracks), axis=0)
        if tr.arr_lost.size > 0:
            lost_tracks = np.concatenate((lost_tracks, tr.arr_lost), axis=0)
        #lats, lons = gen.Xy2Ll(tr.arr_tracks[:, 0], tr.arr_tracks[:, 1], 19.747526, -85.766569)
        #lats, lons = gen.Xy2Ll(tr.arr_tracks[:, 0], tr.arr_tracks[:, 1], 19.747526, -85.766569)
        ##plot la trayectoria normal
        #tr_lats, tr_lons  = gen.Xy2Ll(tr.arr_tracks[:, 0], tr.arr_tracks[:, 1], 19.747526, -85.766569)
        #xtr, ytr = m(tr_lons, tr_lats)
        #t = m.scatter(xtr, ytr, marker='o', color='blue')
        ##plot las particulas que se pierden del dominio
        #if tr.arr_lost.size > 0:
        #    lost_lats, lost_lons = gen.Xy2Ll(tr.arr_lost[:, 0], tr.arr_lost[:, 1], 19.747526, -85.766569)
        #    xlost, ylost = m(lost_lons, lost_lats)
        #    s = m.scatter(xlost, ylost, marker='o', color='red')
    #plot la trayectoria normal
    all_tracks, lost_tracks = all_tracks[1:, :], lost_tracks[1:, :]
    tr_lats, tr_lons = gen.Xy2Ll(all_tracks[1:, 0], all_tracks[1:, 1], 19.747526, -85.766569)
    xtr, ytr = m(tr_lons, tr_lats)
    t = m.scatter(xtr, ytr, marker='o', color='blue')

    if not lost_tracks.size == 0:
        lost_lats, lost_lons = gen.Xy2Ll(lost_tracks[:, 0], lost_tracks[:, 1], 19.747526, -85.766569)
        xlost, ylost = m(lost_lons, lost_lats)
        s = m.scatter(xlost, ylost, marker='o', color='red')

    print "generating all_tracks.png"
    plt.savefig('%s/images/all_tracks.png' % track_path)
    plt.clf()
    plt.cla()
    plt.close()
    return all_tracks, lost_tracks

