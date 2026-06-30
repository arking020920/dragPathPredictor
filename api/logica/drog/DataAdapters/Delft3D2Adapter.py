import sys

__author__ = 'M.Sc. Dayron Chang Dominguez, Proyecto Petromar-3D v2.1, CMM INSMET, Cuba (Ene, 2021)'

"""
Petromar-3D adapter to convert Flow-uv data from Delft3D Flow model to Petromar-3D v2.1 model.

Input file is a NetCDF3-CLASSICAL file containing a Triangular Finite ELement Mesh Structure.
Important attributes are: time, mesh2d_face_x, mesh2d_face_y, mesh2d_ucx, mesh2d_ucy.

The procedure it is configured so every file of Delft3D model will contains 24h of data with a
time step of 3h including the 24h time step (Time steps are from 0h, 3h, 6h, ..., 24h). This values
could be chenged in the constructor of the class Delft3D2PetromarAdapter. The time step of Petromar
is 1h and it is given. Time step is only relevant to the time interpolation at the end of the
GetMatrix Method.

Spatial interpolacion of the currents is been made using the Inverse Distances Weighted Method with
internal KDTree (https://github.com/paulbrodersen/inverse_distance_weighting),
Linear interpolator (https://matplotlib.org/3.3.3/api/tri_api.html) on a triangular grid and
Cubic interpolator on a triangular grid (https://matplotlib.org/3.3.3/api/tri_api.html).
The Akima 1D interpolation method is been used for the time interpolation of the currents.
"""

import os
import errno
from netCDF4 import Dataset
from datetime import datetime, timedelta
import numpy as np
import Adapter
from Adapter import PetromarAssimilationError
from Generic import GenericFunctions as gen
from Generic.ColorController import Bcolors
from Generic import idw
# Loading the triangular mesh interpolator
import matplotlib.tri as tri
# Load the modules for the paralelization process
from multiprocessing import cpu_count
import thread
from threading import Thread


class FileNotFoundError(OSError):
    pass


# Locker used by the threads to access resources. This guarantee that the resource which is been locked will be
# no access from other execution thread than the one who lock it, during the use of it.
# (Used in the CubicTriangleInterp option)
locker = thread.allocate_lock()


# Thread class wrapper for cubic tri interpolation thread
class cubic_tri_interp_thread(Thread):
    def __init__(self, params, outputj):
        Thread.__init__(self)
        self.params = params
        self.outputj = outputj

    def run(self):
        # for each parameter:
        for param in self.params:
            model_data, tk, tri_finder, xx, yy = \
                param[0], param[1], param[2], param[3], param[4]

            # Acquire a lock on the netcdf file handler (model_data is a resource)
            locker.acquire()
            # Get the model uk and vk variables corresponding to the time tk
            model_uk = model_data.variables['mesh2d_ucx'][tk, :]
            model_vk = model_data.variables['mesh2d_ucy'][tk, :]
            # Release the lock on the netcdf file handler
            locker.release()

            # Get the interpolators to approximate the Petromar-3D nodes to Delft3D values
            cub_tri_u = tri.CubicTriInterpolator(tri_finder._triangulation, model_uk, kind='geom',
                                                 trifinder=tri_finder)
            cub_tri_v = tri.CubicTriInterpolator(tri_finder._triangulation, model_vk, kind='geom',
                                                 trifinder=tri_finder)

            # Do interpolation
            uk = cub_tri_u(xx, yy)
            vk = cub_tri_v(xx, yy)

            # Release memory space (*** Important ***)
            del cub_tri_u
            del cub_tri_v

            # Acquire the lock on the list of outputs. This list must to be locked in order to append information
            # to it in a save way. Otherwise, another thread could be appending new information in the same
            # spot in which the current thread is writing and could raise a runtime exception or override data.
            locker.acquire()
            # Adding results to the list
            self.outputj.append((uk, vk))
            # Release the lock on the output list
            locker.release()


