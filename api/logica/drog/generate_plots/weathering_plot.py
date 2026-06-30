# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
from PIL._imaging import font

from Generic import GenericFunctions as gen
from Generic import paths
############### 
import matplotlib.tri as mtri                                       #tringulacion   
from matplotlib import cm                                           #paletas de colores
from matplotlib.patches import Polygon                              #objeto poligonos
from matplotlib.collections import PatchCollection                  #objeto patches

from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes #axes zoom
from mpl_toolkits.axes_grid1.inset_locator import mark_inset        #mark zoom

import cmocean as cmo                                               #paleta color oceano
from mpl_toolkits.basemap import Basemap                            #mapa
#Colocar luego
#import xy2ll as ll                                                  #cambio de coordenada
###############################################################################    
def plot_thick(out_list=None, path=None, zone=None):

    time = np.array([])
    tick = np.array([])
    sumtick = 0

    fig = plt.figure(figsize=(16, 9), dpi=255)
    ax = plt.subplot(111)
    #mapa = Basemap(llcrnrlon=nlons.min(), llcrnrlat=nlats.min(), urcrnrlon=nlons.max(), urcrnrlat=nlats.max(),
     #              projection='merc', resolution='c', ax=ax, fix_aspect=True)

    for idx, tr in enumerate(out_list):
        # plot normal track
        # plot las particulas que se pierden del dominio
        time = np.append(time, idx)
        tick = np.append(tick, np.average(tr.arr_thickness))

    plt.plot(time[1:], tick[1:])
    plt.xlabel('horas')
    plt.ylabel('[m]')

    plt.title('Grosor superficial')
    print('simpletick_all.png')# % (str(tr.time_init), str(tr.time_end), str(count))
    plt.savefig(path+'/images/simple_tick.png')

    plt.close()
###############################################################################
def plot_rho(out_list=None, path=None, zone=None):
    time = np.array([])
    Rho = np.array([])
    sumtick = 0

    fig = plt.figure(figsize=(16, 9), dpi=255)
    ax = plt.subplot(111)

    for idx, tr in enumerate(out_list):
        # plot normal track
        # plot las particulas que se pierden del dominio
        time = np.append(time, idx)
        Rho = np.append(Rho, np.average(tr.arr_density))

    plt.plot(time[1:], Rho[1:])
    plt.xlabel('horas')
    plt.ylabel('[Kg/m3]')

    plt.title('Densidad de la mancha')
    print('simple-rho_all.png')  # % (str(tr.time_init), str(tr.time_end), str(count))
    plt.savefig(path + '/images/simple-rho_all.png')

    plt.close()
###############################################################################
def plot_conc(vol, out_list=None, path=None, zone=None ):

    time = np.array([])
    conc = np.array([])
    sumtick = 0

    fig = plt.figure(figsize=(16, 9), dpi=255)
    ax = plt.subplot(111)

    for idx, tr in enumerate(out_list):
        # plot normal track
        # plot las particulas que se pierden del dominio
        if tr.radio is not None:
            time = np.append(time, idx)
            conc = np.append(conc, np.average(tr.arr_density)*vol/(tr.radio**2*np.pi))
    plt.plot(time[1:], conc[1:])
    plt.xlabel('horas')
    plt.ylabel('[kg/km**2]')

    plt.title(u'Concentracion superficial')

    print('simple_conc_all.png')# % (str(tr.time_init), str(tr.time_end), str(count))
    plt.savefig(path+'/images/simple_conc.png')

    plt.close()
