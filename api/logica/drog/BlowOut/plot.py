# -*- coding: utf-8 -*-
"""
Created on Wed May 25 08:31:16 2016

@author: Carlos
"""
import matplotlib as mpl
import matplotlib.cm as cmap
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.tri as mtri
from mpl_toolkits.mplot3d import Axes3D
from pylab import *
import sys

def PlotPlume(b_t, x_t, y_t, z_t, w_t, v_t, u_t, E):


    rcParams['legend.loc'] = 'best'


    n_plot = 10
    
    
    """
    Ploteo de la Pluma
    """
    b_p = np.linspace(b_t[0], b_t[-1], n_plot)
    x_p = np.linspace(x_t[0], x_t[-1], n_plot)
    y_p = np.linspace(y_t[0], y_t[-1], n_plot)
    z_p = np.linspace(z_t[0], z_t[-1], n_plot)
    w_p = np.linspace(w_t[0], w_t[-1], n_plot)
    u_p = np.linspace(u_t[0], u_t[-1], n_plot)
    v_p = np.linspace(v_t[0], v_t[-1], n_plot)
    
    b_color = np.linspace((b_p[0] / (1. * b_p[-1])), (b_p[-1] / (1. * b_p[-1])), n_plot )
    
    
    
    t = np.linspace(0, 2 * np.pi)
    fig = plt.figure(figsize = (8,8))
    ax0 = plt.subplot2grid((1, 15), (0, 2), colspan = 14, projection = '3d')
    ax1 = plt.subplot2grid((1, 15), (0, 0))
    for i in np.arange(0, n_plot-1):
        x = b_p[i] * np.cos(t)
        y = b_p[i] * np.sin(t)
        z = ( u_p[i] * (x) - v_p[i] * (y)) / w_p[i] - z_p[i]
        triang = mtri.Triangulation((x - x_p[i]), (y - y_p[i]))
        PlotObject = ax0.plot_trisurf(triang, z)
        PlotObject.set_edgecolor((b_color[i], b_color[i], b_color[i]))
        PlotObject.set_facecolor((b_color[i], b_color[i], b_color[i]))
    
    
    """
    Ploteo de la barra de colores
    """
    b_c = np.array([])
    x = np.linspace(0, 1, n_plot)
    y = np.linspace(0, 1, n_plot)
    xx, yy = np.meshgrid(x, y)
    
    for i in np.arange(0, n_plot):
        b_c = np.append(b_c, b_color)
    
    b_c = np.reshape(b_c, (n_plot, n_plot))
    b_c = b_c.T
    
    PaletObject = ax1.contourf(xx, yy, b_c, 100, cmap = cmap.Greys_r)
    ax1.yaxis.set_ticks(np.linspace(0, 1, 11))
    ax1.yaxis.set_ticklabels(['1.0', '0.9', '0.8', '0.7', '0.6', '0.5', '0.4', '0.3', '0.2', '0.1', '0.0' ])
    ax1.xaxis.set_ticks(np.linspace(0, 1, 1))
    ax1.xaxis.set_ticklabels([''])
    
    
    """
    Detalles de la figura
    """
    
    
    ax0.set_xlabel('Desplazamiento meridional $s [m]$')
    ax0.set_ylabel('Desplazamiento zonal $s [m]$')
    ax0.set_zlabel('Profundidad $z [m]$')
    ax0.set_title("Ascenso de un VC de Petroleo")
    ax1.set_ylabel('$C /C_0$')
    #plt.show()
    plt.savefig('Plume E ' + str(E) + '.png')


def PlotCurves(b_t, x_t, y_t, z_t, w_t, v_t, u_t, wl_t, vl_t, ul_t, T_t, E):
    
    #z_t = z_t[-1:0:-1]    
   # x_t = x_t[-1:0:-1]    
   # y_t = y_t[-1:0:-1]
    
    rcParams['legend.loc'] = 'best'
    
    fig_c = plt.figure()
    axd = fig_c.gca(projection='3d')
    axd.plot( x_t[0:-1], y_t[0:-1], -z_t, label = 'desplazamiento')
    axd.legend()
    
    
    axd.set_xlabel('Desplazamiento meridional $s [m]$')
    axd.set_ylabel('Desplazamiento zonal $s [m]$')
    axd.set_zlabel('Profundidad $z [m]$')
    axd.set_title("Ascenso de un VC de Petroleo")
    #plt.show()
    plt.savefig('Desplazamiento E ' + str(E) + '.png')


def PLotVelocities(w_t, T_T, x_t, E):

    rcParams['legend.loc'] = 'best'    
    
    
    fig_v = plt.figure()
    axv = fig_v.gca()
    axv.plot(T_T / 6, (w_t / w_t[0]), label = 'velocidad vertical $w [m/s]$')
    axv.set_xlabel('Tiemppo $t [s]$')
    axv.set_xlim(0, 50)
    axv.set_ylabel(' velocidad vertical $w/w_0$')    
    axv.legend()
    plt.savefig('velocidad vertical E' + str(E) + '.png')


