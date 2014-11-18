#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Test if the database connection is working

import sys
from config import *
from distutils.spawn import find_executable
import dbconn

#q = "UPDATE dem_fishnets SET state=0 WHERE state<>0 AND id IN (" + rr + ")"

#q = "UPDATE dem_fishnets SET state=0 WHERE state=1 AND id <> 1164 AND id <> 1095 AND id <> 1094 AND id <> 1232"
q = """
    SELECT d.id FROM dem_fishnets d,sa_fishnets s WHERE ST_WITHIN(s.the_geom,d.the_geom) AND s.id=5578
"""
#q = "UPDATE sa_fishnets SET state=0 FROM county c,sa_fishnets s WHERE c.countyname = 'Stearns' AND ST_INTERSECTS(c.the_geom,s.the_geom)"

#q = "UPDATE sa_fishnets SET state=0 FROM county c,sa_fishnets s WHERE c.countyname = 'Stearns' AND ST_INTERSECTS(c.the_geom,s.the_geom)"
#q = "CREATE INDEX the_geom_ix ON sa_fishnets USING GIST (the_geom)"
t = dbconn.run_query(q)


for s in t:
    print str(s['id'])