###############################################################################    
#def plotBudget(VolT,volevap,voldisp):
def plotBudget(VolT, out_list, path, nele):

    #timep = np.arange(np.size(volevap))
    #timep = np.arange(31813)
    #########################################################
    # colores "Tableau 20" en RGB.
    tableau20 = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),
                 (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),
                 (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),
                 (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),
                 (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]
    # Scale the RGB values to the [0, 1] range, which is the format matplotlib accepts.
    for i in range(len(tableau20)):
        r, g, b = tableau20[i]
        tableau20[i] = (r / 255., g / 255., b / 255.)
    ##########################################################
    yticks = np.linspace(0,VolT,11)

    time = np.array([])
    volevap = np.array([])
    voldisp = np.array([])

    for idx, tr in enumerate(out_list):
        time = np.append(time, idx)
        #print(tr.arr_volumeEvap.size)
        volevap = np.append(volevap, np.average(tr.arr_volumeEvap))
        voldisp = np.append(voldisp, np.average(tr.arr_volumeNatDisp))

    #for idx, tr in enumerate(out_list):
    #    time = np.append(time, idx)
    #    if idx
    #        volevap = np.append(volevap, np.sum(tr.arr_volumeEvap)/idx)
    #    voldisp = np.append(voldisp, np.sum(tr.arr_volumeNatDisp)/idx)

    datae = nele * volevap
    datad = 30 * nele * voldisp
    
    plt.figure(figsize=(14, 9), dpi=300)
    ax = plt.subplot(111)
    ax.spines["top"].set_visible(False)
    ax.spines["bottom"].set_visible(False) 
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()
    ax.set_ylim(bottom=0.0, top=VolT)
    ax.set_yticks(yticks)
    ax.set_ylabel('Volumen $[m^3]$')
    ax.set_xlabel('Tiempo $[h]$')
    #plt.title('Balance Total', fontdict=font)
    plt.title('Balance Total')
    
    for i in yticks:
        ax.plot(time, np.array(i).repeat(time.size), '--', lw=0.5, color='black', alpha=0.4)

    ax.fill_between(time, VolT, facecolor=tableau20[-6], label='Vol Restante')
    if datad.any():

        ax.fill_between(time, datae, datae+datad, facecolor=tableau20[-5], label='Vol Disperso')
    ax.fill_between(time, datae, facecolor=tableau20[0], label='Vol Evaporado')
    
    ax.legend()
    print('Balance_Total.png')
    plt.savefig(path + '/images/Balance_Total.png')
    plt.close()  