def PlotRadio(b_t, T_T, z_t, E):
    
    rcParams['legend.loc'] = 'best'
    
    fig_b = plt.figure()
    axb = fig_b.gca()
    axb.plot(b_t,(100 - z_t), label = 'Radio $r [m]$')
    axb.legend()
    axb.set_ylabel('Profundidad $z [m]$')
    axb.set_xlabel('Radio $r [m]$')
    plt.savefig('Radio E ' + str(E) + '.png')

def PlotDensity(dty_def, T_T, x_t, E):
    
    rcParams['legend.loc'] = 'best'
    
    fig_dd = plt.figure()
    axdd = fig_dd.gca()
    axdd.plot(T_T / 2  , (dty_def / dty_def[0]), label = 'Deficiencia de densidad')
    axdd.legend()
    axdd.set_xlim(0, 80)
    axdd.set_xlabel('Tiempo $t [s]$')
    axdd.set_ylabel(' deficiencia de densidad ')
    plt.savefig('deficiencia de densidad E' + str(E) + '.png')


def Plotconcentracion(b_t, T_T, E):
    
    rcParams['legend.loc'] = 'best'    
    
    fig_c = plt.figure()
    axc = fig_c.gca()
    axc.plot(T_T / 60 , (1 - (b_t / b_t[0])), label = 'Radio $r [m]$')
    axc.legend()
    axc.set_xlabel('Tiempo $t [min]$')
    axc.set_ylabel(' concentrcion $C/C_0$')
    plt.savefig('Concentracion E ' + str(E) + '.png')
    #plt.show()
    
def Plotxy(x_t, y_t, z_t, E):

    rcParams['legend.loc'] = 'best'    
    
    fig_zx = plt.figure()
    axzx = fig_zx.gca()
    axzx.plot(-y_t[:-1], -z_t, label = 'Desplazamiento $z/x$')
    axzx.legend()
    
    axzx.set_xlabel('Desplazamiento Zonal $S [m]$')
    axzx.set_ylabel('Desplazamiento vertical $S [m]$')
    plt.savefig('DesplazamientoZX ' + str(E) + '.png')
    #plt.show()
    
    
    fig_zy = plt.figure()
    axzy = fig_zy.gca()
    axzy.plot(x_t[:-1], -z_t, label = 'Desplazamiento $z/y$')
    axzy.legend()
    
    axzy.set_xlabel('Desplazamiento meridional $S [m]$')
    axzy.set_ylabel('Desplazamiento vertical $S [m]$')
    plt.savefig('DesplazamientoZY ' + str(E) + '.png')
    #plt.show()
    
def czx(z_t2, z_t1, z_t05, z_t01, z_t001, x_t2, x_t1, x_t05, x_t01, x_t001, x_as, z_as):

    rcParams['legend.loc'] = 'best'    
    
    fig_czx = plt.figure()
    axczx = fig_czx.gca()
    axczx.plot(-x_t2[:-1], - z_t2, 'g', label = '$E = 2$')
    axczx.plot(-x_t1[:-1], - z_t1, 'r', label = '$E = 1$')
    axczx.plot(-x_t05[:-1], - z_t05, 'm', label = '$E = 0.5$')
    axczx.plot(-x_t01[:-1], - z_t01, 'c', label = '$E = 0.1$')
    axczx.plot(-x_as, z_as, 'b--', label = 'As-Ma')
    
    #axczx.plot(x_t001[:np.size(z_t001)], - z_t001, 'b', label = 'E = 0.01')
    axczx.legend()    
    
    axczx.set_xlim(-30, 40)
    axczx.set_xlabel('Desplazamiento meridional $S [m]$')
    axczx.set_ylabel('Profundidad $z [m]$')
    plt.savefig('czx.png')
    
    #plt.show()
    
    
def czy(z_t2, z_t1, z_t05, z_t01, z_t001, y_t2, y_t1, y_t05, y_t01, y_t001, y_as, z_as):

    rcParams['legend.loc'] = 'best'    
    
    fig_czy = plt.figure()
    axczy = fig_czy.gca()
    axczy.plot(-y_t2[:-1], - z_t2, 'g', label = '$E = 2$')
    axczy.plot(-y_t1[:-1], - z_t1, 'r', label = '$E = 1$')
    axczy.plot(-y_t05[:-1], - z_t05, 'm', label = '$E = 0.5$')
    axczy.plot(-y_t01[:-1], - z_t01, 'c', label = '$E = 0.1$')
    axczy.plot(-y_as, z_as, 'b--', label = 'As-Ma')
    # axczy.plot(y_t001[:np.size(z_t001)], - z_t001, 'b', label = 'E = 0.01')
    axczy.legend()    
    
    axczy.set_xlim(90, -30)
    axczy.set_xlabel('Desplazamiento zonal $S [m]$')
    axczy.set_ylabel('Profundidad $z [m]$')
    plt.savefig('czy.png')
    
    #plt.show()
    

    
    
