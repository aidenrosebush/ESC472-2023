from osgeo import ogr, gdal
import matplotlib.pyplot as plt
import numpy as np

# Location of shapefile
vector_fn = '.\\Buildings\\Buildings.shp'

# Define pixel_size and NoData value of new raster
pixel_width = 1 # resolution in meters
NoData_value = 255 # positive value only, changed to -1 later in code

# TODO: See if we could read in only the extent needed
# Open the data source and read in the extent
source_ds = ogr.Open(vector_fn)
source_layer = source_ds.GetLayer()
source_srs = source_layer.GetSpatialRef()
x_min, x_max, y_min, y_max = source_layer.GetExtent()

# Setting extent
# Note: utm coordinate system
radius = 500 # meters
obs_point = [629908.16, 4833309.73] # Rogers Centre
# bounding box [xmin, xmax, ymin, ymax]
bbox = [obs_point[0]-radius, obs_point[0]+radius, obs_point[1]-radius, obs_point[1]+radius] 

# Create the destination data source
cols = int((bbox[1] - bbox[0]) / pixel_width)
rows = int((bbox[3] - bbox[2]) / pixel_width)
print(f'Size of grid (cols, rows) = ({cols}, {rows})')

# Create Raster file
target_ds = gdal.GetDriverByName('GTiff').Create('temp.tif', cols, rows, gdal.GDT_Byte)

# A geotransform consists in a set of 6 coefficients:
# GT(0) x-coordinate of the upper-left corner of the upper-left pixel.
# GT(1) w-e pixel resolution / pixel width.
# GT(2) row rotation (typically zero).
# GT(3) y-coordinate of the upper-left corner of the upper-left pixel.
# GT(4) column rotation (typically zero).
# GT(5) n-s pixel resolution / pixel height (negative value for a north-up image).
target_ds.SetGeoTransform((bbox[0], pixel_width, 0, bbox[2], 0, pixel_width))
band = target_ds.GetRasterBand(1)
band.SetNoDataValue(NoData_value)

# Rasterize
# Note: May need to change ATTRIBUTE depending on data set
gdal.RasterizeLayer(target_ds, [1], source_layer, burn_values=[1], options = ['ATTRIBUTE=HEIGHT'])

# Read as array
array = band.ReadAsArray()
array = np.where(array == NoData_value, -1, array)
np.save('buildings_array.npy', array)
#print(array)

# Plot
plt.pcolormesh(array)
plt.axis('scaled')
plt.colorbar(label = 'Elevation (dm)')
plt.savefig('buildings_array.png')
plt.show()