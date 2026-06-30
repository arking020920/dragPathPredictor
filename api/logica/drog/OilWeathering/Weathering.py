#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Created on Mon May 02 11:59:22 2016

@author: Worgan
"""

from __future__ import print_function
import numpy as np


class Weathering(object):

    '''
    Clase basica de Python para la estimacion del envejecimiento
    de hidrocarburos(oil weathering) en el modelo PPETROMAR.
    
    Para usar esta clase el programa debe crear un objeto Weathering
    definiendo las principales propiedades del hidrocarburo derramado
    
    >>> mi_derrame = Weathering(inAPI, inVis, visRefTemp, Volume)
           
           inAPI => densidad inicial especificada en API Gravity
           inVis => viscosidad inicial del hidrocarburo [cSt]
           visReTemp => temperatura de referencia a la cual fue medida la viscosidad [C]
           Volume => volumen inicial [m**3]
    
    Luego se definen las propiedades del entorno para terminar la inicializacion,
    el valor de retorno por defecto es el numero de pseudocomponentes usados (10)
    
   >>> mi_derrame.SetEnvironment(windSpeed,waterTemp,mixedLayerDepth)
           
           windSpeed => velocidad del viento a 10m [m/s]
           waterTemp => temperatura del agua [m]
           mixedLayerDepth => profundidad de la capa de mezcla [m]
    
    La integracion temporal se realiza por el metodo
    
    >>> mi_derrame.Step(stepLengthSec)
           
           stepLengthSec => tiempo total de integracion [seg] 
    
    Las variables de estado son obtenidas a traves de los siguentes metodos
       
       >>> mi_derrame.getDensity() # devuelve la densidad [kg/m3]
       >>> mi_derrame.getViscosity() # devuelve la viscosiad [cSt]
       >>> mi_derrame.getArea() # devuelve el area de la mancha [m**2]
       >>> mi_derrame.getSlickWidth() # devuelve el ancho de la mancha perpendicular al viento [m**2]
       >>> mi_derrame.getThickness() # devuelve el gorsor de la capa de petroleo sin enmulcion
       >>> mi_derrame.getProdThickness() # devuelve el gorsor de la capa de petroleo con enmulcion
       >>> mi_derrame.getEnvirThickness() # devuelve el gorsor maximo de la capa de petroleo con enmulcion
       >>> mi_derrame.getC1() # devuelve el coeficiente de escalado debido al transporte de gotas de petroleo
       >>> mi_derrame.getC2() # debuelve el coeficiente de escalado debido al proceso Langmuir 
       >>> mi_derrame.getWaterCont() # dwevuelve el contenido de agua [%]
       >>> mi_derrame.getVolInit() # devuelve el volumen inicial de petroleo [m**3]
       >>> mi_derrame.getPresentVol() # devuelve el volumen actual de petroleo [m**3]
       >>> mi_derrame.getVolEvap() # devuelve el volumen perdido por evaporacion [m**3]
       >>> mi_derrame.getVolNatDisp() # devuelve el volumen perdido por dispersion natural [m**3]
       >>> mi_derrame.getAge() # devuelve el tiempo total de simulacion [seg]
       >>> mi_derrame.getMinThickness() # devuelve el gorsor minimo de la capa de petroleo [m]
       >>> mi_derrame.isMinThickness() # devuelve True si se ha alcanzado el gorsor minimo de la capa de petroleo, else False
       >>> mi_derrame.isOilSlickLeft() # devuelve True si el balance de masa indica q aun queda petroleo sin envejecer, else False
       >>> mi_derrame.getAreaMod() # devuelve una fraccion estimada del area total del derrame donde ocurren los procesos de weathering
    '''

    def __init__(
        self,
        inAPI,
        inVis,
        visRefTemp,
        Volume,
        ):
        """ definicion de los parametros iniciales
        """

        self.api = inAPI
        self.refVis = inVis
        self.refVisT = visRefTemp + 273.18  #  todas las tem son en K

        # Variables relacionadas al volumen

        self.v0 = Volume  # volumen inicial [m**3]
        self.volumeEvap = 0.
        self.volumeDis = 0.
        self.areaMax = np.nan_to_num(np.Inf)
        self.oilRemainingFlag = True
        self.age = 0
        self.expCoefRho = 0.0008

        # Variables relacionadas a los pseudo componentes

        self.pseudoComponentsSet = False
        self.defaultNumPC = 10  # num de pc
        self.massFrac = np.zeros(self.defaultNumPC)
        self.boilPt = np.zeros(self.defaultNumPC)
        self.pcVol = np.zeros(self.defaultNumPC)  #  en moles
        self.pcBP = np.zeros(self.defaultNumPC)  #  punto de ebullicion k
        self.pcMV = np.zeros(self.defaultNumPC)  #  mole/m**3
        self.pcMW = np.zeros(self.defaultNumPC)  #
        self.pcEvapRate = np.zeros(self.defaultNumPC)  #  razon de evap moles/(m**2 sec)
        self.averMW = 0.
        self.oilVis0 = 0.  # camvio de vis por eva

        # coeficientes de esprcimiento gravitacional

        self.L = 0.  # const esparcimiento grav
        self.T0 = 0.
        self.l0 = 0.
        self.windDistance = 0.
        self.width = 0.

        #  Variables relacionadas a la enmulsificazion

        self.yFraction = 0.  #  contenido de agua (fraccion)
        self.S = 0.
        self.Ymax = 0
        self.Smax = 0
        self.dMax = 10E-6  #  10 micras
        self.dMin = 1e-06  #  1 micras
        self.dSize = self.dMax

        #   Variables relacionadas al controlde la dispesion y el esparcimiento

        self.dtDropModel = 30
        self.DF = 0.  #  coeficiente dependiente del vento en Delvigne droplet model
        self.MaxDispSize = 5e-05  #  50 micras

        #    Variables relacionadas al gorsor de la capa de petroleo

        self.minThicknessFlag = True
        self.minThickness = 2E-6

####################################################################
###########
###############################

    def SetEnvironment(
        self,
        wind10,
        waterTemp,
        mixLayerDepth=10.,
        ):
        """ Metodo para definir o redefinir las condiciones del entorno 
     ....   
         >>> mi_derrame.SetEnvironment(windSpeed,waterTemp,mixedLayerDepth)
           
               windSpeed => velocidad del viento a 10m [m/s]
               waterTemp => temperatura del agua [m]
               mixedLayerDepth => profundidad de la capa de mezcla [m]
        """

        numberOfPC = self.defaultNumPC
        self.wTemp = waterTemp + 273.18  #  todas las temp estan K
        self.wind = wind10

        #  verificar la vel min del wiento = 1m/sec

        if self.wind < 1.:
            self.wind = 1.
        self.mixLayer = mixLayerDepth

        if not self.pseudoComponentsSet:
            self.pseudoComponentsSet = True
            self.SetDefaultPC(self.api)

        if self.oilVis0 == 0.:

            #  esta seccion solo se ejecuta una vez
            #  inicializa la contante usada en el cambio de la vis por la evap

            Ct = 5000.0  #  K

            fac = Ct * (1. / self.wTemp - 1. / self.refVisT)
            self.oilVis0 = self.refVis * np.exp(fac)
            self.CF = 1.5 * np.sqrt(self.oilVis0)
            if self.CF < 2.0:
                self.CF = 2.0
            if self.CF > 12:
                self.CF = 12.0

                #  calcular la densidad [kg/m**3] del agua un funcion de la temp [C]

            self.wRho = 1020 * (1. - 1.12E-4 * (waterTemp - 4.0))

            #  agregar 2% para el agua de mar
            #  calcular la densidad inicial del petroleo en funcion de API y wtemp

            self.oilRho = 1000 * (141.5 / (131.5 + self.api))
            refRhoT = 273.18 + 16.0
            self.oilRho *= 1. - self.expCoefRho * (self.wTemp - refRhoT)

            #  chequear undimiento del petroleo y mostrar error

            if self.oilRho > self.wRho:
                numberOfPC = -8

                #  inicializar constantes para la emmulsificacion

            dyVis = self.oilRho * 1e-06 * self.CalculateVis()
            if dyVis > 0.050:
                self.Ymax = 0.9 - 0.0952 * np.log(dyVis / 0.050)
            else:
                self.Ymax = 0.9
            self.Smax = 6.0 / self.dMin * self.Ymax / (1. - self.Ymax)

            #  usado en la entrada de agua

            self.Schk = 6.0 / self.dMax * self.Ymax / (1. - self.Ymax)

            #  usado en la entrada de agua....
            #  calcular el umbral de evapo para la formacion de enmulsion. manual ADIOS

            TBP = 532.98 - 3.1295 * self.api
            TG = 1356.7 - 247.36 * np.log(self.api)
            A1est = (483.0 - TBP) / TG
            if A1est < 0.:
                A1est = 0.
            elif A1est > 0.4:
                A1est = 0.4
            A2est = 1.
            if self.api < 26.0:
                A2est = 0.08
            elif self.api > 50.0:
                A2est = 0.303
            else:
                A2est = -1.038 - 0.78935 * np.log10(1. / self.api)
            self.EmOnsetFraction = 0.50 * (A1est + A2est)
            self.diag = self.EmOnsetFraction
        k0y = 2.042 * 1e-06

        #  usado en doc Roberts ....

        self.Ky = k0y * self.wind * self.wind
        self.Ks = 6.0 * self.Ky / self.dMax
        if self.L == 0.:

            #  esta seccion solo se ejecuta una vez
            #  inicializa la constante de esparcimiento gravitacional

            self.L = self.v0 ** 0.3333
            fac1 = self.L ** 1.1428
            fac2 = (1e-06 * self.CalculateVis()) ** -0.4285  # convertir [cSt] => [m**2/s]
            self.T0 = fac1 * fac2
            self.l0 = (self.L * self.L * self.T0 * self.T0) ** 0.3333

            #  calcurar la razon de dispersion natural por seg

        d = 5.48E-3 * self.wind ** 5
        d = d ** 0.57

        #  energia de la ola rompiente

        f = 1.18e-3 * self.wind ** 1.03

        #  establecer limite minimo pra la velucidad viento

        if self.wind < 3.0:
            f = 0.
        vEntrained = self.MaxDispSize ** 1.7 / 1.7
        F = 1. - np.exp(-f * self.dtDropModel)
        self.DissapationFactor = F * vEntrained

        #  calcular el termino de Delvigne dependiente del viento para el modelo droplet

        self.DF = d * F
        return numberOfPC

#####################################3333
        # ###############################################
################################################

    def Step(self, stepLengthSec):
        """Metodo para integrar en el tiempo
           >>> mi_derrame.Step(stepLengthSec)
           
               stepLengthSec => tiempo total de integracion [seg] 
       """

        # comprobar si aun queda petroleo, si no, no integrar

        moleSum = np.sum(self.pcVol)
        if moleSum == 0. or not self.oilRemainingFlag:
            self.oilRemainingFlag = False
            return

            #  procesos de integracion

        self.StepEvaporation(stepLengthSec)
        self.StepNaturalDispersion(stepLengthSec)
        self.StepWaterContent(stepLengthSec)
        windFac = 0.03
        if self.wind > 6.0:
            windFac += 0.0050
        self.windDistance += windFac * self.wind * stepLengthSec
        chkThickness = self.getProdThickness() * self.getC1()
        if chkThickness > self.minThickness:
            self.minThicknessFlag = True
        else:
            self.minThicknessFlag = False
        self.age += stepLengthSec

#####################################3333
        # ###############################################
################################################

    def getDensity(self):
        """ >>> mi_derrame.getDensity() # devuelve la densidad [kg/m3]
        """

        rhoOil = self.oilRho * (1. + 0.18 * self.getVolEvap() / self.v0)
        delRho = (self.wRho - rhoOil) / self.wRho
        if delRho < 1E-4:
            rhoOil = self.wRho * (1. - 1E-4)
        return rhoOil * (1. - self.yFraction) + self.wRho \
            * self.yFraction

    def getViscosity(self):
        """ >>> mi_derrame.getViscosity() # devuelve la viscosiad [cSt]
  ....   """

        return self.CalculateVis()

    def getArea(self):
        """ >>> mi_derrame.getArea() # devuelve el area de la mancha [m**2]
        """

        return self.CalculateArea(self.age)

    def getConcentration(self):    
        """ >>> mi_derrame.getConcentration() # devuelve la concentracion superficial de petroleo [kg/m**2]
        """
        
        return self.getDensity()*self.v0/self.getArea()
    
    def getSlickWidth(self):
        """ >>> mi_derrame.getSlickWidth() # devuelve el ancho de la mancha perpendicular al viento [m**2]
        """

        return self.width

    def getThickness(self):
        """ >>> mi_derrame.getThickness() # devuelve el gorsor de la capa de petroleo sin enmulcion
        """

        return self.CalculateVolume() / self.CalculateArea(self.age)

    def getProdThickness(self):
        """>>> mi_derrame.getProdThickness() # devuelve el gorsor de la capa de petroleo con enmulcion
        """

        return self.getThickness() / (1. - self.yFraction)

    def getEnvirThickness(self):
        """mi_derrame.getEnvirThickness() # devuelve el gorsor maximo de la capa de petroleo con enmulcion
        """

        return self.getC1() * self.getC2() * self.getProdThickness()

    def getC1(self):
        """ >>> mi_derrame.getC1() # devuelve el coeficiente de escalado debido al transporte de gotas de petroleo
        """

        if not self.isOilSlickLeft():
            return 0.
        C1 = 1.

        #  para caso de velocidad del viento muy baja

        if self.wind < 3.0:
            return C1

            #  calculo del coeficiente de escala (SlickMass/DropletMass)

        scale = self.getDensity() * self.getProdThickness() \
            / self.CalculateDropletMass()
        C1 = 1. + 2.2 * (1. - np.exp(-np.sqrt(3.0 * scale)))
        return C1

    def getC2(self):
        """ >>> mi_derrame.getC2() # debuelve el coeficiente de escalado debido al proceso Langmuir 
        """

        if not self.isOilSlickLeft():
            return 0.
        C1 = self.getC1()
        thicknessNow = C1 * self.getProdThickness()
        val = self.calculateC2(self.wind, self.getDensity(),
                               thicknessNow)
        return val

    def getAreaMod(self):
        """ >>> mi_derrame.getAreaMod() # devuelve una fraccion estimada del area total del derrame donde ocurren los procesos de weathering
        """

        return self.AreaMod()

    def getWaterCont(self):
        """>>> mi_derrame.getWaterCont() # dwevuelve el contenido de agua [%]
        """

        return self.yFraction

    def getPresentVol(self):
        """ >>> mi_derrame.getPresentVol() # devuelve el volumen actual de petroleo [m**3]
        """

        if not self.isOilSlickLeft():
            return 0.
        return self.CalculateVolume()

    def getVolInit(self):
        """>>> mi_derrame.getVolInit() # devuelve el volumen inicial de petroleo [m**3]
        """

        return self.v0

    def getVolEvap(self):
        """>>> mi_derrame.getVolEvap() # devuelve el volumen perdido por evaporacion [m**3]
        """

        return self.volumeEvap

    def getVolNatDisp(self):
        """>>> mi_derrame.getVolNatDisp() # devuelve el volumen perdido por dispersion natural [m**3]
        """

        return self.volumeDis

    def getAge(self):
        """>>> mi_derrame.getAge() # devuelve el tiempo total de simulacion [seg]"""

        return self.age

    def getMinThickness(self):
        """>>> mi_derrame.getMinThickness() # devuelve el gorsor minimo de la capa de petroleo [m]
        """

        return self.minThickness

    def getWave(self):
        return self.wave_height(self.wind, fetch=None)

    def isMinThickness(self):
        """>>> mi_derrame.isMinThickness() # devuelve True si se ha alcanzado el gorsor minimo de la capa de petroleo, else False
        """

        return self.minThicknessFlag

    def isOilSlickLeft(self):
        """>>> mi_derrame.isOilSlickLeft() # devuelve True si el balance de masa indica q aun queda petroleo sin envejecer, else False
        """

        return self.oilRemainingFlag

