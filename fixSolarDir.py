#!/usr/bin/env python

import os
import glob,dbconn
from config import *
import shutil

#outdir = "F:\SolarResourceData\Final_SRR_Rerun"

os.chdir('D:\\MN_Solar_Suitability_Analysis\\MN_Solar\\Solar_Tiles')

out_path = "D:\MN_Solar_Suitability_Analysis\MN_Solar\Solar_Tiles"

#out_path = config.get('paths','solar_raster_output_dir')
print "Checking files in " + out_path

extensions = [
        '.img',
        '.img.aux.xml',
        '.rrd',
        '.img.xml'
        ]

for dirname in glob.glob(out_path + "\\*"):
    print "Processing " + dirname

    dirno = dirname.replace(out_path + "\\",'')
    



    updatewhere = []
    for img in glob.glob(dirname + '\\*.img'):
        imgnumber = img.replace(dirname + '\\','').replace('.img','')
        #updatewhere.append(imgnumber)
        demno = 0
        q = """
            SELECT d.id FROM dem_fishnets d,sa_fishnets s WHERE ST_WITHIN(s.the_geom,d.the_geom) AND s.id=""" + imgnumber + """
        """
        t = dbconn.run_query(q)
        for s in t:
            demno = str(s['id'])

        if not os.path.exists(out_path + "\\" + demno):
            os.mkdir(out_path + "\\" + demno)

        if dirno != demno and demno != 0:
            print "----Move----"
            for ext in extensions:
                srcfile = out_path + "\\" + dirno + "\\" + imgnumber + ext
                dstfile = out_path + "\\" + demno + "\\" + imgnumber + ext
                
                try:
                    #shutil.move(srcfile,dstfile)
                    print srcfile
                    print dstfile
                    print
                except:
                    pass

        #sys.exit(0)

            


