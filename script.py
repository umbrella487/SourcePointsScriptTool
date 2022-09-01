#ArcGIS script tool for generating controls(horizontals only) for setting out the position of source points in a geophysical survey

#Created by Francis Dowuona

#import modules
import arcpy
import csv
import ctypes

#Get Parameters
xy_table = arcpy.GetParameterAsText(0)
x_field = arcpy.GetParameterAsText(1)
y_field = arcpy.GetParameterAsText(2)
shotpoints_interval = arcpy.GetParameterAsText(3)
export_to_file = arcpy.GetParameterAsText(4) #if user wishes to export shot points on the GO!
coordinate_system = arcpy.GetParameterAsText(5)
shot_points = arcpy.GetParameterAsText(6)

#Declare local variables
path = (arcpy.Describe(xy_table)).path + "\\"
eventLayer = "eventlyr"
line = path + "line.shp"
msgBox = ctypes.windll.user32.MessageBoxW
expression_for_pointIDS="getPointID(!FID!)"
codeblock_for_expression = """def getPointID(val):
 return str( 2000 + int(val) * 2)"""
shotpointscsv = path + "shotpoints.csv"

#Define Process Function
def generateShotPoints():
    try:
        #Make Event layer of input points
        arcpy.MakeXYEventLayer_management(xy_table, x_field, y_field, eventLayer, coordinate_system, "")

        #Create Line Feature for event layer
        arcpy.PointsToLine_management(eventLayer, line, "", "", "NO_CLOSE")

        #Densify Line per shot points interval
        arcpy.Densify_edit(line, "DISTANCE", shotpoints_interval, "0.1 METERS", "")

        #Extraction points from densified line
        arcpy.FeatureVerticesToPoints_management(line, shot_points, "ALL")

        #Delete line Feature as it is not needed anymore
        arcpy.Delete_management(line)

        #Add PointID Field to Shot Points
        arcpy.AddField_management(shot_points, "POINTID", "TEXT", "", "", "50", "Point_id", "NULLABLE", "NON_REQUIRED", "")

        #Calculate PointID per project specfification
        arcpy.CalculateField_management(shot_points, "POINTID", expression_for_pointIDS, "PYTHON", codeblock_for_expression)

        #Calculate coordinates for shot points
        arcpy.AddGeometryAttributes_management(shot_points, "POINT_X_Y_Z_M", "", "", coordinate_system)

        #If user chooses to export points on the GO!
        if export_to_file:
            with open(shotpointscsv, 'wb') as csvFile:
                csvwriter = csv.writer(csvFile, delimiter=',')
                csvwriter.writerow(["POINTID","POINT_X","POINT_Y"])
                for i in arcpy.da.SearchCursor(shot_points, ["POINTID","POINT_X","POINT_Y"]):
                    data = [i[0],i[1],i[2]]
                    csvwriter.writerow(data)
    except arcpy.ExecuteError:
        for i in range(0, arcpy.GetMessageCount()):
            msgBox(None, u'{0}'.format(arcpy.GetSeverity(i)),u'{0}'.format(arcpy.GetMessage(i)),0)

#Call Function
generateShotPoints()
