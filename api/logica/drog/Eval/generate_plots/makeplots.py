__autor__ = 'ivand'
import plot_track, plot_all, plot2_all, plot2_track, coptions, simple_track, simple_all, plot_lost, weathering_plot, plot_mariel, simple_track_brasil, fancy_plot
import cPickle

def makeplots (config, plots = None):

    out_dir = config['General']['output_data']
    sce_name = config['Model']['nombre_escenario']
    track_name = config['Model']['nombre_trayectoria']
    vol = config['Model']['volumen']
    plots = config['Model']['plots']
    track_path = out_dir + '/' + sce_name + '/tracks/' + track_name
    sce_file = out_dir + '/' + sce_name + '/' + sce_name + '.esc'

    sce_f = open(sce_file)
    esc_conf = sce_f.readline().split('-')
    sce_f.close()
    zone = esc_conf[0]
    datafile = open(track_path+'/save.pk')
    data = cPickle.load(datafile)
    datafile.close()


    if plots == 'simple':
        simple_all.simple_all(zone=zone, out_list=data, path=track_path)
        #coptions.plot_coption(zone=zone, out_list=data, path=track_path)
    elif plots == 'all':
        plot2_all.plot2_all(out_list=data,path=track_path,zone=zone)
        simple_track.simple_track(out_list=data,path=track_path,zone=zone)
        simple_all.simple_all(out_list=data,path=track_path,zone=zone)
        weathering_plot.plot_conc(vol,out_list=data,path=track_path)
        weathering_plot.plot_thick(out_list=data,path=track_path,zone=zone)
        plot_lost.plot_lost(out_list=data, path=track_path, zone=zone)
        coptions.plot_coption(out_list=data,path=track_path,zone=zone)
    elif plots == 'email':
        simple_all.simple_all() #TODO cambiar por fancy
        weathering_plot.plot_conc()
        plot_lost.plot_lost()
    elif plots == 'simple_track_brasil':
        simple_track_brasil.simple_track(out_list=data, path=track_path, zone=zone)
    elif plots == 'simple_track':
        #simple_track_brasil.simple_track(out_list=data, path=track_path, zone=zone)
        simple_track.simple_track(out_list=data, path=track_path, zone=zone)
    elif plots == 'fancy_plot':
        fancy_plot.fancy_plot(out_list=None, path=None, zone=None)