def cubic_tri_interp_thread_wrapper(params, cpus=None):
    # Get the available cpus
    ncpu = cpu_count() if cpus is None else cpus

    # Tasks that have to be done (the lists inside will be empty at this moment)
    tasks = [[] for i in range(ncpu)]

    # Resulting outputs of each task (the lists inside will be empty at this moment)
    outputs = [[] for i in range(ncpu)]

    # Calculation of the amount of tasks which are divisible by ncpu.
    q = len(params) / ncpu

    # Assign q tasks to the jth cpu
    if q > 0:
        for j in range(ncpu):
            chunk = params[q * j: q * (j + 1)]
            tasks[j] += list(chunk)

    # Calculation of the rest of the tasks which are not divisible by ncpu
    r = len(params) % ncpu

    # Assign 1 tasks of r to each cpu.
    for j in range(r):
        tasks[j].append(params[q * ncpu + j])

    # List to store the threads created
    threads = []

    # Create and start the threads
    for n in range(ncpu):
        # Creating and setting up the thread
        thread = cubic_tri_interp_thread(tasks[n], outputs[n])
        # Storing the object in the list
        threads.append(thread)
        # Execute the thread
        thread.start()

    # Signal to all threads to wait for the others to finish
    for thread in threads:
        thread.join()

    # Destroy all the threads
    del threads

    # Ordered results list
    result_uv = []

    # Order the chunks divisible by ncpu
    for n in range(ncpu):
        for uv in outputs[n][0: q * ncpu]:
            result_uv.append(uv)

    # Add the rests to the result
    for j in range(r):
        result_uv.append(outputs[j][-1])

    return result_uv


