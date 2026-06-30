import shapefile as shp


def shapeout(out_list=None, path=None,):
    out = shp.Writer(shp.POINT)
    out.point(0, 0)
    out.point(1, 1)
    out.point(2, 2)
    out.point(3, 3)
    out.point(4, 4)
    out.point(5, 5)
    #out.field('lon', 'N')
    #out.field('lat', 'N')
    out.field('con', 'N')
    out.record()


    pass
