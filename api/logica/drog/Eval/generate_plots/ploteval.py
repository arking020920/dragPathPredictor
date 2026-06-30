import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from ..Generic import GenericFunctions as gen
import numpy as np


def plotmap(driflon, driflat, tracklon, tracklat, driftime, tracktime, zone):

    nodes = np.loadtxt('./petromar/Geodata/Zones/%s/%s.nod' % (zone, zone))
    nlats, nlons = gen.Xy2Ll(nodes[:, 1], nodes[:, 2], 19.747526, -85.766569)

    startidx = np.searchsorted(driftime, tracktime[0]) - 1
    endidx = np.searchsorted(driftime, tracktime[-1])
    err = np.zeros(tracktime.size)

    fig_mapa = plt.figure(figsize=(16, 9), dpi=255)
    ax = plt.subplot(111)
    mapa = Basemap(llcrnrlon=nlons.min(), llcrnrlat=nlats.min(), urcrnrlon=nlons.max(), urcrnrlat=nlats.max(),
                   projection='merc', resolution='i', ax=ax, fix_aspect=True)

    mapa.drawcoastlines()
    mapa.drawmapboundary(linewidth=0.0, fill_color='#f0f0f0')
    mapa.drawmeridians(np.linspace(nlons.min(), nlons.max(), 10), labels=[0, 0, 0, 1], color='#969696', fontsize=12)
    mapa.drawparallels(np.linspace(nlats.min(), nlats.max(), 10), labels=[1, 0, 0, 0], color='#969696', fontsize=12)

    driflon, driflat = mapa(driflon, driflat)
    tracklon, tracklat = mapa(tracklon, tracklat)

    mapa.plot(tracklon, tracklat, '-or')
    mapa.plot(driflon[startidx:endidx], driflat[startidx:endidx], '-ok')
    #plt.show()

    fig_err = plt.figure()

    for idxtrack, idxdrif in enumerate(np.arange(startidx, endidx)):
        err[idxtrack] = np.sqrt(
            (tracklon[idxtrack] - driflon[idxdrif]) ** 2 + (tracklat[idxtrack] - driflat[idxdrif]) ** 2)
    #print err  # debug

    error = plt.plot(err)
    #plt.show()
    return fig_mapa, fig_err, np.stack((tracklon, tracklat, driflon[startidx:endidx], driflat[startidx:endidx]), axis=1)