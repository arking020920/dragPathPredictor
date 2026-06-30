import numpy as np
import matplotlib.pyplot as plt



def decom2(xx, yy, r, nele=1000):
    xnew = np.zeros(nele)
    ynew = np.zeros(nele)

    for i in np.arange(nele):
        flag = False
        while not flag:
            dx=r*(2*np.random.rand()-1)
            dy=r*(2*np.random.rand()-1)

            xnew[i] = xx+dx
            ynew[i] = yy+dy

            #plt.plot(xx, yy, 'bo')
            #plt.plot(xnew[i],ynew[i], 'ro')
            #print np.sqrt(xnew[i]**2+ynew[i]**2), r

            if dx**2+dy**2 <= r**2:
                flag = True
    return xnew, ynew