#####################################3333
        # ###############################################
################################################

    # --------------------------------------------------
    # --------------- Metodos intermos -----------------
    # ----------- no deben ser llamados ----------------
    # --------------------------------------------------

    def SetDefaultPC(self, api):
        """Inicializacion de los pseudo componentes basado an los datos de corelacion y la API
        """

        T0 = 457.16 - 3.3447 * api

        #  Manual ADIOS

        dT = 1356.7 - 247.36 * np.log(api)
        sumVolMW = 0.
        sumVol = 0.
        for i in np.arange(self.defaultNumPC):
            BP = T0 + dT * (np.float(i) + 0.50) / self.defaultNumPC

            #  temperatura [K]

            MV = 7.000E-5 - 2.102E-7 * BP + 1.000E-9 * BP * BP
            MW = 0.04132 - 1.985E-4 * BP + 9.494E-7 * BP * BP
            vi = self.v0 / self.defaultNumPC
            self.pcVol[i] = vi / MV

            #  moles en cada corte

            self.pcBP[i] = BP
            self.pcMV[i] = MV
            self.pcMW[i] = MW
            sumVolMW += MW * vi / MV
            sumVol += vi / MV
        self.averMW = sumVolMW / sumVol

        # calculo de la zaon de evaporacion

        K0 = 0.0048 * 1.3676 * (0.018 / self.averMW) ** 0.3333 \
            * self.wind ** 0.7777
        R1 = 8.205E-5  #  constante de los gases [(atmos m**3)/(mol K)]
        for i in np.arange(self.defaultNumPC):
            vp = self.VaporPressure(self.pcBP[i])
            moleRate = K0 * vp / (R1 * self.wTemp)  #  [mol/(m**2 sec)]
            self.pcEvapRate[i] = moleRate

