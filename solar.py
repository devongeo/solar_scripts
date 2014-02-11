#!/usr/bin/env python

class solar
    # module constants

    # SConst — The solar flux outside the atmosphere at the mean earth-sun 
    # distance, known as solar constant. The solar constant used in the analysis is 
    # 1367 W/m2. This is consistent with the World Radiation Center (WRC) solar constant.
    SCONST = 1367

    # Pdif — The proportion of global normal radiation flux that is diffused. 
    # Typically it is approximately 0.2 for very clear sky conditions and 0.7 
    # for very cloudy sky conditions.
    PDIF = 0.4

    sectors = []

    def __init__(self):
        self.loadSectors()

    def loadSectors(files):
        self.sectors = []


    # From: http://resources.arcgis.com/en/help/main/10.1/index.html#//009z000000tm000000
    # How solar radiation is calculated
    # Desktop » Geoprocessing » Tool reference » Spatial Analyst toolbox » Solar Radiation toolset
    # 
    # The solar radiation analysis tools calculate insolation across a landscape or 
    # for specific locations, based on methods from the hemispherical viewshed algorithm 
    # developed by Rich et al. (Rich 1990, Rich et al. 1994) and further developed by 
    # Fu and Rich (2000, 2002).
    # 
    # The total amount of radiation calculated for a particular location or area is 
    # given as global radiation. The calculation of direct, diffuse, and global insolation 
    # are repeated for each feature location or every location on the topographic surface,
    # producing insolation maps for an entire geographic area.

    # Solar radiation equations


    # Global radiation calculation
    # 
    # Global radiation (Globaltot) is calculated as the sum of direct (Dirtot) and 
    # diffuse (Diftot) radiation of all sun map and sky map sectors, respectively.
    # 
    #  Globaltot = Dirtot + Diftot

    def globaltot:
        return dirtot() + diftot()

    # Direct solar radiation
    # 
    # Total direct insolation (Dirtot) for a given location is the sum of the direct 
    # insolation (Dirθ,α) from all sun map sectors:
    # 
    #  Dirtot = Σ Dirθ,α    (1)

    def dirtot:
        tot = 0
        for sector in sectors:
            tot += dirinsolation(sector)
        return tot

    # The direct insolation from the sun map sector (Dirθ,α) with a centroid at 
    # zenith angle (θ) and azimuth angle (α) is calculated using the following equation:
    # 
    #  Dirθ,α = SConst * βm(θ) * SunDurθ,α * SunGapθ,α * cos(AngInθ,α)    (2)
    #     where:
    #         SConst — The solar flux outside the atmosphere at the mean earth-sun 
    # distance, known as solar constant. The solar constant used in the analysis is 
    # 1367 W/m2. This is consistent with the World Radiation Center (WRC) solar constant.
    #
    # β — The transmissivity of the atmosphere (averaged over all wavelengths) for the shortest path (in the direction of the zenith).
    # m(θ) — The relative optical path length, measured as a proportion relative to the zenith path length (see equation 3 below).
    # SunDurθ,α — The time duration represented by the sky sector. For most sectors, 
    #   it is equal to the day interval (for example, a month) multiplied by the hour 
    #   interval (for example, a half hour). For partial sectors (near the horizon), 
    #   the duration is calculated using spherical geometry.
    # SunGapθ,α — The gap fraction for the sun map sector.
    # AngInθ,α — The angle of incidence between the centroid of the sky sector and 
    #   the axis normal to the surface (see equation 4 below).

    def dirinsolation(sector):
        transmissivity = ???
        pathlength = relative_optical_path_length(sector)
        sundur = sun_duration(sector)
        sungap = sun_gap(sector)
        angle  = angle_of_incidence(sector)

        return SCONST * transmissivity * pathlength * sundur * sungap * math.cos(angle)


    # Relative optical length, m(θ), is determined by the solar zenith angle and 
    # elevation above sea level. For zenith angles less than 80°, it can be calculated 
    # using the following equation:
    # 
    #  m(θ) = EXP(-0.000118 * Elev - 1.638*10-9 * Elev^2) / cos(θ)    (3)
    # 
    #     where:
    #         θ — The solar zenith angle.
    #         Elev — The elevation above sea level in meters.

    def relative_optical_path_length(sector):
        elev = sector.elevation
        zenith = ???
        return (-0.000118 * elev - 1.638*10^-9 * elev^2) / math.cos(zenith)
    
    # The effect of surface orientation is taken into account by multiplying by the 
    # cosine of the angle of incidence. Angle of incidence (AngInSkyθ,α) between the 
    # intercepting surface and a given sky sector with a centroid at zenith angle and 
    # azimuth angle is calculated using the following equation:
    # 
    #  AngInθ,α = acos( Cos(θ) * Cos(Gz) + Sin(θ) * Sin(Gz) * Cos(α-Ga) )    (4)
    # 
    #     where:
    #         Gz — The surface zenith angle.
    # 
    #         Note that for zenith angles greater than 80°, refraction is important.
    #         Ga — The surface azimuth angle.

    def angle_of_incidence(sector):
        gz = sector.surface_zenith_angle
        ga = sector.surface_azimuth_angle
        angle = sector.angle
        alpha = ???
        return math.acos(math.cos(angle) * math.cos(gz) + math.sin(angle) * math.sin(gz) * math.cos(alpha - gz))

    # Diffuse radiation calculation
    # 
    # For each sky sector, the diffuse radiation at its centroid (Dif) is calculated, 
    # integrated over the time interval, and corrected by the gap fraction and angle 
    # of incidence using the following equation:
    # 
    #  Difθ,α = Rglb * Pdif * Dur * SkyGapθ,α * Weightθ,α * cos(AngInθ,α)    (5)
    # 
    #     where:
    #         Rglb — The global normal radiation (see equation 6 below).
    #         Pdif — The proportion of global normal radiation flux that is diffused. 
    #           Typically it is approximately 0.2 for very clear sky conditions and 0.7 
    #           for very cloudy sky conditions.
    #         Dur — The time interval for analysis.
    #         SkyGapθ,α — The gap fraction (proportion of visible sky) for the sky sector.
    #         Weightθ,α — The proportion of diffuse radiation originating in a given 
    #           sky sector relative to all sectors (see equations 7 and 8 below).
    #         AngInθ,α — The angle of incidence between the centroid of the sky 
    #           sector and the intercepting surface.

    def difuse_radiation(sector):
        dur = ????
        gap = skygap(sector)
        wei = weight(sector)
        angle = angle_of_incidence(sector)
        rglob = global_normal_radiation(sector) 
        return rglob * PDIF * dur * gap * wei * math.cos(angle)

    # The global normal radiation (Rglb) can be calculated by summing the direct 
    # radiation from every sector (including obstructed sectors) without correction 
    # for angle of incidence, then correcting for proportion of direct radiation, 
    # which equals 1-Pdif:
    # 
    #  Rglb = (SConst Σ(βm(θ))) / (1 - Pdif)    (6)

    def global_normal_radiation():
        dirtot = dir_radiation()
        return (SCONST * dirtot) / (1 - PDIF)

    def dir_radiation:
        tot = 0
        for sector in sectors:
            tot += dir_radiation_one(sector);
        return tot

    def dir_radiation_one:
        transmissivity = ???
        pathlength = relative_optical_path_length(sector)
        return transmissivity * pathlength 

    # For the uniform sky diffuse model, Weightθ,α is calculated as follows:
    # 
    #  Weightθ,α = (cosθ2- cosθ1) / Divazi    (7)
    # 
    #     where:
    #         θ1 and θ2 — The bounding zenith angles of the sky sector.
    #         Divazi — The number of azimuthal divisions in the sky map.

    def uniform_sky_diffuse_weight:
        angle_one = ???
        angle_two = ???
        divisions = ???
        return (math.cos(angle_two) - math.cos(angle_one)) / divisions


    # For the standard overcast sky model, Weightθ,α is calculated as follows:
    # 
    #  Weightθ,α = (2cosθ2 + cos2θ2 - 2cosθ1 - cos2θ1) / 4 * Divazi    (8)

    def standard_overcast_weight:
        angle_one = ???
        angle_two = ???
        divisions = ???
        return (2 * math.cos(angle_two) + math.cos(2 * angle_two) -  2 * math.cos(angle_one) - math.cos(2 * angle_one)

    # Total diffuse solar radiation for the location (Diftot) is calculated as the sum 
    # of the diffuse solar radiation (Dif) from all the sky map sectors:
    # 
    #  Diftot = Σ Difθ,α    (9)

    def diftot:
        tot = 0
        for sector in sectors:
            tot += difuse_radiation(sector)
        return tot

    # 
    # References
    # 
    # Fu, P. 2000. A Geometric Solar Radiation Model with Applications in Landscape 
    #   Ecology. Ph.D. Thesis, Department of Geography, University of Kansas, Lawrence, Kansas, USA.
    # Fu, P., and P. M. Rich. 2000. The Solar Analyst 1.0 Manual. Helios Environmental Modeling Institute (HEMI), USA.
    # Fu, P., and P. M. Rich. 2002. "A Geometric Solar Radiation Model with Applications 
    #   in Agriculture and Forestry." Computers and Electronics in Agriculture 37:25–35.
    # Rich, P. M., R. Dubayah, W. A. Hetrick, and S. C. Saving. 1994. "Using Viewshed 
    #   Models to Calculate Intercepted Solar Radiation: Applications in Ecology. 
    #   American Society for Photogrammetry and Remote Sensing Technical Papers, 524–529.
    # Rich, P. M., and P. Fu. 2000. "Topoclimatic Habitat Models." Proceedings of 
    #   the Fourth International Conference on Integrating GIS and Environmental Modeling. 