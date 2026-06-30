__author__ = 'root'
import matplotlib.tri as tri

def FindTriangleByXy(x, y, grid):
    triangles = grid.ele - 1
    #print triangles.max()
    mytri = tri.Triangulation(grid.gridx, grid.gridy, triangles)
    trap_finder = tri.TrapezoidMapTriFinder(mytri)
    element = trap_finder.__call__(x, y)
    #lo sgte plotea el mapa de la zona seleccionada a la perfeccion
    #plt.figure()
    #plt.gca().set_aspect('equal')
    #plt.triplot(grid.gridx, grid.gridy, triangles)
    #plt.title('triplot of user-specified triangulation')
    #plt.xlabel('Longitude (degrees)')
    #plt.ylabel('Latitude (degrees)')
    #
    #plt.show()
    #print "END FindTriangleByXy"

    return element, mytri


