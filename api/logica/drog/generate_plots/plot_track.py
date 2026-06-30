__author__ = 'root'

from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np
from Generic import GenericFunctions as gen
#import os


def PlotTracks(zone, tracks_uv, track_path, all_tracks, lost_tracks):
    nodes = np.loadtxt('./petromar/Geodata/Zones/%s/%s.nod' % (zone, zone))
    nlats, nlons = gen.Xy2Ll(nodes[:,1], nodes[:,2], 19.747526, -85.766569)

    count = 1
    m = Basemap(projection='merc', llcrnrlon=nlons.min(), llcrnrlat=nlats.min(), urcrnrlon=nlons.max(), urcrnrlat=nlats.max(),
                resolution='i')
    for tr in tracks_uv:
        lats, lons = gen.Xy2Ll(tr.arr_tracks[:, 0], tr.arr_tracks[:, 1], 19.747526, -85.766569)
        nx, ny = m(nlons, nlats)
        m.drawcoastlines()
        m.drawmapboundary(fill_color='cyan')
        m.fillcontinents(color='green', lake_color='aqua')
        parallels = np.arange(5., 38, 2.5)
        m.drawparallels(parallels, labels=[False, True, True, False])
        meridians = np.arange(0., 351., 3.)
        m.drawmeridians(meridians, labels=[True, False, False, True])
        speed = np.sqrt(tr.arr_uv[:, 0] * tr.arr_uv[:, 0] + tr.arr_uv[:, 1] * tr.arr_uv[:, 1])
        u = tr.arr_uv[:, 0] / max(speed)
        v = tr.arr_uv[:, 1] / max(speed)
        #plot normal track
        tr_lats, tr_lons  = gen.Xy2Ll(tr.arr_tracks[:, 0], tr.arr_tracks[:, 1], 19.747526, -85.766569)
        xtr, ytr = m(tr_lons, tr_lats)
        t = m.scatter(xtr, ytr, marker='o', color='blue')
        #plot las particulas que se pierden del dominio
        if tr.arr_lost.size > 0:
            lost_lats, lost_lons = gen.Xy2Ll(tr.arr_lost[:, 0], tr.arr_lost[:, 1], 19.747526, -85.766569)
            xlost, ylost = m(lost_lons, lost_lats)
            s = m.scatter(xlost, ylost, marker='o', color='red', s=100)
        q = m.quiver(nx[::10], ny[::10], u[::10], v[::10], speed, scale=20, headlength=7, cmap='autumn')
        print ('hour_from_%s_to_%s_%s.png' % (str(tr.time_init), str(tr.time_end), str(count)))
        plt.savefig('%s/images/hour_from_%s_to_%s_%s.png' % (track_path, str(tr.time_init), str(tr.time_end), str(count)))
        t.remove()
        count += 1

        #strplt.remove()
        q.remove()
        #plt.clf()
        #plt.cla()
        #plt.close()




print ("end")

#ani = animation.FuncAnimation(m, animate, interval=1000)
#animati
#plt.show()






