__author__ = 'frank'
import numpy as np

def coef_v(wind):
    wind_mag = np.sqrt(wind[:, 0]**2+wind[:, 1]**2)
    for i in np.arange(wind_mag.size):
        if wind_mag[i] <= 1.:
            wind_mag[i] = 0.5*np.sqrt(wind_mag[i])*0.001
        elif wind_mag[i] <= 15.:
            wind_mag[i] = (0.8+0.065*wind_mag[i])*0.001
        else:
            wind_mag[i] = 2.26*0.001 #revisar
    return wind_mag

def CalcVelTotal(esc_path, det_recep, zona_s, cant_dias):
    import os
    from Generic import GenericFunctions as gen
    imposed_type = ['lluvioso', 'poco_lluvioso', 'frente_frio', 'sur', 'huracan']
    impo = ''

    # preguntar y obtener la matriz de la corriente, hacer lo mismo con el viento y el oleaje en el futuro
    coef0 = 1.2

    coef_c = 1.1

    if os.path.exists(esc_path+'/uv_corr.txt'):
        uv_corr = np.loadtxt(esc_path+'/uv_corr.txt')
        if impo in imposed_type:
            imposed_nodes, imposed_vel = gen.imposed_data(zona_s, np.int(cant_dias), impo)
            uv_corr[np.int32(imposed_nodes[:, 0]) - 1, 1:] = imposed_vel
        vel_total = np.zeros(shape=uv_corr.shape)
    if os.path.exists(esc_path + '/uv_viento.txt'):
        uv_viento = np.loadtxt(esc_path + '/uv_viento.txt')
        #for i in range(0, uv_viento.shape[0]):

        for i in np.arange(1, uv_viento.shape[1] - 1, 2):
            vel_total[:, i] = coef_c * uv_corr[:, i] + coef_v(uv_viento[:, i:i+2]) * uv_viento[:, i]
            vel_total[:, i+1] = coef_c * uv_corr[:, i+1] + coef_v(uv_viento[:, i:i+2]) * uv_viento[:, i+1]
            #vel_total[:, i] = uv_corr[:, i] + 0.1 * uv_viento[:, i]
            #vel_total[:, i+1] = uv_corr[:, i+1] + 0.1 * uv_viento[:, i+1]
    else:
        vel_total[:, 1:] = coef0 * uv_corr[:, 1:]
    # imprimir el fichero de la uv.txt final
    np.savetxt(esc_path + '/uv.txt', det_recep*vel_total)
    print("END CalcVelTotal")
    return det_recep*vel_total
