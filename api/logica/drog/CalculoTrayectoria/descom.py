import numpy as np
import matplotlib.pyplot as plt



def decom1(A, xx, yy, r, nele=1000):
    space = 2*r
    lowerx = xx-r
    lowery = yy-r
    xnew = np.zeros(nele)
    ynew = np.zeros(nele)
    fig=plt.figure()
    for i in np.arange(nele):
        flag = False
        while not flag:
            xnew[i] = lowerx+space*np.random.rand()
            ynew[i] = lowery+space*np.random.rand()
            j = A(xnew[i], ynew[i])


            if np.sqrt((xnew[i]-xx)**2+(ynew[i]-yy)**2) <= r:
                if j!=-1: flag=True
    plt.savefig("figure.png")
    return xnew, ynew

def decom2(files_poligon, nele=1000):
    import numpy as np
    import matplotlib.path
    from ..Generic import GenericFunctions as gen

    pths=[]
    minsx=[]
    maxsx=[]
    minsy=[]
    maxsy=[]


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

        pths.append(matplotlib.path.Path(vert, closed=True))
        minsx.append(min(a))
        maxsx.append(max(a))
        minsy.append(min(b))
        maxsy.append(max(b))

    xnew = np.zeros(nele)
    ynew = np.zeros(nele)
    lowerx = min(minsx)
    lowery = min(minsy)
    spacex = max(maxsx)- lowerx
    spacey = max(maxsy)- lowery

    for i in np.arange(nele):
        flag = False
        while not flag:
            xnew[i] = lowerx+spacex*np.random.rand()
            ynew[i] = lowery+spacey*np.random.rand()
            for path in pths:
                flag = path.contains_points([(xnew[i], ynew[i])], radius=1e-9)
                if flag:break

    xnew, ynew  = gen.Ll2Xy(ynew, xnew, 19.747526, -85.766569)

    return xnew, ynew
