"""
ArcGIS script tool for generating controls(horizontals only) for setting out the 
position of source points in a geophysical survey

Created by Francis Dowuona
"""

#import modules
import arcpy
import os


#Declare local variables

def work_space(path):
    return os.path.dirname(path)

def FeatType(path):
    return '.shp' if path.endswith('.shp') else ''

def b_name(path):
    bname = os.path.basename(path).split('.')[0]
    for x in bname:
        if x == '-':
            bname = bname.replace('-','_')
    return bname

#Define Process Function
def generateShotPoints(table, x_field, y_field, coord_sys, interval, outputFeature, export_to_file='false', exportFile=''):
    try:
        """
        Process for generating source points preplots for geophysical survey
        """
        #Make Event layer of input points
        line = arcpy.MakeXYEventLayer_management(table, x_field, y_field, 'line', coord_sys, "")

        #Create Line Feature for event layer
        arcpy.PointsToLine_management(line,
                                        os.path.join(work_space(outputFeature),'{}_Line{}'.format(b_name(table),FeatType(outputFeature))), 
                                        '', '', 'NO_CLOSE')

        #Densify Line per shot points interval
        arcpy.Densify_edit(os.path.join(work_space(outputFeature),'{}_Line{}'.format(b_name(table),FeatType(outputFeature))), 
                            "DISTANCE", interval, 
                            "0.1 METERS", "")

        #Extraction points from densified line
        arcpy.FeatureVerticesToPoints_management(os.path.join(work_space(outputFeature),'{}_Line{}'.format(b_name(table),FeatType(outputFeature))),
                                                     outputFeature, "ALL")

        #Delete line Feature as it is not needed anymore
        arcpy.Delete_management(os.path.join(work_space(outputFeature),'{}_Line{}'.format(b_name(table),FeatType(outputFeature))))

        #Calculate coordinates for shot points
        arcpy.AddGeometryAttributes_management(outputFeature, "POINT_X_Y_Z_M", "", "", coord_sys)

        #If user chooses to export points on the GO!
        if export_to_file == 'true':
            arcpy.TableToExcel_conversion(outputFeature, exportFile)
            pass
    except arcpy.ExecuteError as err:
        arcpy.AddError(err)

#Call Function
if __name__=='__main__':
    args = tuple(arcpy.GetParameterAsText(i)for i in range(arcpy.GetArgumentCount()))
    generateShotPoints(*args)