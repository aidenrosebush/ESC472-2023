from pyproj import Transformer
import copy
import convertShp2Array as shp2array
import viewshed_los_fast as viewshed
import matplotlib.pyplot as plt

"""
wmerc refers to webmercator or wgs84 psuedo mercator, EPSG3857
utm refers to wgs84 utm 17N, EPSG32617
the building height file uses the pseudo mercator co-ordinate reference system (crs)
the terrain file uses utm as its crs
"""

scale = 10

wmerc2utm = Transformer.from_crs("EPSG:3857","EPSG:32617")
utm2wmerc = Transformer.from_crs("EPSG:32617","EPSG:3857")

centre_wmerc = [-8837768.68,5410177.27]

centre_utm = wmerc2utm.transform(*centre_wmerc)
radius_utm = 250
bbox_utm = shp2array.Bbox(centre_utm, radius_utm, "EPSG:32617")

bbox_wmerc = copy.copy(bbox_utm)
bbox_wmerc.transform( utm2wmerc.transform, "EPSG:3857")

building_array = shp2array.import_shpfile_as_array("./toronto_3d_massing/3DMassingShapefile_2022_WGS84.shp", "AVG_HEIGHT", bbox_wmerc, nrows=scale*20, ncols=scale*20)
dtm_array = shp2array.import_tif_as_array("./dtm_1m_utm17_e_12_83.tif",bbox_utm, nrows=scale*20, ncols=scale*20)

map = building_array + dtm_array

point_wmerc = [-8837941.6,5410132.6]
point = shp2array.get_idx(point_wmerc, map, bbox_wmerc)

direction = [-1,1]
r = 7*scale
elevation = map[ point[0], point[1] ] + 10
m = viewshed.getViewshed(map, point, direction, r, elevation)
m = viewshed.detectBuildings(building_array, m)
viewshed.plotVisiblePoints(m, building_array)
plt.show()
