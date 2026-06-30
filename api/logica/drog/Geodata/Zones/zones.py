def selet_zone(xo, yo):
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib.path

    pfile=open('zonas.txt')

    zonas={}
    list_z=[]

    for line in pfile.readlines():
        if line[0]=='Z':
            zona=line[:-2]
            list_z.append(zona)
            points=[]
        elif line[0]=='[':
            a=line.split('], [')
            p= a[0][2:].split(',')
            points.append((float(p[0]),float(p[1])))
            for xy in a[1:-1]:
                p= xy.split(',')
                points.append((float(p[0]),float(p[1])))
            p= a[-1][:-3].split(',')
            points.append((float(p[0]),float(p[1])))
            zonas.__setitem__(zona, points)

    for key in list_z:
        points=zonas[key]
        path = matplotlib.path.Path(points, closed=True)
        a=[(xo,yo)]
        flag = path.contains_points(a)
        if flag:
            print(key)
            return key

    print('El derrame no se encuentra en ninguna zona de interes')
selet_zone(-88.0, 22.0)

