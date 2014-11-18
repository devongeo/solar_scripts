#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Continue fetching fishnet tiles that haven't been processed yet
# Fetch the list of lidar files for those tiles and process them

# DEM states
# -3 -- errors encountered
# -2 -- areas calculated to have no tiles within 100m
# -1 -- square has no intersecting lidar bboxes within 100m
# 0 -- available to process
# 1 -- reserved, but not complete
# 2 -- completed

import dbconn,sys,os,subprocess,re,tempfile,time
from config import *
#from arcpy import *

buffersize  = config.get('buffers','dem_selection_buffer')
basedir = config.get('paths','las_dir')
outputdir = config.get('paths','dem_output_dir')

# Radiate outwards from Blegen Hall
reserveQuery = """
    UPDATE """ + config.get('postgres','schema') + "."  + config.get('postgres','dem_fishnet_table') + """ dem 
    SET state=1 
    WHERE dem.id in (
        SELECT id FROM """ + config.get('postgres','schema') + "."  + config.get('postgres','dem_fishnet_table') + """ WHERE state=0 
        ORDER BY ST_Distance(the_geom,ST_SetSrid(ST_MakePoint(""" + config.get('processing','starting_x') + """,""" + config.get('processing','starting_y') + """),""" + config.get('projection','srid') + """))
        LIMIT 1
    ) 
    RETURNING 
    id, 
    ST_XMin(the_geom) as xmin, 
    ST_YMin(the_geom) as ymin, 
    ST_XMax(the_geom) as xmax, 
    ST_YMax(the_geom) as ymax
"""

lidarlist = """
    SELECT bbox.* FROM 
    """ + config.get('postgres','schema') + "." + config.get('postgres','dem_fishnet_table') + """ dem,
    lidar_bbox bbox
    WHERE dem.id=DEMID
    AND 
    ST_Intersects(ST_Buffer(dem.the_geom,""" + str(buffersize) + """),bbox.the_geom)
"""

completeQuery = """
    UPDATE """ + config.get('postgres','schema') + "." + config.get('postgres','dem_fishnet_table') + """ dem
    SET state=NEWSTATE
    WHERE
    dem.id=DEMID
"""

# demid is the database ID of the dem fishnet square we're working on
# lidarlist is a text file with a list of lidar files to use. This is needed because the command line gets too long for Powershell or blast2dem (not sure which)
# line is (xmin,ymin,xmax,ymax) for the output area
# buffersize is the buffer to apply for consideration
# outputdir is the directory where the files should be saved
def blast2dem(demid,lidarlist,line,buffersize,outputdir):

    print demid
    print lidarlist
    print line
    print buffersize
    print outputdir
    
    outputfile = outputdir + '\\' + '_'.join(line) + '.img'
    cmd = ['blast2dem']
   
    # Input tiles
    cmd.append('-lof ' + lidarlist)
    
    # Processing parameters
    cmd.append('-merged')
    cmd.append('-step 1')
    
    # Spatial Filtering 
    # This defines the buffered area used for calcultions
    cmd.append('-inside ' + str(int(line[0]) - int(buffersize)) + ' ' + str(int(line[1]) - int(buffersize)) + ' ' + str(int(line[2]) + int(buffersize)) + ' ' + str(int(line[3]) + int(buffersize)))
    
    # This defines the output lower-left corner
    cmd.append('-ll ' + str(line[0]) + ' ' + str(line[1]))
    
    # This defines the output tile's height and width
    cmd.append('-ncols ' + str(int(line[2]) - int(line[0])))
    cmd.append('-nrows ' + str(int(line[3]) - int(line[1])))

    # Data Filtering 
    cmd.append(config.get('blast2dem','additional_parameters'))

    # Output parameters
    cmd.append('-v')
    cmd.append('-oimg')
    filename = str(demid) + '.img'
    cmd.append('-o ' + filename)
    cmd.append('-odir ' + outputdir)

    command = ' '.join(cmd)
    
    print command

    # Check output
    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        output,error = process.communicate()
        returncode = process.poll()

        #build pyramids for new DSM tile
        #arcpy.BuildPyramids_management(outputdir + "\\" + filename,pyramid_level="-1",SKIP_FIRST="NONE",resample_technique="NEAREST",compression_type="DEFAULT",compression_quality="75",skip_existing="OVERWRITE")
        
    except:
        e = sys.exc_info()[0]
        sys.stdout.write("\t\t\t" + str(e))
        print "\n\t\t" + command 
        if os.path.isfile(outputdir + "\\" + filename):
            os.unlink(outputdir + "\\" + filename)
        return False

    # Print errors
    if error != None:
        sys.stdout.write("\t\t\t" + error)
        print "\n\t\t" + command 
        if os.path.isfile(outputdir + "\\" + filename):
            os.unlink(outputdir + "\\" + filename)
        return False
    if returncode != 0:
        sys.stdout.write("\t\t\t" + output)
        print "\n\t\t" + command 
        if os.path.isfile(outputdir + "\\" + filename):
            os.unlink(outputdir + "\\" + filename)
        return False

    if not os.path.isfile(outputdir + "\\" + filename):
        sys.stdout.write("\t\t\t" + output)
        sys.stdout.write("\t\t\tExpected to find output file " + filename + ", but didn't")
        print "\n\t\t" + command 
        return False

    # Remove empty files. Will happen where fishnet is off the map
    # 750703 -- 748kb files when they're solid black (also no results)
    if re.match('.*bounding box. skipping.*',output,re.DOTALL) or int(os.stat(outputdir + "\\" + filename).st_size) == 750703:
        sys.stdout.write("\t\t\tNo data found, not saving tile.")
        os.unlink(outputdir + "\\" + filename)
        return True

    return True

res = dbconn.run_query(reserveQuery).fetchall()
count = 0
average = 0;
while len(res) > 0:
    for row in res:
        count += 1

        sys.stdout.write("\nRunning blast2dem for row " + str(row['id']) + "\t\t\t")
        starttime = time.time()

        # The long lists of files was making the command too long for PowerShell to handle 
        # so instead we write the list of file names to a temp file and delete the file
        # when we're done
        tmp = tempfile.NamedTemporaryFile(delete=False,dir=config.get('paths','temp_dir'))
        lidares = dbconn.run_query(lidarlist.replace("DEMID",str(row['id']))).fetchall()
        for lidar in lidares:
            tmp.write(basedir + '\\' + lidar['lasfile'] + "\n")
        tmp.close()

        try:
            blasted = blast2dem(demid=row['id'],lidarlist=tmp.name,line=[str(int(row['xmin'])),str(int(row['ymin'])),str(int(row['xmax'])),str(int(row['ymax']))],buffersize=buffersize,outputdir=outputdir)
        except:   
            e = sys.exc_info()[0]
            print "\t\t\t" + str(e)
            blasted = False

        stoptime = time.time()
        average = (average * (count - 1) + stoptime - starttime) / count


        if blasted:
            print "DONE! (" + str((stoptime - starttime)) + " seconds, running avg:" + str(average) + ")"
            os.unlink(tmp.name)
            markDone = completeQuery.replace("DEMID",str(row['id'])).replace('NEWSTATE','2')
            print markDone
            dbconn.run_query(markDone)
        else:
            print "Error! (" + str((stoptime - starttime)) + " seconds, running avg:" + str(average) + ")"
            dbconn.run_query(completeQuery.replace("DEMID",str(row['id'])).replace('NEWSTATE','-3'))

        print "--END--\n"

    res = dbconn.run_query(reserveQuery).fetchall()
