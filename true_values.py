"""True values from the real world - do not edit."""

""" ########################
##  SCIENTIFIC CONSTANTS  ##
######################## """

# determines rate of thermal radiation
stefan_boltzmann_constant = 5.6703*pow(10, -8)
gravitational_constant = 6.6741*pow(10, -11)

""" ######################################
# ARBITRARY VALUES FROM THE REAL WORLD  ##
###################################### """

""" the earth """
earths_circumference = 40.075*pow(10, 6)  # (m)
earths_energy_production = 47*pow(10, 12)
# (W) https://en.wikipedia.org/wiki/Earth%27s_internal_heat_budget
earths_mass = 5.972*pow(10, 24)
# (kg) https://en.wikipedia.org/wiki/Earth_mass

""" the oceans """
earths_water_mass = 1.35*pow(10, 21)  # (kg)

""" sun's parameters """
suns_power = 3.846*pow(10, 26)
# (W) https://en.wikipedia.org/wiki/Sun#Structure
earth_sun_distance = 149.6*pow(10, 9)
# (m) http://www.space.com/17081-how-far-is-earth-from-the-sun.html

""" heat capacities """
earths_crust_specific_heat_capacity = 800
# (J/K kg) http://www.engineeringtoolbox.com/specific-heat-capacity-d_391.html
water_specific_heat_capacity = 4186
# http://hyperphysics.phy-astr.gsu.edu/hbase/thermo/spht.html

""" thermal conductivities """
# (W/Km) http://www.engineeringtoolbox.com/thermal-conductivity-d_429.html
earths_crust_thermal_conductivity = 1.5
water_thermal_conductivity = 0.58


""" densities """
earths_crust_density = 3000
# (kg/m^3) https://en.wikipedia.org/wiki/Structure_of_the_Earth#Core
# http://www.engineeringtoolbox.com/metal-alloys-densities-d_50.html
water_density = 1000
# (kh/m^3) http://www.engineeringtoolbox.com/liquids-densities-d_743.html

""" albedos """
soil_albedo = 0.17  # https://en.wikipedia.org/wiki/Albedo
max_water_albedo = 0.95
min_water_albedo = 0.05

""" absorbicities """
# http://oceanworld.tamu.edu/resources/ocng_textbook/chapter06/chapter06_10.htm
# https://en.wikipedia.org/wiki/Beer%E2%80%93Lambert_law
# https://en.wikipedia.org/wiki/Electromagnetic_absorption_by_water
water_attenuation_coefficient_sunlight = 0.05
water_attenuation_coefficient_infrared = 10000


def water_albedo(facing):
    """Value of water albedo depending on facing value."""
    return min_water_albedo + \
        (1 - facing)*(max_water_albedo - min_water_albedo)


""" emmisivities """
soil_emissivity = 0.92  # http://www.thermoworks.com/emissivity_table.html
water_emissivity = 0.95