###############################################################################
#def plotmap(nodxy,tri,pos_par,data1,data2,data2u,data2v,data3):
def plotmap(VolT, out_list, path, zone):
    '''
    plotea la mancha dentro de la zona de estudio
    '''
    nodxy = np.loadtxt(os.path.join(paths.geo_dir(),zone,zone+'.nod')) ### arreglar
    ##creando malla del dominio
    #lon00, lat00 = ll.xy2ll(nodxy[:,1],nodxy[:,2])
    lon00, lat00 = gen.Xy2Ll(nodxy[:, 1], nodxy[:, 2])
    trigrid = mtri.Triangulation(lon00, lat00,triangles=tri[:,1:])
    #malla regular
    lonnod = np.linspace(lon00.min(),lon00.max(),900)
    latnod = np.linspace(lat00.min(),lat00.max(),900)
    lonnod, latnod =np.meshgrid(lonnod,latnod)
    #creando la proyeccion geografica
    
    mapa = Basemap(llcrnrlon=lon00.min(),llcrnrlat=lat00.min()
                            ,urcrnrlon=lon00.max(),urcrnrlat=lat00.max()
                            ,projection='merc',resolution='c')
    
    #paletas de colores
    cmap0 = cmo.cm.speed #campo de fondo
    cmap1 = cm.bone_r #mancha de petroleo

    ##############################################################################
    rang = [71]  # np.arange(np.size(pos_par,1)/2-1)

    for h in rang:
        fig = plt.figure(figsize=(14, 9))
        # plt.subplots_adjust(left=0.05,right=0.95,top=0.90,bottom=0.05,wspace=0.15,hspace=0.05)
        ax = plt.subplot(111)

        mapa.drawmeridians(np.arange(lon00.min().round(), lon00.max().round() + 1), labels=[0, 0, 0, 1])
        mapa.drawparallels(np.arange(lat00.min().round(), lat00.max().round() + 1), labels=[1, 0, 0, 0])
        mapa.drawmapscale(lon00.max() - 1.1, lat00.min() + 0.2,
                          lon00.max(), lat00.min(), 100,
                          barstyle='fancy', labelstyle='simple',
                          fillcolor1='w', fillcolor2='#555555',
                          zorder=5)

        mapa.readshapefile('./shapefiles/countyp020', 'caribe', drawbounds=True, linewidth=0.7)
        mapa.readshapefile('./shapefiles/cuba', 'cuba', drawbounds=True, linewidth=0.7)
        fill_shp(ax, mapa.cuba_info, mapa.cuba)
        fill_shp(ax, mapa.caribe_info, mapa.caribe)
        #####################################

        i = 2 * h
        j = 2 * h + 1

        # fondo
        ############################################
        var = mtri.CubicTriInterpolator(trigrid, data1[:, h])
        var = var(lonnod, latnod)
        mapa.pcolormesh(lonnod, latnod, var, latlon=True, vmin=var.min(), vmax=var.max(), cmap=cmap0)
        #        mapa.colorbar(size='2%',extend= 'both',label= 'Velocidad'+'$[m/s]$')

        #        ####malla regular de la mancha
        lon0, lat0 = ll.xy2ll(pos_par[:, i], pos_par[:, j])

        lonp = np.linspace(lon0.min(), lon0.max(), 500)
        latp = np.linspace(lat0.min(), lat0.max(), 500)
        lonp, latp = np.meshgrid(lonp, latp)

        ################################################
        var = mtri.CubicTriInterpolator(trigrid, data2[:, h])
        var = var(lonnod, latnod)

        lwv = (var) / var.max()

        varu = mtri.CubicTriInterpolator(trigrid, data2u[:, h])
        varu = varu(lonnod, latnod)
        varv = mtri.CubicTriInterpolator(trigrid, data2v[:, h])
        varv = varv(lonnod, latnod)

        mapa.streamplot(lonnod, latnod, varu, varv, latlon=True, density=2.0, cmap=cmap0, linewidth=lwv)
        #############################################

        trispill = mtri.Triangulation(lon0, lat0)
        mask = set_mask1(trispill, 0.21)
        trispill.set_mask(mask)

        var = mtri.CubicTriInterpolator(trispill, data3[:, h] * 1000)
        var = var(lonp, latp)

        mapa.pcolormesh(lonp, latp, var, latlon=True, vmin=data3.min(), vmax=data3.max(), cmap=cmap1)
        #        mapa.pcolormesh(lonp, latp,var,latlon=True,vmin=var.min(),vmax=var.max(),cmap=cmap1)
        mapa.colorbar(size='2%', extend='both', label=u'Concentración ' + '$[g/m^2]$')
        plt.title(u'Pronóstico de la concentración para ' + str(h + 1) + ' horas', fontdict=font)

        plt.savefig('Conc' + str(h + 1) + '.png')
        plt.close()

###############################################################################
###############################################################################
#wavg = np.average(wind_all, 0)
#cavg = np.average(corr_all, 0)
#davg = np.average(Density, 0)
#vavg = np.average(Viscosity, 0)
#wcavg = np.average(WaterCont, 0)
#
#veavg = np.sum(VolEvap, 0)
#pvavg = np.sum(PresentVol, 0)
#vdavg = np.sum(VolDisp, 0)
#plotBudget(VolT,veavg,vdavg)
#
#plot1D(davg,'Densidad','$[kg/m^3]$')
#plot1D(vavg,'Viscosidad','$[cSt]$')
#plot1D(wcavg*100,'Contenido de agua','$[\%]$')
#plot1D(veavg/VolT*100,'Petroleo Evaporado','$[\%]$')
#plot1D(vdavg/VolT*100,'Petroleo Disperso','$[\%]$')
#plot1D(pvavg/VolT*100,'Petroleo Restante','$[\%]$')
#plot1D(wavg,'Intensidad del Viento','$[m/s]$')
#plot1D(cavg,'Intensidad de las Corrientes','$[m/s]$')
#plotmap(nodxy,tri,pos_par,corr_all,corr_all,corru_all,corrv_all,Conc)
