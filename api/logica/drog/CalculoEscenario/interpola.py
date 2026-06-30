__author__ = 'frank'
import os, numpy as np

def Interpola2d(grid, x, y):
    # interpolar punto a punto, lograr hacer una interpolacion explain
    grid = grid.transpose()

    xs = grid[1:(grid.shape)[0],0]
    # xs = np.zeros(5)
    ys = grid[0,1:(grid.shape)[0]]
    z = 0
    ix1 = np.array(np.where(xs > x))
    a = ix1.shape
    if ix1.shape[1] > 0:
        i = ix1[0,0] - 1
        # if i < 1:
        #     i = 1
        iy1 = np.array(np.where(ys > y))
        if iy1.shape[1] > 0:
            j = iy1[0,0] - 1
            # if j < 1:
            #     j = 1
            # b = i + 1
            dx = xs[i + 1] - xs[i]
            dy = ys[j + 1] - ys[j]

            clat = (y - ys[j]) / dy
            clon = (x - xs[i]) / dx

            i += 1
            j += 1
            #poner el conmtrol de abajo (-100:100) como general
            if -100 < grid[i,j] < 100 and -100 < grid[i+1,j] < 100 and -100 < grid[i,j+1] < 100 and -100 < grid[i+1,j+1] < 100:
                    z = ((1 - clat) * (1 - clon) * grid[i,j]) + ((1 - clat) * clon * grid[i + 1, j]) + (clat * clon * grid[i + 1,j + 1]) + (clat * (1 - clon) * grid[i,j+1])
    return z
    # print "END Interpola2d"

def VelInterp_Interm(vel_interp, dt):
    # interpolar en el tiempo en dependencia del modelo
    result = vel_interp[:,0]
    sy = vel_interp.shape[1]
    interp_time = 6 if dt == 24 else 1
    for j in range(1,sy - 3,2):
        result = np.column_stack([result,vel_interp[:,[j,j+1]]])
        for i in range(interp_time, (dt - (interp_time - 1)), interp_time):

            #tfac1 = float(i/dt)
            #tfac2 = float(1 - tfac1)
            tfac1 = float(i) / float(dt)
            tfac2 = float(1) - tfac1
            ut = tfac1 * vel_interp[:,j+2] + tfac2 * vel_interp[:,j]
            vt = tfac1 * vel_interp[:,j+3] + tfac2 * vel_interp[:,j+1]
            result = np.column_stack([result,ut])
            result = np.column_stack([result,vt])

    result = np.column_stack([result,vel_interp[:,[(vel_interp.shape[1] - 2),vel_interp.shape[1] - 1]]])
    return result
    print "END VelInterp_Interm"




def Interpolar(temp_path, nodes, cant_dias, path, model_type, dt):
    # datav = []
    # sz = (nodes.shape)[0]
    interpol = nodes[:,0]
    nodes = nodes[:,[1,2]]
    # cant_files = 0
    lista = os.listdir(temp_path)
    f = []
    for name_file in sorted(os.listdir(temp_path)):
        # print name_file.find('u')
        # print name_file.find('v')
        if (name_file.find('u') != -1) or (name_file.find('v') != -1):
            data = np.loadtxt(temp_path + '/' + name_file)
            f = []
            for j in range(nodes.shape[0]):
                x = nodes[j,0]
                y = nodes[j,1]
                f.append(Interpola2d(data, x, y))
            interpol = np.column_stack([interpol,f])
            # cant_files += 1
    # para coastwatch el dt = 24, para roms es 6, despues se pregunta para otros modelos

    interpol = VelInterp_Interm(interpol, dt)
    np.savetxt(path + '/uv_'+model_type+'.txt', interpol)
    # codigo q hay q preguntarle a amilcar
    import shutil as sh
    sh.rmtree(temp_path)


    # print 'END Interpolar'