def czb(z_t2, z_t1, z_t05, z_t01, z_t001, b_t2, b_t1, b_t05, b_t01, b_t001):
    
    rcParams['legend.loc'] = 'best'    
    
    fig_czb = plt.figure()
    axczb = fig_czb.gca()
    axczb.plot(b_t2, - z_t2, 'g', label = '$E = 2$')
    axczb.plot(b_t1, - z_t1, 'r', label = '$E = 1$')
    axczb.plot(b_t05, - z_t05, 'm', label = '$E = 0.5$')
    axczb.plot(b_t01, - z_t01, 'c', label = '$E = 0.1$')
    # axczy.plot(y_t001[:np.size(z_t001)], - z_t001, 'b', label = 'E = 0.01')
    axczb.legend()    
    
    axczb.set_xlim(0,45)
    axczb.set_xlabel('Radio $r [m]$')
    axczb.set_ylabel('Profundidadl $z [m]$')
    plt.savefig('czb.png')
    
    #plt.show()
    
    
def cwt(T_T2, T_T1, T_T05, T_T01, T_T001, w_t2, w_t1, w_t05, w_t01, w_t001):
    
    rcParams['legend.loc'] = 'best'
    
    fig_cwt = plt.figure()
    axcwt = fig_cwt.gca()
    axcwt.plot( (w_t2 / w_t2[0]), -T_T2 / 1, 'g', label = '$E = 2$')
    axcwt.plot( (w_t1 / w_t1[0]),  -T_T1 / 1, 'r', label = '$E = 1$')
    axcwt.plot(  (w_t05 / w_t05[0]),-T_T05 / 1, 'm', label = '$E = 0.5$')
    axcwt.plot( (w_t01 / w_t01[0]), -T_T01 / 1, 'c', label = '$E = 0.1$')
    # axczy.plot(y_t001[:np.size(z_t001)], - z_t001, 'b', label = 'E = 0.01')
    axcwt.legend()    
    
    axcwt.set_xlim(1,0)
    #axcwt.set_ylim(0,1)
    axcwt.set_ylabel('Profundidad $z [m]$')
    axcwt.set_xlabel('Decaimiento de la velocidad vertical $w /w_0$')
    plt.savefig('czwt.png')
    
    #plt.show()
    
def cdt(T_T2, T_T1, T_T05, T_T01, T_T001, dty_def2, dty_def1, dty_def05, dty_def01, dty_def001):
    
    rcParams['legend.loc'] = 'best'
    
    fig_cdt = plt.figure()
    axcdt = fig_cdt.gca()
    axcdt.plot(  (dty_def2 /dty_def2[0]), -T_T2,'g', label = '$E = 2$')
    axcdt.plot(  (dty_def1 /dty_def1[0]),-T_T1,'r', label = '$E = 1$')
    axcdt.plot(  (dty_def05 /dty_def05[0]),-T_T05,'m', label = '$E = 0.5$')
    axcdt.plot(  (dty_def01 /dty_def01[0]),-T_T01,'c', label = '$E = 0.1$')
    # axczy.plot(y_t001[:np.size(z_t001)], - z_t001, 'b', label = 'E = 0.01')
    axcdt.legend()    
    
    
    axcdt.set_xlim(1, 0)
    axcdt.set_ylabel('Profundidad $z [m]$')
    axcdt.set_xlabel('Decaimiento de la deficiencia de densidad ')
    plt.savefig('cdt.png')
    
    #plt.show()
    
def czxy(z_t2, z_t1, z_t05, z_t01, z_t001, y_t2, y_t1, y_t05, y_t01, y_t001, x_t2, x_t1, x_t05, x_t01, x_t001, x_as, y_as, z_as):
    
    rcParams['legend.loc'] = 'best'    
    
    fig_czxy = plt.figure()
    axczxy = fig_czxy.gca(projection='3d')
    
    
    axczxy.plot( -x_t2[0:-1],- y_t2[0:-1], -z_t2, 'g', label = '$E=2$' )
    axczxy.plot( -x_t1[0:-1], -y_t1[0:-1], -z_t1, 'r', label = '$E=1$' )
    axczxy.plot( -x_t05[0:-1], -y_t05[0:-1], -z_t05, 'm', label = '$E=0.5$' )
    axczxy.plot( -x_t01[0:-1], -y_t01[0:-1], -z_t01, 'c', label = '$E=0.1$' )
    axczxy.plot( -x_as, -y_as, z_as, 'b--', label = 'As-Ma' )    
    axczxy.legend()
    
    axczxy.set_ylim(90, -10)
    axczxy.set_xlabel('Desplazamiento meridional $s [m]$')
    axczxy.set_ylabel('Desplazamiento zonal $s [m]$')
    axczxy.set_zlabel('Profundidad $z [m]$')
    #plt.show()
    plt.savefig('czxy.png')

    
    