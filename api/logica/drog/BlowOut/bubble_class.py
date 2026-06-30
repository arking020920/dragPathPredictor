# -*- coding: utf-8 -*-
"""
Created on Mon May  2 19:29:29 2016

esto mola





@author: Carlos
"""

import numpy as np
import scipy.constants as sco
import scipy.interpolate as spin
import seawater as sw
from seawater.library import T90conv


class OilBubbleTracking(object):
    '''
    Clase para seguir el desarrollo de un volumen de control de petroleo y gas derrmando en el oceano
    '''
    def __init__(self, input_data):
        
        '''
        Parametros que definen el objeto
        '''
        self.E = np.float(input_data['Model']['constante_E'])
        self.ss_p = np.float(input_data['Model']['salinidad_p'])
        self.tt_p = np.float(input_data['Model']['temperatura_p'])
        self.lat_p = np.float(input_data['Model']['y'])
        self.lon_p = np.float(input_data['Model']['x'])
        if self.lon_p < 0: self.lon_p = 360 + self.lon_p
        self.depth_p = np.float(input_data['Model']['profundidad_p'])
        self.b_v = np.float(input_data['Model']['radio_v'])
        self.v_p = np.float(input_data['Model']['v_p'])
        self.u_p = np.float(input_data['Model']['u_p'])
        self.w_p = np.float64(input_data['Model']['w_p'])
        self.dty_p = np.float(input_data['Model']['densidad_p'])
        self.final_time= np.float(input_data['Model']['tiempo_final'])
        self.dty_p15 = np.float(input_data['Model']['densidad15_p'])
        self.escenario = input_data['Model']['nombre_escenario']
        self.track = input_data['Model']['nombre_trayectoria']
        #Constantes Globales y parametros de inicializacion
        
        self.dty_v = self.dty_p
        self.K_ss = 0.12
        self.tt_p_0 = np.array([15])
        self.K_tt = 0.12
        self.g = sco.g
        self.EE = 2
        self.p1 = 0.1
        self.p2 = 0.2
        self.p3 = 0.5
        self.a1 = 0.23
        self.a2 = 0.2
        self.pi = sco.pi
        self.w_l = 0.02
        self.uvz_p = np.sqrt(self.u_p ** 2 + self.v_p ** 2 + self.w_p ** 2 )
        self.d_t = 0.1 * self.b_v / self.uvz_p
        self.h_v = np.float64(self.d_t * self.uvz_p)
        
        #Very very big data set
        self.h_v_1 = np.float64()
        self.b_v_1 = np.float64()
        self.b_v_1 = np.float64()
        
        
        
        
        #self.m_v = 0.05        
        self.m_v = self.dty_p * self.pi * self.b_v **2 * self.h_v
        self.m_p = self.m_v
        self.d_b = 0
        self.d_x = 0
        self.d_y = 0
        self.d_z = 0
        self.d_s = 0
        self.d_c_fi_c_alfa = 0
        self.d_c_fi_s_alfa = 0
        self.d_s_fi = 0
        self.A_s = 2 * self.pi * self.b_v * self.h_v
        self.K_0 = 0
        self.K_c = 0
        self.S_0 = 0.56
        self.X_0 = 0.2
        self.cc_p = 0.15
        self.cc_a = 0.02
        self.K_cc = 0.36
        self.C_d = 0
        self.beta = 0.7 ** 2
        self.w_b = 0.
        self.temp_flag = self.d_t
        self.dty_def = 1
        self.bubble_R = 8.3144621
        self.bubble_M = 0.01204
        self.bubble_k = self.bubble_M / self.bubble_R
        self.x = 0
        self.y = 0
        
        #                Tracking Data
        self.x_t = np.array([0])
        self.y_t = np.array([0])
        self.d_dty_t = np.array([])
        self.Q_e_t = np.array([])
        self.u_p_t = np.array([])     
        self.v_p_t = np.array([])
        self.w_l_t = np.array([])
        self.u_l_t = np.array([])
        self.v_l_t = np.array([])
        self.w_p_t = np.array([])
        self.lat_p_t = np.array([])
        self.lon_p_t = np.array([])
        self.m_v_t = np.array([])
        self.m_t_v_t = np.array([])
        self.b_v_t = np.array([])     
        self.h_v_t = np.array([])
        self.tt_p_t = np.array([])
        self.ss_p_t = np.array([])
        self.cc_p_t = np.array([])
        self.depth_p_t = np.array([])
        self.d_x_t = np.array([])
        self.d_y_t = np.array([])
        self.dty_p_t = np.array([])
        self.dty_b_t = np.array([])  
        self.vol_p_t = np.array([])    
        self.dty_def_t = np.array([])
        self.dty_a_t = np.array([])
        self.tt_l_t = np.array([])        
        self.ss_l_t = np.array([])
        self.vol_v_t = np.array([])
        self.dty_v_t = np.array([])
        self.tt_l_t = np.array([])
        self.T_T = np.array([])

    def Environment(self, I_m, nivel_m, lat_m, lon_m):
             fi = spin.RegularGridInterpolator(( nivel_m[:], lat_m[:, 1], lon_m[1, :]), I_m[1:, :, :] )
             I_int = fi((self.depth_p, self.lat_p, self.lon_p))
         
             return I_int


    def Find_level(self, nivel_m):
        self.i=0
        while(nivel_m[self.i]<self.depth_p):
             self.i=self.i+1
             if self.i==0:
                self.j=0
                self.i=1
             else:
                self.j=self.i-1
    
        
        
    def Densities(self, nivel_m): 
         self.pp_l = sw.pres(self.depth_p, self.lat_p)   
         self.tt_l = T90conv(self.tt_l)
         self.dty_a = sw.dens(np.abs(self.ss_l), self.tt_l, self.pp_l)              
         
         K_a15_0 = 613.97226
         K_a15_1 = 0
         a_15 = (K_a15_0 + K_a15_1 * self.dty_p15) / self.dty_p15 ** 2
         K_tt = np.exp(-a_15 * (self.tt_p - 15) * (1 + 0.8 * a_15 * (self.tt_p - 15)))
         ganma = 10 ** -3 * np.exp(-1.62080 + 0.00021592 * self.tt_p + 0.87096 * (10 ** 6) / self.dty_p15 ** 2 + 4.2092 * self.tt_p * (10 ** 3) / self.dty_p15 ** 2)
         K_pp = 1 / (1 - ganma * self.pp_l * 10 ** -9)
         self.dty_p = self.dty_p15 * K_tt * K_pp
                  
         
         
         #self.dty_def = (self.dty_a - self.dty_p) / self.dty_p
         self.dty_b = self.bubble_k * (self.pp_l / self.tt_p)
         self.dty_m = (self.dty_p * (1 - self.beta) + self.dty_b * self.beta)
         self.b_f = (self.dty_p - self.dty_m) / (self.dty_p - self.dty_b)
    def DensityP(self):
         K_a15_0 = 613.97226
         K_a15_1 = 0
         a_15 = (K_a15_0 + K_a15_1 * self.dty_p15) / self.dty_p15 ** 2
         K_tt = np.exp(-a_15 * (self.tt_p - 15) * (1 + 0.8 * a_15 * (self.tt_p - 15)))
         ganma = 10 ** -3 * np.exp(-1.62080 + 0.00021592 * self.tt_p + 0.87096 * (10 ** 6) / self.dty_p15 ** 2 + 4.2092 * self.tt_p * (10 ** 3) / self.dty_p15 ** 2)
         K_pp = 1 / (1 - ganma * self.pp_l * 10 ** -9)
         dty_p = self.dty_p15 * K_tt * K_pp 
         return dty_p          
        
    def Geometry(self):
         self.mod_vel_a = np.sqrt(self.u_l ** 2 + self.v_l ** 2 + self.w_l ** 2)
         self.mod_vel_p = np.sqrt(self.u_p ** 2 + self.v_p ** 2 + self.w_p ** 2)
         self.alfa_h_p = np.arctan(self.v_p / self.u_p)
         self.alfa_h_a = np.arctan(self.u_l /self.v_l)
         self.fi_h = 90 - self.alfa_h_p - self.alfa_h_a
         self.fi_v = np.arctan(self.w_p / np.sqrt(self.u_p ** 2 + self.v_p ** 2))
         self.v_a_ph = self.mod_vel_a * np.cos(self.fi_h)
         self.v_a_pt = np.dot([self.w_p, self.u_p, self.v_p], [self.w_l, self.u_l, self.v_l]) * self.mod_vel_a
         self.c_fi_c_alfa = np.cos(self.fi_v) * np.cos(self.alfa_h_p)
         self.c_fi_s_alfa = np.cos(self.fi_v) * np.sin(self.alfa_h_p)
         self.s_fi = np.sin(self.fi_v)         
         
         
    def BubbleMass(self):
        self.m_b = self.dty_b * self.pi * self.h_v * self.b_f * (self.b_v ** 2) * (self.beta ** 2) 
        
        
    def Entrainment(self):
        
    
        #                      Shear induced entrainment
        
        self.d_dty = self.dty_a - self.dty_v
        if (self.d_dty < 0): self.d_dty = 0.001
        self.F = self.EE * (np.abs(self.mod_vel_p - self.v_a_pt) / np.sqrt(self.g * self.b_v * self.d_dty / self.dty_a ))
        self.T_n = 0.554 * np.sin(self.fi_v) / self.F ** 2
        self.T_n = self.T_n + 0.057
        self.T_d = 5 * self.v_a_pt / np.abs(self.mod_vel_p - self.v_a_pt)
        self.T_d = self.T_d + 1
        self.A = np.sqrt(2) * (self.T_n / self.T_d)
        self.Q_s = self.E * self.pi * self.b_v * self.h_v * self.A * (np.abs(self.mod_vel_p - self.v_a_pt))
        
        
        
        #                       Forced Entrainment
        
         
        d_s = np.sqrt(self.d_x ** 2 +self.d_y ** 2 + self.d_z ** 2) 
        self.Q_f_x = self.dty_a * np.abs(self.u_l) * self.d_t * (self.pi * self.b_v * self.d_b * np.abs(np.cos(self.fi_v) * np.cos(self.alfa_h_p)) + 2 * self.b_v * d_s * np.sqrt(1 - np.cos(self.fi_v) ** 2 * np.cos(self.alfa_h_p) ** 2) + self.pi * self.b_v ** 2 * np.abs(self.d_c_fi_c_alfa) / 2)
        self.Q_f_y = self.dty_a * np.abs(self.v_l) * self.d_t * (self.pi * self.b_v * self.d_b * np.abs(np.cos(self.fi_v) * np.sin(self.alfa_h_p)) + 2 * self.b_v * d_s * np.sqrt(1 - np.cos(self.fi_v) ** 2 * np.sin(self.alfa_h_p) ** 2) + self.pi * self.b_v ** 2 * np.abs(self.d_c_fi_s_alfa) / 2)
        self.Q_f_z = self.dty_a * np.abs(self.w_l) * self.d_t * (self.pi * self.b_v * self.d_b * np.abs(np.sin(self.fi_v)) + 2 * self.b_v * d_s * np.abs(np.cos(self.fi_v) ) + self.pi * self.b_v ** 2 * np.abs(self.d_s_fi) / 2 )
        #self.Q_f = Q_f_x + Q_f_y + Q_f_z
        self.Q_f = np.sqrt(self.Q_f_x ** 2 + self.Q_f_y ** 2 + self.Q_f_z ** 2) / (self.dty_a * self.d_t)
        self.Q_e = self.Q_f + self.Q_s
        #self.Q_e = 0.5 * self.vol_v
        
    def volumen(self):
        self.vol_v = self.pi * self.b_v ** 2 * self.h_v



    def MassLoss(self):
        a = 0.7
        self.d_m_i =self.K_0 * a * self.X_0 * self.S_0 * self.A_s
        self.d_m_d = self.dty_a * self.K_c * self.A_s * (self.cc_p - self.cc_a) /self. b_v         
        self.volumen()
        
    def StepIntergation(self, u_m, v_m, tt_m, ss_m, nivel_m, lat_m, lon_m):


        while self.w_p >= 0.02 and self.depth_p > 0.01 and self.temp_flag < self.final_time:
            
            self.temp_flag = self.temp_flag + self.d_t
            
            self.Find_level(nivel_m)
            
            self.u_l = self.Environment(u_m, nivel_m, lat_m, lon_m)
            self.v_l = self.Environment(v_m, nivel_m, lat_m, lon_m)
            self.tt_l = self.Environment(tt_m, nivel_m, lat_m, lon_m)
            self.ss_l = self.Environment(ss_m, nivel_m, lat_m, lon_m)
            
            #self.volumen()
            
            self.Densities(nivel_m)
        
            #             Mass Variables Diagnostic
            self.BubbleMass()
            self.MassLoss()
            self.Geometry()
            self.Entrainment()
            self.d_m = self.dty_a * self.Q_e * self.d_t - self.d_m_i - self.d_m_d
            #self.v_a = self.vol_v - self.dty_p / self.m_p
            #self.dty_v = (self.dty_p * self.dty_p / self.m_p + self.dty_a * self.v_a) / self.vol_v
            self.dty_v = (self.dty_v * self.vol_v + self.dty_a * self.Q_e * self.d_t) / (self.vol_v + self.Q_e * self.d_t)
            self.dty_def = (self.dty_a - self.dty_v) / self.dty_v
            if (self.dty_def < 0): self.dty_def = 0.000001
            self.vol_v = self.vol_v + self.Q_e * self.d_t
            self.m_t_v = self.m_v + self.d_m
           
            #            Scalars Pronostic
           
            self.m_v_1 = self.m_v + self.d_m
            self.tt_p_1 = (self.m_v * self.tt_p + self.d_m * self.tt_l - self.dty_a * 2 * self.K_tt * self.h_v * (self.tt_p - self.tt_l)* self.d_t ) / self.m_v_1
            self.ss_p_1 = (self.m_v * self.ss_p + self.d_m * self.ss_l - self.dty_a * 2 * self.K_ss * self.h_v * (self.ss_p - self.ss_l)* self.d_t ) / self.m_v_1
            self.cc_p_1 = (self.m_v * self.cc_p + self.d_m * self.cc_a - self.dty_a * 2 * self.K_cc * self.h_v * (self.cc_p - self.cc_a)* self.d_t ) / self.m_v_1
            self.dty_p_1 = self.DensityP()
            self.m_t_v_1 = self.m_t_v + self.d_m
            #self.dty_def = (self.dty_a - self.dty_p) / self.dty_p
    
    
            #            Velocities Pronostic
           
            self.u_p_1 = self.HorizontalVelocities(self.u_p, self.u_l, 0) 
            self.v_p_1 = self.HorizontalVelocities(self.v_p, self.v_l, 0)
            #self.w_p_1 = self.BubbleVelocity(self.w_p, self.w_l)
            self.w_p_1 = self.HorizontalVelocities(self.w_p, self.w_l, 1)

           
           
            #            Geometric Pronostic
            
            self.h_v_1 = self.h_v * (np.sqrt(self.u_p_1 ** 2 + self.v_p_1 ** 2 + self.w_p_1 ** 2) / self.mod_vel_p)
            self.b_v_1 = np.sqrt(self.m_v_1 /(self.dty_v * self.h_v_1 * self.pi) )
            self.d_b_v = self.b_v_1 - self.b_v
            self.fi_v_1 = np.arctan(self.w_p_1 / (np.sqrt(self.u_p_1 ** 2 + self.v_p_1 ** 2)))
            self.alfa_h_p_1 = np.arctan(self.v_p_1 / self.u_p_1)
            self.c_fi_c_alfa_1 = np.cos(self.fi_v_1) * np.cos(self.alfa_h_p_1)
            self.c_fi_s_alfa_1 = np.cos(self.fi_v_1) * np.sin(self.alfa_h_p_1)
            self.s_fi_1 = np.sin(self.fi_v_1)
            self.d_c_fi_c_alfa = self.c_fi_c_alfa_1 - self.c_fi_c_alfa
            self.d_c_fi_s_alfa = self.c_fi_s_alfa_1 - self.c_fi_s_alfa
            self.d_s_fi = self.s_fi_1 - self.s_fi
            
            
            
            #          Displacements
            
            
            self.d_x = self.u_p_1 * self.d_t
            self.d_y = self.v_p_1 * self.d_t 
            self.x = self.x + self.d_x
            self.y = self.y + self.d_y
            self.d_z = self.w_p_1 * self.d_t
            self.d_lat_p = self.d_y / 111110
            self.d_lon_p = self.d_x / 111110
            
            #          Tracking and Updates
            
            self.Densities(nivel_m)            
            
            self.Tracking()
            self.Updates(nivel_m)
            #self.vol_p_t = np.append(self.vol_p_t, self.vol_p)
            print('depth', self.depth_p_t[-1])
       
       
    def HorizontalVelocities(self,vel, vel_a, L) :
        vel_1 = (self.m_t_v * vel + self.d_m * vel_a + L * self.m_t_v_1 * self.dty_def     \
        * self.g  * self.d_t) / self.m_t_v_1        
        return vel_1 
        
    def BubbleVelocity(self, vel, vel_a):
        vel_1 = vel + (self.d_t / self.m_t_v) * ((vel_a * self.d_m / self.d_t) + (self.dty_a - self.dty_v) * self.g * self.pi \
        * self.b_v ** 2 * (1 - self.b_f * self.beta ** 2 ) * self.h_v + (self.dty_a - self.dty_b) * self.g * self.pi * self.b_v\
        ** 2 * self.h_v * self.b_f - vel * self.d_m / self.d_t)
        return vel_1
        
    def Tracking(self):
        self.u_p_t = np.append(self.u_p_t, self.u_p_1)     
        self.v_p_t = np.append(self.v_p_t, self.v_p_1)
        self.w_p_t = np.append(self.w_p_t, self.w_p_1)
        self.w_l_t = np.append(self.w_l_t, self.w_l)
        self.u_l_t = np.append(self.u_l_t, self.u_l)
        self.v_l_t = np.append(self.v_l_t, self.v_l)
        #self.lat_p_t = np.append(self.lat_p_t, (self.lat_p + self.d_lat_p))
        #self.lon_p_t = np.append(self.lon_p_t, (self.lon_p + self.d_lon_p))
        self.m_v_t = np.append(self.m_v_t, self.m_v_1)
        #self.m_t_v_t = np.append(self.m_t_v_t, self.m_t_v_1)
        self.b_v_t = np.append(self.b_v_t, self.b_v_1)     
        self.h_v_t = np.append(self.h_v_t, self.h_v_1) 
        self.tt_p_t = np.append(self.tt_p_t, self.tt_p_1)
        #self.ss_p_t = np.append(self.ss_p_t, self.ss_p_1)
        #self.cc_p_t = np.append(self.cc_p_t, self.cc_p_1)
        self.depth_p_t = np.append(self.depth_p_t, (self.depth_p - self.d_z))
        self.d_x_t = np.append(self.d_x_t, self.d_x)
        self.d_y_t = np.append(self.d_y_t, self.d_y)
        self.x_t = np.append(self.x_t, self.x)
        self.y_t = np.append(self.y_t, self.y)
        self.dty_p_t = np.append(self.dty_p_t, self.dty_p_1)
        #self.dty_b_t = np.append(self.dty_b_t, self.dty_b)
        self.dty_def_t = np.append(self.dty_def_t, self.dty_def)
        self.dty_a_t = np.append(self.dty_a_t, self.dty_a)
        self.tt_l_t = np.append(self.tt_l_t, self.tt_l)
        #self.ss_l_t = np.append(self.ss_l_t, self.ss_l) 
        self.dty_v_t = np.append(self.dty_v_t, self.dty_v)
        self.vol_v_t = np.append(self.vol_v_t, self.vol_v)
        self.ss_l_t = np.append(self.ss_l_t, self.ss_l)
        self.Q_e_t = np.append(self.Q_e_t, self.Q_e)
        self.d_dty_t = np.append(self.d_dty_t, self.d_dty)
        self.T_T = np.append(self.T_T, self.temp_flag)
    def Updates(self, nivel_m):
        self.lat_p =self.lat_p + self.d_lat_p 
        self.lon_p =self.lon_p + self.d_lon_p
        self.u_p = self.u_p_1
        self.v_p = self.v_p_1
        self.w_p = self.w_p_1
        self.h_v = self.h_v_1
        self.b_v = self.b_v_1
        self.A_s = 2 * self.pi * self.b_v * self.h_v
        #self.dty_def = (self.dty_a - self.dty_p_1) / self.dty_p_1
        self.depth_p = self.depth_p -self.d_z
        self.tt_p = self.tt_p_1
        self.ss_p = self.ss_p_1
        self.cc_p = self.cc_p_1 
        self.m_v = self.m_v_1  
        self.Find_level(nivel_m)
        #self.uvz_p = np.sqrt(self.u_p ** 2 + self.v_p ** 2 + self.w_p ** 2 )
        #self.d_t = 0.1 * self.b_v / self.uvz_p
        
    def GetVar(self):
        b_t2 = self.b_v_t
        x_t2 = self.x_t
        y_t2 = self.y_t
        z_t2 = self.depth_p_t
        w_t = self.w_p_t
        v_t = self.v_p_t
        u_t = self.u_p_t
        wl_t = self.w_l_t
        vl_t = self.v_l_t
        ul_t = self.u_l_t
        T_t = self.temp_flag
        t_T = self.T_T
        h_t = self.h_v_t
        dty_def2 = self.dty_def_t
        E = self.E
        return h_t, b_t2, x_t2, y_t2, z_t2, w_t, v_t, u_t, wl_t, vl_t, ul_t, T_t, t_T, dty_def2, E
        
    def SaveVar(self):
        spath = '../Datos/Escenarios/' + self.escenario + '/tracks/' + self.track
        np.save(spath + '/xp.npy', self.x_t)
        np.save(spath + '/yp.npy', self.y_t)
        np.save(spath + '/zp.npy', self.depth_p_t)
        np.save(spath + '/dety_def.npy', self.dty_def_t)
        np.save(spath + '/h.npy', self.h_v_t)
        np.save(spath + '/b.npy', self.b_v_t)
        np.save(spath + '/vp.npy', self.v_p_t)
        np.save(spath + '/up.npy', self.u_p_t)
        np.save(spath + '/wp.npy', self.w_p_t)
        np.save(spath + '/wl.npy', self.w_l_t)
        np.save(spath + '/vl.npy', self.v_l_t)
        np.save(spath + '/ul.npy', self.u_l_t)
        np.save(spath + '/tp.npy', self.T_T)
        np.save(spath + '/tfp.npy', self.temp_flag)
        
        
    def PetromInput(self):
         lat_in = self.lat_p
         lon_in = self.lon_p - 360.
         b_in = self.b_v
         v_in = self.vol_v #* self.dty_v
         d_t = self.d_t
         return lat_in, lon_in, b_in, v_in, d_t

        

        