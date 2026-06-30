# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = 'alex'

import os

import datetime
from datetime import timedelta
from Generic import GenericFunctions as gen
import numpy as np
from Generic.paths import geo_dir


coption = ['Centro de masa',
           'Área del derrame',
           'Contacto con la costa']

def kml_simple(out_list=None, path=None, zone=None):
    import simplekml
    indextime = timedelta(hours=0)
    for idx, tr in enumerate(out_list):

        kml_file = simplekml.Kml()
        # plot normal track
        tr_lats, tr_lons = gen.Xy2Ll(tr.arr_tracks[:, 0], tr.arr_tracks[:, 1], 19.747526, -85.766569)
        for lon, lat in  zip(tr_lons, tr_lats):
            pto = kml_file.newpoint(name='', coords=[(lon, lat) ])
            pto.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/pal3/icon49.png'
            pto.style.iconstyle.scale = 0.25

        # plt mass center
        try:
            masslat, masslon  = gen.Xy2Ll(np.array([tr.masscenter[0]]), np.array([tr.masscenter[1]]), 19.747526, -85.766569)
            pto = kml_file.newpoint(name='', coords=[(masslon, masslat)])

            if idx == 0:
                pto.style.iconstyle.icon.href = 'http:// labs.google.com/ridefinder/images/mm_20_green.png'
            elif idx == out_list.__len__()-1:
                pto.style.iconstyle.icon.href = 'http:// labs.google.com/ridefinder/images/mm_20_blue.png'
            else:
                pto.style.iconstyle.icon.href = 'http:// labs.google.com/ridefinder/images/mm_20_black.png'
        except:
            pass

        pto.style.iconstyle.scale = 0.25

        # plot las particulas que se pierden del dominio
        if tr.arr_lost.size > 0:
            lost_lats, lost_lons = gen.Xy2Ll(tr.arr_lost[:, 0], tr.arr_lost[:, 1], 19.747526, -85.766569)
            for lon, lat in  zip(lost_lons, lost_lats):
                pto = kml_file.newpoint(name='', coords=[(lon, lat)])
                pto.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/pal3/icon33.png'
                pto.style.iconstyle.scale = 0.25


        indextime += timedelta(hours=1)
        # Saving the result to the disk specifying the name based on the corresponding time-step datetime.
        kml_file.save('%s/images/%s.kml' % (path,indextime))