################################################

    def VaporPressure(self, BP):
        """ Metodo para calcualar la presion de vapor en atm"""

        dZ = 0.97  #  constante de Lyman
        R = 1.987  #  constante de los gases [(cal)/(mol K)]
        dS = 8.75 + R * np.log(BP)
        c2 = 0.19 * BP - 18.0
        T1 = BP - c2
        T2 = self.wTemp - c2
        fac1 = dS * T1 * T1 / (dZ * R * BP)
        fac2 = (T2 - T1) / (T2 * T1)
        vapP = np.exp(fac1 * fac2)
        return vapP

################################################

    def StepEvaporation(self, stepLengthSec):
        """Metodo para la integracion temporal de la evap"""

        #  calcula la suma de los ps [mol]

        moleSum = np.sum(self.pcVol)
        AModCoef = 1.
        effArea = self.CalculateArea(self.age + stepLengthSec / 2.0) \
            * (1. - self.yFraction) * (1. - AModCoef * self.AreaMod())
        for i in np.arange(self.defaultNumPC):
            downWindFactor = self.windDistance ** 0.1111
            if downWindFactor < 1.:
                downWindFactor = 1.
            Dmi = self.pcEvapRate[i] * (self.pcVol[i] / moleSum) \
                * effArea * stepLengthSec / downWindFactor
            if Dmi > self.pcVol[i]:
                Dmi = self.pcVol[i]  #  reemplazar los viejos volumenes molares
            self.pcVol[i] = self.pcVol[i] - Dmi  #  suatraer la suma de evap
            self.volumeEvap += Dmi * self.pcMV[i]

