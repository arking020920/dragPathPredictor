__autor__ = 'ivand-alex-amilcar'
from . import plot_track, plot_all, plot2_all, plot2_track, coptions, fancy_plot, simple_track, simple_all, plot_lost, \
    weathering_plot, plot_mariel, simple_track_currents, simple_track_vectors, simple_current_drift, kml_all, kml_simple
import _pickle as cPickle
from Generic.ColorController import Bcolors


def makeplots(config, plots= None):
    out_dir = config['General']['output_data']
    sce_name = config['Model']['nombre_escenario']
    track_name = config['Model']['nombre_trayectoria']
    vol = config['Model']['volumen']
    track_path = out_dir + '/' + sce_name + '/tracks/' + track_name
    sce_file=r'D:\Escenarios\ENE2024-040506-BACK\ENE2024-040506-BACK.esc'
    #sce_file = out_dir + '/' + sce_name + '/' + sce_name + '.esc'

    if plots is None:
        plots = config['Model']['plots']

    sce_f = open(sce_file)
    esc_conf = sce_f.readline().split('-')
    sce_f.close()
    zone = esc_conf[0]
    
    try:
        datafile = open(r'D:\Escenarios\ENE2024-040506-BACK\tracks\TestMiguel'
 + r'\save.pk', 'rb')
    except EOFError:
        print('Data no found, check config file section run parameters: create_esc, get_esc')

    data = cPickle.load(datafile)
    datafile.close()

    if plots == 'fancy_plot':
        fancy_plot.fancy_plot(zone=zone, out_list=data, path=track_path)
    elif plots == 'coption':
        coptions.plot_coption(zone=zone, out_list=data, path=track_path)
    elif plots == 'email':
        simple_all.simple_all(zone=zone, out_list=data, path=track_path)  # TODO cambiar por fancy
        #weathering_plot.plot_conc(vol=vol,out_list = data,path=track_path,zone=zone)
        #plot_lost.plot_lost(zone=zone, out_list=data, path=track_path)
    elif plots == 'kml_all':
        kml_all.kml_all(zone=zone, out_list=data, path=track_path)
    elif plots == 'kml_simple':
        kml_simple.kml_simple(zone=zone, out_list=data, path=track_path)
    elif plots == 'simple':
        simple_all.simple_all(zone=zone, out_list=data, path=track_path)
        kml_all.kml_all(zone=zone, out_list=data, path=track_path)
    elif plots == 'simple_track':
        simple_track.simple_track(zone=zone, out_list=data, path=track_path)
    elif plots == 'simple_current_drift':
        print (Bcolors.OKBLUE + '> Saving plots to folder: ' + Bcolors.UNDERLINE + track_path + '/images' + Bcolors.ENDC)
        simple_current_drift.simple_track(out_list=data, path=track_path, zone=zone)
        #weathering_plot.plot_conc(vol=vol, out_list=data, path=track_path, zone=zone)
        #weathering_plot.plot_thick(out_list=data, path=track_path, zone=zone)
        #weathering_plot.plot_rho(out_list=data, path=track_path, zone=zone)
        #weathering_plot.plotBudget(vol=vol, out_list=data, path=track_path, zone=zone)
        #weathering_plot.plot1D(vol=vol, out_list=data, path=track_path, zone=zone)
    elif plots == 'all':
        weathering_plot.plot_conc(vol=vol,out_list = data,path=track_path,zone=zone)
        weathering_plot.plot_thick(out_list = data,path=track_path,zone=zone)
        #weathering_plot.plot_rho(out_list=data, path=track_path, zone=zone)
        #weathering_plot.plotBudget(vol=vol, out_list=data, path=track_path, zone=zone)
        #weathering_plot.plot1D(vol=vol, out_list=data, path=track_path, zone=zone)
        simple_current_drift.simple_track(out_list=data, path=track_path, zone=zone)
        simple_track_currents.simple_track(zone=zone, out_list=data, path=track_path)
        kml_all.kml_all(zone=zone, out_list=data, path=track_path)
        simple_all.simple_all(zone=zone, out_list=data, path=track_path)
        
    return kml_all.kml_all(zone=zone, out_list=data, path=track_path)

