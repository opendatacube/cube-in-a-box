import sys, getopt
import ogr

#/home/ubuntu/index-config

def convertLatLongToPathRows(extent,ascending,path):

    driver = ogr.GetDriverByName('ESRI Shapefile')
    dataSource = driver.Open(path, 0) # 0 means read-only. 1 means writeable.
    layer = dataSource.GetLayer()

    ring = ogr.Geometry(ogr.wkbLinearRing)
    ring.AddPoint(extent[0], extent[1])
    ring.AddPoint(extent[0], extent[3])
    ring.AddPoint(extent[2], extent[3])
    ring.AddPoint(extent[2], extent[1])
    ring.AddPoint(extent[0], extent[1])
    poly = ogr.Geometry(ogr.wkbPolygon)
    poly.AddGeometry(ring)

    layer.SetSpatialFilter(poly)
    print (layer.GetFeatureCount())
    if ascending == False:
        layer.SetAttributeFilter("MODE = 'A'")
    else:
        layer.SetAttributeFilter("MODE = 'D'")

    pathRows = []
    for pInfo in layer:
        pathRows.append([pInfo.GetField('PATH'),pInfo.GetField('ROW')])

    return pathRows

def main(argv):
   inputfile = 'default1'
   shapeFile = 'default2'
   try:
      opts, args = getopt.getopt(argv,"hi:o",["ifile=","ofile="])
   except getopt.GetoptError:
      print 'test.py -i <inputfile> -o <outputfile>'
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print 'test.py -i <inputfile> -o <outputfile>'
         sys.exit()
      elif opt in ("-i", "--ifile"):
         inputfile = arg
      elif opt in ("-o", "--ofile"):
         shapeFile = arg


   fileMe = open(inputfile, "r")
   stringMe = fileMe.readlines()[0]
   x1,x2,y1,y2 = eval(stringMe)
   xmin = min([x1,x2])
   xmax = max([x1,x2])
   ymin = min([y1,y2])
   ymax = max([y1,y2])
   print shapeFile
   print 'hello'
   pathRows = convertLatLongToPathRows([xmin,ymin,xmax,ymax], True, shapeFile)
   print pathRows

if __name__ == "__main__":
    main(sys.argv[1:])