################################################

    def StepNaturalDispersion(self, stepLengthSec):
        """Metodo para la integracion temporal de la DispNatural"""

        #  si el area maxima esta restringida no existe disp

        if self.areaMax != np.nan_to_num(np.Inf):
            return

            #  dis normal

        AModCoef = 1.

        #  kg de petroleo disperso

        massDis = self.CalculateDisConst() * self.DissapationFactor \
            * (1. - self.yFraction) * self.CalculateArea(self.age) \
            * (1. - AModCoef * self.AreaMod()) * stepLengthSec \
            / self.dtDropModel
        volDis = massDis / self.getDensity()  #  conversion a volumen
        nowVolume = self.getPresentVol()  #  volumen de las gotas.... ....

        #  comprovar si quedan moles de petroleo en cada pc y ajustar debido a las perdidas

        if volDis > nowVolume:
            self.oilRemainingFlag = False
        else:
            for i in np.arange(self.defaultNumPC):
                pcFrac = self.pcVol[i] * self.pcMV[i] / nowVolume
                self.pcVol[i] = self.pcVol[i] - pcFrac * volDis \
                    / self.pcMV[i]
        self.volumeDis += volDis

################################################

    def StepWaterContent(self, stepLengthSec):
        """Metodo para la integracion temporal de la Enmulsificacion"""

        #  comprobar si la evap ha empesado

        evapFraction = self.getVolEvap() / self.v0
        if evapFraction > self.EmOnsetFraction:
            self.S = self.Smax - (self.Smax - self.S) * np.exp(-self.Ks
                    * stepLengthSec / self.Smax)
            if self.S > self.Smax:
                self.S = self.Smax

                # ajustar el contenido de agua

            if self.S < self.Schk:
                self.yFraction = self.S * self.dMax / (6.0 + self.S
                        * self.dMax)

                #  comprobar si admite mas agua

                self.dSize = self.dMax
            else:
                self.yFraction = self.Ymax
                self.dSize = 6.0 / self.S * self.yFraction / (1.
                        - self.yFraction)
            if self.yFraction > 1.:
                self.yFraction = 1.

