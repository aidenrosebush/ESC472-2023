from osgeo import ogr, gdal
import numpy.typing as npt
import numpy as np

class Bbox:

	def __init__(self, centre:list, radius:int|float):
		self.centre = centre
		self.xmax = centre[0] + radius
		self.xmin = centre[0] - radius
		self.ymax = centre[1] + radius
		self.ymin = centre[1] - radius

	def transform(self, transformer:callable):
		topleft = transformer( self.xmin, self.ymin )
		bottomright = transformer( self.xmax, self.ymax )

		self.xmax = bottomright[0]
		self.xmin = topleft[0]
		self.ymax = bottomright[1]
		self.ymin = topleft[1]


def gen_raster_datasource(bbox:type(Bbox), nrows:int, ncols:int) -> gdal.Dataset:

	res_ns = int((bbox.ymax - bbox.ymin) / nrows)
	res_we = int((bbox.xmax - bbox.xmin) / ncols)

	raster_ds = gdal.GetDriverByName('GTiff').Create('temp.tif', ncols, nrows, gdal.GDT_Byte)

	"""
	A geotransform consists in a set of 6 coefficients:
	GT(0) x-coordinate of the upper-left corner of the upper-left pixel.
	GT(1) w-e pixel resolution / pixel width.
	GT(2) row rotation (typically zero).
	GT(3) y-coordinate of the upper-left corner of the upper-left pixel.
	GT(4) column rotation (typically zero).
	GT(5) n-s pixel resolution / pixel height (negative value for a north-up image).
	"""

	raster_ds.SetGeoTransform((bbox.xmin, res_we, 0, bbox.ymin, 0, res_ns))

	return raster_ds


def ds2array(raster_ds) -> npt.ArrayLike:
	no_data = 255
	band = raster_ds.GetRasterBand(1)
	band.SetNoDataValue(no_data)
	array = band.ReadAsArray()
	array = np.where(array == no_data, -1, array)

	return array


def import_shpfile_as_array(shp_fname:str, attr:str, bbox:type(Bbox), nrows:int = 200, ncols:int = 200) -> np.typing.ArrayLike:
	shp_datasource = ogr.Open(shp_fname)
	shp_layer = shp_datasource.GetLayer()

	raster_datasource = gen_raster_datasource(bbox, nrows, ncols)
	gdal.RasterizeLayer(raster_datasource, [1], shp_layer, burn_values=[1], options = [f"ATTRIBUTE={attr}"])

	array = ds2array(raster_datasource)

	return array


def import_tif_as_array(tif_fname:str, bbox:type(Bbox), nrows:int=200, ncols:int=200) -> np.typing.ArrayLike:

	src_raster_ds = gdal.Open('/home/jasperh/esc472/dtm_1m_utm17_e_12_83.tif', gdal.GA_ReadOnly)
	dst_raster_ds = gen_raster_datasource(bbox, nrows, ncols)
	gdal.Warp(dst_raster_ds, src_raster_ds)
	
	array = ds2array(dst_raster_ds)

	return array

def plot_array(A:np.typing.ArrayLike):
	plt.pcolormesh(A)
	plt.axis('scaled')
	plt.colorbar(label = 'Elevation (m)')

	plt.show()


if __name__ == "__main__":

	import matplotlib.pyplot as plt
	from pyproj import Transformer
	import copy

	"""
	wmerc refers to webmercator or wgs84 psuedo mercator, EPSG3857
	utm refers to wgs84 utm 17N, EPSG32617
	the building height file uses the pseudo mercator co-ordinate reference system (crs)
	the terrain file uses utm as its crs
	"""

	wmerc2utm = Transformer.from_crs("EPSG:3857","EPSG:32617")
	utm2wmerc = Transformer.from_crs("EPSG:32617","EPSG:3857")

	centre_wmerc = [-8837768.68,5410177.27]

	centre_utm = wmerc2utm.transform(*centre_wmerc)
	radius_utm = 250
	bbox_utm = Bbox(centre_utm, radius_utm)

	bbox_wmerc = copy.copy(bbox_utm)
	bbox_wmerc.transform( utm2wmerc.transform )

	building_array = import_shpfile_as_array("./toronto_3d_massing/3DMassingShapefile_2022_WGS84.shp", "AVG_HEIGHT", bbox_wmerc)
	dtm_array = import_tif_as_array("./dtm_1m_utm17_e_12_83.tif",bbox_utm)

	total_elevation = building_array + dtm_array

	plot_array(building_array)
	plot_array(dtm_array)
	plot_array(total_elevation)
