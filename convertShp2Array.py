from osgeo import ogr, gdal
import matplotlib.pyplot as plt
import numpy as np

def gen_raster_datasource(res_m, radius_m, centre_utm):

	pixel_width = res_m

	bbox = [centre_utm[0]-radius_m, centre_utm[0]+radius_m, centre_utm[1]-radius_m, centre_utm[1]+radius_m] 

	cols = int((bbox[1] - bbox[0]) / pixel_width)
	rows = int((bbox[3] - bbox[2]) / pixel_width)
	print(f"Size of grid (cols, rows) = ({cols}, {rows})")

	raster_ds = gdal.GetDriverByName('GTiff').Create('temp.tif', cols, rows, gdal.GDT_Byte)

	# A geotransform consists in a set of 6 coefficients:
	# GT(0) x-coordinate of the upper-left corner of the upper-left pixel.
	# GT(1) w-e pixel resolution / pixel width.
	# GT(2) row rotation (typically zero).
	# GT(3) y-coordinate of the upper-left corner of the upper-left pixel.
	# GT(4) column rotation (typically zero).
	# GT(5) n-s pixel resolution / pixel height (negative value for a north-up image).

	print(bbox[0], pixel_width, bbox[2])
	raster_ds.SetGeoTransform((bbox[0], pixel_width, 0, bbox[2], 0, pixel_width))

	return raster_ds


def ds2array(raster_ds):
	no_data = 255
	band = raster_ds.GetRasterBand(1)
	band.SetNoDataValue(no_data)
	array = band.ReadAsArray()
	array = np.where(array == no_data, -1, array)

	return array

def import_shpfile_as_array(shp_fname, attr, centre_of_view_utm, radius_m=500, res_m=1):
	shp_datasource = ogr.Open(shp_fname)
	shp_layer = shp_datasource.GetLayer()

	raster_datasource = gen_raster_datasource(res_m, radius_m, centre_of_view_utm)

	gdal.RasterizeLayer(raster_datasource, [1], shp_layer, burn_values=[1], options = [f"ATTRIBUTE={attr}"])

	array = ds2array(raster_datasource)

	return array


if __name__ == "__main__":

	shp_fname = r'./Buildings.shp'
	attr = "HEIGHT"
	centre_of_view_utm = [629908.16, 4833309.73]

	array = import_shpfile_as_array(shp_fname, attr, centre_of_view_utm)

	np.save('buildings_array.npy', array)

	# Plot
	plt.pcolormesh(array)
	plt.axis('scaled')
	plt.colorbar(label = 'Elevation (dm)')
	plt.savefig('buildings_array.png')
	plt.show()