################################################

    def CalculateVis(self):
        """Metodo para calcular la viscosidad basada en la correcion por la temp del agua,
        la correcion por la evap y la empulsifica"""

        #  calcular el cambio debido a la evap

        fractionEvap = self.volumeEvap / self.v0
        vis = self.oilVis0 * np.exp(self.CF * fractionEvap)

        #  calcular el cambio debido a la enmulsiffff
        #  coeficiente de 0.2 tomado del manual de adios

        Cy = 0.50 * (1. + 0.2 * self.dMin / self.dSize)
        if Cy > 0.85:
            Cy = 0.85
        if Cy < 0.35:
            Cy = 0.45
        fac = 2.5 * self.yFraction / (1. - Cy * self.yFraction)
        vis = vis * np.exp(fac)
        return vis

################################################

    def CalculateArea(self, time):
        """ Metodo para estimar el area del derrame basado 
        primero en Fay y luego en Richarson/Batchlor/Obuko ademas de 
        el esparcimiento de las gotas debido al viento"""

        l1 = 0
        if time < self.T0:

            #  se mantiene el esprcimiento gravitacional

            l1 = (self.L * self.L + time * time) ** 0.333
        else:

            # Richardson/Batchelor/Obuko

            fac0 = (100 * self.l0) ** 0.6666 + 0.006 * (time - self.T0)  #  conversion a [cm] por la cont de Obuko
            l1 = .01 * fac0 ** 1.5  # conversion de vuelta a [m]

        #  correcion de la deriva de las gotas a favor del viento....

        self.width = l1
        l2 = l1 + self.windDistance
        area = l1 * l2

        #  verificar si sobrepasa el areaMax espesificada

        if area > self.areaMax:
            area = self.areaMax
        return area

