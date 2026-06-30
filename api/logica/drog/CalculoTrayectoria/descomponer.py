import numpy as np
import matplotlib.pyplot as plt

def decom1(A, xx, yy, r, dxdy=.111):

    xnew = []
    ynew = []
    rcor=int(r/dxdy)*dxdy
    for x in np.arange(xx-rcor, xx+r, dxdy):
        for y in np.arange(yy-rcor, yy+r, dxdy):
            if np.sqrt((x-xx)**2+(y-yy)**2) <= r:
                j = A(x, y)
                if j!=-1:
                    xnew.append(x)
                    ynew.append(y)

    return np.array(xnew), np.array(ynew)

def decom2(files_poligon, dxdy=.001):
    import numpy as np
    import matplotlib.path
    from Generic import GenericFunctions as gen

    for file_poligon in files_poligon:
        pfile=open(file_poligon)
        vert=[]
        for line in pfile.readlines():
            a=line.split(',')
            vert.append((float(a[0].split(' ')[3]), float(a[0].split(' ')[4])))
            vert.append((float(a[1].split(' ')[1]), float(a[1].split(' ')[2])))

        a=[]
        b=[]
        for poly in vert:
            a.append(poly[0])
            b.append(poly[1])

        A= matplotlib.path.Path(vert, closed=True)
        xnew = []
        ynew = []
        for x in np.arange(np.min(a), np.max(a), dxdy):
            for y in np.arange(np.min(b), np.max(b), dxdy):
                if A.contains_points([(x, y)], radius=1e-9):
                    xnew.append(x)
                    ynew.append(y)

    return gen.Ll2Xy(np.array(ynew), np.array(xnew), 19.747526, -85.766569)