class Delft3D2PetromarAdapter(Adapter.Adapter):
    # constructor
    def __init__(self, dir_esc, model_type, fecha_inicio, cant_dias, model_name, input_data):
        Adapter.Adapter.__init__(self, dir_esc, model_type, fecha_inicio, cant_dias, input_data)
        self.model_name = model_name
        self.inpath = input_data['General']['model_data']
        # The time step it will be assumed from the Delft3D files. (In seconds) (1h ~ 3600s, 3h ~ 10800s)
        self.time_step = 10800
        # The total time in seconds contained in the Delft3D file
        self.total_time = 24 * 60 ** 2
        # Postfix string expression which is a constant part of the filename of Delft3D data files
        self.filename_postfix = '_0000_Delft3D_t24h_dt3h.nc'

        self.spatial_interpolator = input_data['Adapter']['spatial_interpolator']  # ['CubicTriangleInterp',
        # 'LinearTriangleInterp', 'IDW']

        self.kind = input_data['Adapter']['kind'] if self.spatial_interpolator == 'CubicTriangleInterp' else None
        ## ['min_E', 'geom']

        # Number of CPUs will be used for the cubic interpolator
        self.ncpu = input_data['Adapter']['ncpu'] if self.spatial_interpolator == 'CubicTriangleInterp' else None

    def GetMatrix(self, nodes, delta_t, det_recep):
        # Get the path of the data file of Delft3D
        path = '%s/%s/%s' % (self.inpath, self.model_type, self.model_name)

        # Get the initial datetime of the data
        date = datetime.strptime(self.fecha_inicio, '%d/%m/%Y')
        start_date = date

        # Check the existence of the path
        if os.path.isdir(path):
            # Get the ids of the Petromar-3D nodes
            nodes_id = nodes[:, 0]

            # Set the matrix resulting of the column vector of the nodes ids and all time pairs u,v of
            # Delft3D uv data interpolated to the Petromar-3D nodes, stack as vertical columns to the right
            # (id, u0, v0, u1, v1, ..., uN, vN).
            uv_column_stacked = np.copy(nodes_id)

            # Will contains the final u,v data in nodes and time steps of Petromar-3D
            uv_petromar = np.copy(nodes_id)

            # Get nodes of the triangular finite elements mesh of Petromar-3D
            xx = nodes[:, 1]
            yy = nodes[:, 2]

            # Convert the plain coordenates of the Petromar mesh to geographics
            yy, xx = gen.Xy2Ll(xx, yy, 19.747526, -85.766569)

            # This is the offset that will be taking out of the bounding box to guarantee Petromar-3D nodes
            # will have always values available from the Delft3D mesh. The distance is measured in degrees
            offset = 0.62

            # Get the bounding box of the Petromar-3D domain mesh
            x_min, x_max = np.min(xx) + offset, np.max(xx) + offset
            y_min, y_max = np.min(yy) + offset, np.max(yy) + offset

            # Variable to save the default Deflt3D time step. It will be updated later
            delft3d_dt = self.time_step

            print Bcolors.OKBLUE + '> Spatial interpolation with %s method...' % (self.spatial_interpolator) \
                  + Bcolors.ENDC

            # Iterate over the time period from start_date to start_date+cant_dias
            for dk in range(self.cant_dias):
                # Get the datetime of the next Delft3D data to try to load the file
                date = start_date + timedelta(days=dk)

                # Construct the filename of the Delft3D data file corresponding to that date
                model_filename = '%s/%04d-%02d-%02d%s' % (path, date.year, date.month, date.day, self.filename_postfix)

                print '> Processing datetime: ' + Bcolors.UNDERLINE + date.strftime(
                    '%d/%m/%Y %H:%M:%S') + Bcolors.ENDC + \
                      '. Openning file:' + Bcolors.UNDERLINE + model_filename + Bcolors.ENDC

                # Raise an Exception if the file does not exists
                if not os.path.isfile(model_filename):
                    raise IOError('%s. %s' % (os.strerror(errno.ENOENT), model_filename,))

                # Otherwise prosed to process the data

                # Open NetCDF4 file
                try:
                    model_data = Dataset(model_filename, "r")
                except Exception as e:
                    raise PetromarAssimilationError(
                        "Problem openning NetCDF file of Delft3D current model. >>> '%s'" % (e,))

                # Get longitudes and latitudes of the reference points of the triangles faces
                lon = model_data.variables['mesh2d_face_x'][:]
                lat = model_data.variables['mesh2d_face_y'][:]

                # Reduce the domain area to a sub-domain which bounds the Petromar-3D domain. Get the indexes
                # of the points inside the bounding box calculated.
                lon_idx = np.where((lon >= x_min) * (lon <= x_max))[0]
                lat_idx = np.where((lat >= y_min) * (lat <= y_max))[0]

                # Check if the Petromar-3D domain is a subdomain of the Delft3D model
                if lon_idx.shape[0] == 0 or lat_idx.shape[0] == 0:
                    raise PetromarAssimilationError('Petromar-3D subdomain out of the bounding box of Delft3D domain.')

                # Get indexes of the coordinates which satisfy the bounding box
                coord_idx = np.intersect1d(lat_idx, lon_idx)

                # Get the coordinates which satisfy the bounding box
                lon_bnd = lon[coord_idx]
                lat_bnd = lat[coord_idx]

                # Set the time loop

                # Get the time vector
                model_time = model_data.variables['time'][:]

                # TODO Chech the first time step setup to 0. I think is better to deleted from the file in a previous process

                # Update the model time step default with the real. The time is in seconds.
                # A regular fixed time step is expected.
                # delft3d_dt = np.int(np.abs(model_time[1] - model_time[0]))
                delft3d_dt = np.int(np.abs(model_time[2] - model_time[1]))  # For testing!!!!

                # Assert if the data file is from 0 hour to 23 hours (total of 24h) at least.
                # -> The (model_time.shape[0] - 1) =: |T|, means the number of time steps.
                # -> delft3d_dt =: dt in seconds so, (delft3d_dt / 3600.0) is the dt in hours.
                # -> self.total_time / 3600 is the expected 24h time covered by the data file. Like a threshold
                #                           of 24h in which will work (0h to 23h).
                assert ((model_time.shape[0] - 1) * delft3d_dt / 3600.0 - self.total_time / 3600) >= 0.0, \
                    Bcolors.FAIL + 'Delft3D data file does not has 24h of time steps.' + Bcolors.ENDC

                # Raise a warning if data file has more than 24h of run.
                if ((model_time.shape[0] - 1) * delft3d_dt / 3600.0 - self.total_time / 3600) > 0.0:
                    print Bcolors.WARNING + 'WARNING: Delft3D data file has more than 24h of time steps! ' \
                                            'Only the first 24h will be considered.' + Bcolors.ENDC

                # TODO Use just 24h if the file is bigger.

                # Check self.time_step it is setup in a right way according to the real data on the file
                if delft3d_dt != self.time_step:
                    raise PetromarAssimilationError('Delft3D time steps are %d sec and the adapter time '
                                                    'step is %d sec.' % (delft3d_dt, self.time_step))

                # Initialization of triangular interpolation algorithms
                tri_finder = None

                # If the spatial interpolator is a triangulation then
                if self.spatial_interpolator == 'CubicTriangleInterp' or \
                                self.spatial_interpolator == 'LinearTriangleInterp':
                    # Create a Delaunay triangulation
                    triangulation = tri.Triangulation(lon, lat)
                    # Create a data structure to find triangles
                    tri_finder = tri.TrapezoidMapTriFinder(triangulation)

                # If the method is the cubic triangle interpolation on a Delaunay surface then do it Parallel
                if self.spatial_interpolator == 'CubicTriangleInterp':

                    print Bcolors.OKBLUE + '> Delaunay triangulation created.\n> Interpolating ...' + Bcolors.ENDC

                    # Params to be used by the paralelization algorithm. (netcdf_handler, time, tri_surface_handler
                    #                                                     x_interp_point, y_interp_point)
                    params = [(model_data, tk, tri_finder, xx, yy) for tk in range(model_time.shape[0])]

                    # Call the method CubicTriInterpolatorThreadWrapper which is a wrapper for the paralelization.
                    # the result_uv contains a list of length T, of arrays (N, 2). Each array contains two vectors
                    # of the interpolated x and y dimensions for the correspondent tk.
                    result_uv = cubic_tri_interp_thread_wrapper(params, self.ncpu)

                    # Stack the new interpolated uv currents at the right side of the ndarray for this time step.
                    # This process will be cumulative.
                    for w in result_uv:
                        uv_column_stacked = np.column_stack((uv_column_stacked, w[0], w[1]))
                else:
                    # Iterate over the time variable of the Delft3D file data. The following algorithms are sequential.
                    for tk in range(model_time.shape[0]):

                        uk, vk = [], []

                        if self.spatial_interpolator == 'IDW':
                            # Get the velocities of the selected coordinates in the current time step
                            model_uk = model_data.variables['mesh2d_ucx'][tk, coord_idx]
                            model_vk = model_data.variables['mesh2d_ucy'][tk, coord_idx]

                            # Get the interpolators to approximate the Petromar-3D nodes to Delft3D values
                            idw_tree_u = idw.tree(np.column_stack((lon_bnd, lat_bnd)), model_uk)
                            idw_tree_v = idw.tree(np.column_stack((lon_bnd, lat_bnd)), model_vk)

                            # Interpolate the Approximation of Delft3D values in the Petromar-3D nodes (xx, yy)
                            uk = idw_tree_u(np.column_stack((xx, yy)))
                            vk = idw_tree_v(np.column_stack((xx, yy)))

                            del idw_tree_u
                            del idw_tree_v

                            # elif self.spatial_interpolator == 'CubicTriangleInterp':
                            #     # Get the velocities of the coordinates in the current time step
                            #     model_uk = model_data.variables['mesh2d_ucx'][tk, :]
                            #     model_vk = model_data.variables['mesh2d_ucy'][tk, :]

                            # # Get the interpolators to approximate the Petromar-3D nodes to Delft3D values
                            # cub_tri_u = tri.CubicTriInterpolator(tri_finder._triangulation, model_uk, kind=self.kind,
                            #                                      trifinder=tri_finder)
                            # cub_tri_v = tri.CubicTriInterpolator(tri_finder._triangulation, model_vk, kind=self.kind,
                            #                                      trifinder=tri_finder)
                            #
                            # uk = cub_tri_u(xx, yy)
                            # vk = cub_tri_v(xx, yy)
                            #
                            # del cub_tri_u
                            # del cub_tri_v

                        elif self.spatial_interpolator == 'LinearTriangleInterp':
                            print Bcolors.OKBLUE + '> Delaunay triangulation created.\n> Interpolating ...' + Bcolors.ENDC

                            # Get the velocities of the coordinates in the current time step
                            model_uk = model_data.variables['mesh2d_ucx'][tk, :]
                            model_vk = model_data.variables['mesh2d_ucy'][tk, :]

                            # Get the interpolators to approximate the Petromar-3D nodes to Delft3D values
                            lin_tri_u = tri.LinearTriInterpolator(tri_finder._triangulation, model_uk,
                                                                  trifinder=tri_finder)
                            lin_tri_v = tri.LinearTriInterpolator(tri_finder._triangulation, model_vk,
                                                                  trifinder=tri_finder)

                            uk = lin_tri_u(xx, yy)
                            vk = lin_tri_v(xx, yy)

                            del lin_tri_u
                            del lin_tri_v

                        # Stack the new interpolated uv currents at the right side of the ndarray for this time step.
                        # This process will be cumulative.
                        uv_column_stacked = np.column_stack((uv_column_stacked, uk, vk))

                # Close the file since all data were extracted
                model_data.close()

            # Check if the time steps are correct for Petromar-3D (Which uses a time step equals to 1h ~ 3600).
            # Otherwise, do time interpolation.

            # Alternatives. delta_t is considered the Petromar time step and it is assumed to be 1h

            print Bcolors.OKBLUE + '> Time interpolation ...' + Bcolors.ENDC

            # Converting delta_t from hours to seconds
            delta_t *= 60 ** 2

            # Delft3D_dt < Petromar_dt and Petromar_dt congruent 0 mod Delft3D_dt. (Equality it is consider in the
            # second condition)
            if delta_t % self.time_step == 0 and self.time_step < delta_t:
                # Petromar_dt = q * Delft3D_dt + 0. Get the q constant to know what is the jump we need to make
                # to pick only the columns of the model Delft3D which match with the Petromar_dt.
                q = delta_t / self.time_step

                # Iterate over the amount of time jumps it will be needed, which is total days times total time
                # per day divided by the constant q.
                for k in range(self.cant_dias * model_time.shape[0] / q):
                    # The columns are picked with jumps of size q by k. the addition of 1 and 2 is because
                    # the first column is the nodes_id column, so u_{k*q} and v_{k*q} are lagged by 1.
                    uv_petromar = np.column_stack((uv_petromar,
                                                   uv_column_stacked[:, k * q + 1],
                                                   uv_column_stacked[:, k * q + 2]))
            else:
                # Delft3D_dt > Petromar_dt and (DelftD3_dt < Petromar_dt non-congruent)
                # All times are in seconds.
                petromar_t, uv_petromar = gen.currents_spline_time_interp1d(uv_column_stacked, delta_t, self.time_step,
                                                                            (self.cant_dias * self.total_time))

            # Free the memory of uv_column_stacked
            del uv_column_stacked

            if not det_recep:
                uv_time_inverted = np.copy(uv_petromar)
                # Invert the order of the u-component vector of the Stack Matrix uv_petromar
                # The indexer reads as follows: The columns of uv_time_inverted from the idx=1, two by two, will be
                # replaced by the columns of uv_petromar taken inversely from the column before the last column,
                # two by two.
                uv_time_inverted[:, 1::2] = uv_petromar[:, -2:0:-2]

                # Invert the order of the v-component vector of the Stack Matrix uv_petromar
                # The indexer reads as follows: The columns of uv_time_inverted from idx=2, two by two, will be
                # replaced by the columns of uv_petromar taken inversely from the last column, two by two.
                uv_time_inverted[:, 2::2] = uv_petromar[:, -1:1:-2]

                # Assign the inverted stack matrix to uv_petromar stack matrix
                uv_petromar = np.copy(uv_time_inverted)

                # Free memory space
                del uv_time_inverted

            # Save the interpolated in space and time current data for Petromar-3D into a csv file
            np.savetxt('%s/uv_corr.txt' % self.dir_esc, uv_petromar)
            # Get the final date of the data available in uv_petromar stack matrix
            final_date = start_date + timedelta(days=self.cant_dias)

            print Bcolors.OKBLUE + '> Space and time interpolated mesh saved to %s%s/uv_corr.txt' \
                                   % (Bcolors.UNDERLINE, self.dir_esc,) + Bcolors.ENDC

            # Return the final date in a spanish format, the dt of Petromar-3D, start date and the stack matrix
            # with u,v data.
            return final_date.strftime('%d/%m/%Y'), delta_t, start_date, uv_petromar

        else:
            raise PetromarAssimilationError("Directorio de modelo incorrecto. " \
                                            "Fallo al intentar cargar '%s' del tipo de modelo de '%s' '%s'" % (
                                                path, self.model_type,
                                                self.model_name))