################################################

    def AreaMod(self):
        """ Metodo para calcular el factor de reduccion 
            para evitar perdidas en zonas delgadas de la mancha
        """

        ex = self.getC1() * self.getC2()
        fac = (self.v0 - self.getPresentVol()) / self.v0
        if ex <= 1. or fac < 1e-06:
            return 0.
        x = (fac / ex) ** (1 / (ex - 1.))
        return x

################################################

    def CalculateVolume(self):
        """Metodo pra calcular el volumen total de petroleo"""

        if not self.isOilSlickLeft():
            return 0
        presentVol = 0.
        for i in np.arange(self.defaultNumPC):
            presentVol += self.pcVol[i] * self.pcMV[i]
        if presentVol > self.v0:
            presentVol = self.v0

            # el modelo mo puede agregar volumen

        return presentVol

################################################  ....

    def CalculateDisConst(self):
        """Metodo pra calcular la contante de disipacion C0 Delvigne,
        usando el metodo de la formulacion de Roy"""

        return 2400.0 * np.exp(-73.682 * np.sqrt(1e-06
                               * self.CalculateVis()))

################################################

    def calculateC2(
        self,
        wind,
        rho0,
        thickness0,
        ):
        """ Metodo para el calculo de C2 usando el ajuste analitico del modelo Langmuir de Roy"""

        #  convertir el gorsor de [m] a [mm]

        thick = 1000 * thickness0
        if thick > 1.:
            thick = 1.

            #  velosidad del viento mini

        if wind < 3.0:
            return 1.
        x = 2.0 * (rho0 - 800.0) / (self.wRho - 800.0)
        cLow = np.float()
        nLow = np.float()
        cHigh = np.float()
        nHigh = np.float()
        c = np.float()
        n = np.float()
        val = np.float()
        if wind < 5.0:
            wCoef = (wind - 3.0) / 2.0
            cLow = 0.8851 + x * (-0.4312 + x * 0.6034)
            nLow = -0.8263 + x * (0.0466 + x * -0.0432)
            cHigh = 2.3015 + x * (-0.6293 + x * 1.2263)
            nHigh = -0.7527 + x * (-0.0050 + x * -0.0183)
            c = cHigh * wCoef + cLow * (1. - wCoef)
            n = nHigh * wCoef + nLow * (1. - wCoef)
            val = c * thick ** n
        elif wind < 8.0:
            wCoef = (wind - 5.0) / 3.0
            cLow = 2.3015 + x * (-0.6293 + x * 1.2263)
            nLow = -0.7527 + x * (-0.0050 + x * -0.0183)
            cHigh = 5.1184 + x * (-1.0233 + x * 2.1188)
            nHigh = -0.6799 + x * (-0.0044 + x * -0.0092)
            c = cHigh * wCoef + cLow * (1. - wCoef)
            n = nHigh * wCoef + nLow * (1. - wCoef)
            val = c * thick ** n
        elif wind < 10.:
            wCoef = (wind - 8.0) / 2.0
            cLow = 5.1184 + x * (-1.0233 + x * 2.1188)
            nLow = -0.6799 + x * (-0.0044 + x * -0.0092)
            cHigh = 6.9004 + x * (-1.2544 + x * 2.6376)
            nHigh = -0.6600 + x * (-0.0034 + x * -0.0069)
            c = cHigh * wCoef + cLow * (1. - wCoef)
            n = nHigh * wCoef + nLow * (1. - wCoef)
            val = c * thick ** n
        else:

            #  para vientos mayores de 10m/s

            c = 6.9004 + x * (-1.2544 + x * 2.6376)
            n = -0.6600 + x * (-0.0034 + x * -0.0069)
            val = c * thick ** n
        if val > 80.0:
            val = 80.0
        if thickness0 > 0.001:  #  ajuste por el gorsor min de la capa
            val = val * np.exp(-(thickness0 - 0.001) / 0.001)
        val = val / self.getC1()
        if val < 1.:
            val = 1.
        return val

    def wave_height(self, wind, fetch):
        """
        compute the wave height

        :param wind: wind speed
        :type wind: floating point number in m/s units

        :returns Hrms: RMS wave height in meters
        """
        g = 9.8
        # wind stress factor
        # Transition at U = 4.433049525859078 for linear scale with wind speed.
        #   4.433049525859078 is where the solutions match
        ws = 0.71 * wind ** 1.23 if wind < 4.433049525859078 else wind

        # (2268 * ws ** 2) is limit of fetch limited case.
        if (fetch is not None) and (fetch < 2268 * ws ** 2):
            H = 0.0016 * np.sqrt(fetch / g) * ws
        else:  # fetch unlimited
            H = 0.243 * ws * ws / g

        Hrms = 0.707 * H

        # arbitrary limit at 30 m -- about the largest waves recorded
        # fixme -- this really depends on water depth -- should take that
        #          into account?
        return Hrms if Hrms < 30.0 else 30.0





