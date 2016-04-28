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

""" thermal conductivities """
earths_crust_thermal_conductivity = 1.5
# (W/Km) http://www.engineeringtoolbox.com/thermal-conductivity-d_429.html

""" densities """
earths_crust_density = 3000
# (kg/m^3) https://en.wikipedia.org/wiki/Structure_of_the_Earth#Core
# http://www.engineeringtoolbox.com/metal-alloys-densities-d_50.html
water_density = 1000
# (kh/m^3) http://www.engineeringtoolbox.com/liquids-densities-d_743.html

""" albedos """
soil_albedo = 0.17  # https://en.wikipedia.org/wiki/Albedo

""" emmisivities """
soil_emissivity = 0.92  # http://www.thermoworks.com/emissivity_table.html
