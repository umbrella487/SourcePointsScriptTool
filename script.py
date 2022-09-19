"""
ArcGIS script tool for generating controls(horizontals only) for setting out the 
position of source points in a geophysical survey

Created by Francis Dowuona
"""

#import modules
import arcpy
import csv

#Get Parameters
table = arcpy.GetParameterAsText(0)
x_field = arcpy.GetParameterAsText(1)
y_field = arcpy.GetParameterAsText(2)
interval = arcpy.GetParameterAsText(3)
export_to_file = arcpy.GetParameterAsText(4) #if user wishes to export shot points on the GO!
coordinate_system = arcpy.GetParameterAsText(5)
shotPoints = arcpy.GetParameterAsText(6)

#Declare local variables
expression_for_pointIDS="getPointID(!FID!)"
codeblock_for_expression = "def getPointID(val):\n return str( 2000 + int(val) * 2)"


#Define Process Function
def generateShotPoints():
    try:
        """
        Process for generating source points preplots for geophysical survey
        """
        #Make Event layer of input points
        line = arcpy.MakeXYEventLayer_management(table, x_field, y_field, 'line', coordinate_system, "")

        #Create Line Feature for event layer
        arcpy.PointsToLine_management(line,arcpy.os.path.join(arcpy.env.scratchWorkspace,'_pointsLine'), '', '', 'NO_CLOSE')

        #Densify Line per shot points interval
        arcpy.Densify_edit(arcpy.os.path.join(arcpy.env.scratchWorkspace,'_pointsLine'), "DISTANCE", interval, "0.1 METERS", "")

        #Extraction points from densified line
        arcpy.FeatureVerticesToPoints_management(arcpy.os.path.join(arcpy.env.scratchWorkspace,'_pointsLine'), shotPoints, "ALL")

        #Delete line Feature as it is not needed anymore
        arcpy.Delete_management(arcpy.os.path.join(arcpy.env.scratchWorkspace,'_pointsLine'))

        #Add PointID Field to Shot Points
        arcpy.AddField_management(shotPoints, "POINTID", "TEXT", "", "", "50", "Point_id", "NULLABLE", "NON_REQUIRED", "")

        #Calculate PointID per project specfification
        arcpy.CalculateField_management(shotPoints,"POINTID", expression_for_pointIDS, "PYTHON", codeblock_for_expression)

        #Calculate coordinates for shot points
        arcpy.AddGeometryAttributes_management(shotPoints, "POINT_X_Y_Z_M", "", "", coordinate_system)

        #If user chooses to export points on the GO!
        if export_to_file:
            with open(arcpy.os.path.join(arcpy.os.path.dirname(table),'ShotsFile.csv'), 'wb') as csvFile:
                csvwriter = csv.writer(csvFile, delimiter=',')
                csvwriter.writerow(["POINTID","POINT_X","POINT_Y"])
                for i in arcpy.da.SearchCursor(shotPoints, ["POINTID","Shape@XY"]):
                    data = [i[0],i[1][0],i[1][1]]
                    csvwriter.writerow(data)
    except arcpy.ExecuteError as err:
        arcpy.AddError(err)

#Call Function
generateShotPoints()