################################################
    def CalculateDropletMass(self):
        """Metodo para el calculode la masa de las gotas basado en la furmulacion de Delvigne,
        dependiente de la densidad, vis, wind"""

        #  tartes dependientes de la vis y el viento

        dm0 = self.CalculateDisConst() * self.DF
        Wmix = 1.5 * 0.026 * self.wind ** 2.5  #  calculo de la distribucion de la flotabilidad de las gotas
        dt = 30  #  paso temporal interno
        dcn = 20  #  cantidad de rango de gotas
        d1 = 0.0002  #  limite superior para la deriva de Stokes
        d2 = .01  #  limite inferior para el arrastre
        g = 9.8  #  aceleracion de la gravedad
        wVisc = 1.3e-6  #  viscosidad del agua
        dfac = g * (self.wRho - self.getDensity()) / self.wRho  #  tamanno de los rangos de gotas
        tempY = self.yRise(dfac, d1, d2, wVisc, Wmix / dt)  #  tamanno de las gotas para reflotar 1/2 Wmix en 1/2 dt
        dmax = tempY * (d2 - d1) + d1
        deld = dmax / dcn  #  adicionar un factor de flotabilidad
        dm0 *= deld * dmax ** 1.7 / 1.7
        return dm0

################################################

    def riseVel(
        self,
        dfac,
        d1,
        d2,
        wVisc,
        y,
        ):
        """ Metodo para el calculod e la velocidad de reflotacion de las gotas de petroleo
            dfac= g*(rhoWater-rhoOil)/(rhoWater) termino de flotabilidad
            d1 = 0.0002 #  limite superior para la deriva de Stokes
            d2 = 0.01 #  limite inferior para el arrastre
            wVisc= 1.3e-6 viscosidad del agua en  [kg/ms] 
            y=(dia-d1)/(d2-d1) diametro de las gotas escalado en el intervalo (d2-d1)
            
            **los siguientes dos metodos son empleados tambien en el calculo de 
             la velocidad de reflotacion de las gotas de petroleo y en el escalado del modelo           
        """

        if y < 0.:

            #  caso especial donde d esta en el rango de deriva de Stokes

            ds = y * (d2 - d1) + d1
            return dfac * ds * ds / (18 * wVisc)
        if y >= 1.:

            #  caso especial donde d esta en el rango de arrastre

            df = y * (d2 - d1) + d1
            return np.sqrt(8.0 * dfac * df / 3.0)
        a1 = dfac * d1 * d1 / (18 * wVisc)
        a2 = a1 * (d2 - d1) / (2.0 * d1)
        a3 = np.sqrt(8.0 * dfac * d2 / 3.0)
        a4 = a3 * (d2 - d1) / (2.0 * d2)
        c3 = 2.0 * a1 + a2 - 2.0 * a3 + a4
        c2 = -3.0 * a1 - 2.0 * a2 + 3.0 * a3 - a4
        c1 = a2
        c0 = a1
        return ((c3 * y + c2) * y + c1) * y + c0

    def riseVelP(
        self,
        dfac,
        d1,
        d2,
        wVisc,
        y,
        ):
        """ dfac= g*(rhoWater-rhoOil)/(rhoWater) termino de flotabilidad
            d1 = 0.0002 #  limite superior para la deriva de Stokes
            d2 = 0.01 #  limite inferior para el arrastre
            wVisc= 1.3e-6 viscosidad del agua en  [kg/ms] 
            y=(dia-d1)/(d2-d1) diametro de las gotas escalado en el intervalo (d2-d1) 
        """

        if y < 0.:

            #  caso especial donde d esta en el rango de deriva de Stokes

            ds = y * (d2 - d1) + d1
            return 2.0 * dfac * ds / (18 * wVisc)
        if y >= 1.:

            #  caso especial donde d esta en el rango de arrastre

            df = y * (d2 - d1) + d1
            return np.sqrt(8.0 * dfac * df / 3.0) / (2.0 * df)
        a1 = dfac * d1 * d1 / (18 * wVisc)
        a2 = a1 * (d2 - d1) / (2.0 * d1)
        a3 = np.sqrt(8.0 * dfac * d2 / 3.0)
        a4 = a3 * (d2 - d1) / (2.0 * d2)
        c3 = 2.0 * a1 + a2 - 2.0 * a3 + a4
        c2 = -3.0 * a1 - 2.0 * a2 + 3.0 * a3 - a4
        c1 = a2
        return (3.0 * c3 * y + 2.0 * c2) * y + c1

    def yRise(
        self,
        dfac,
        d1,
        d2,
        wVisc,
        w0,
        ):
        """ dfac= g*(rhoWater-rhoOil)/(rhoWater) termino de flotabilidad
            d1 = 0.0002 #  limite superior para la deriva de Stokes
            d2 = 0.01 #  limite inferior para el arrastre
            wVisc= 1.3e-6 viscosidad del agua en  [kg/ms] 
            y=(dia-d1)/(d2-d1) diametro de las gotas escalado en el intervalo (d2-d1)
        """

        y0 = 0.50
        y1 = 1.
        chk = 1.
        i = 0
        while chk > 5e-05:
            y1 = y0 + (w0 - self.riseVel(dfac, d1, d2, wVisc, y0)) \
                / self.riseVelP(dfac, d1, d2, wVisc, y0)
            chk = np.abs(y1 - y0)
            y0 = y1
            i += 1
            if i > 25:
                break
        return y1
