import os
def install_dir():
	return __file__[:-16]
	
def geo_dir():
	return os.path.join(install_dir(),'Geodata/Zones')

def shp_dir():
	return os.path.join(install_dir(),'Geodata/shp')


