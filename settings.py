import math

""" ########################
##  SCIENTIFIC CONSTANTS  ##
######################## """

# determines rate of thermal radiation
stefan_boltzmann_constant = 5.6703*pow(10, -8)
gravitational_constant = 6.6741*pow(10, -11)

""" ######################################
# ARBITRARY VALUES FROM THE REAL WORLD  ##
###################################### """

""" earth's parameters """
earths_circumference = 40.075*pow(10, 6)  # (m)
earths_water_volume = 1.386*pow(10, 18)  # (m^3) http://water.usgs.gov/edu/gallery/global-water-volume.html
earths_water_mass = 1.35*pow(10, 21)  # (kg)
earths_energy_production = 47*pow(10, 12)  # (W) https://en.wikipedia.org/wiki/Earth%27s_internal_heat_budget
earths_crust_specific_heat_capacity = 800  # (J/K kg) http://www.engineeringtoolbox.com/specific-heat-capacity-d_391.html
earths_crust_thermal_conductivity = 1.5  # (W/Km) http://www.engineeringtoolbox.com/thermal-conductivity-d_429.html
earths_mass = 5.972*pow(10, 24)  # (kg) https://en.wikipedia.org/wiki/Earth_mass

""" sun's parameters """
suns_power = 3.846*pow(10, 26)  # (W) https://en.wikipedia.org/wiki/Sun#Structure
earth_sun_distance = 149.6*pow(10, 9)  # (m) http://www.space.com/17081-how-far-is-earth-from-the-sun.html

""" densities """
earths_crust_density = 3000  # (kg/m^3) https://en.wikipedia.org/wiki/Structure_of_the_Earth#Core and http://www.engineeringtoolbox.com/metal-alloys-densities-d_50.html
water_density = 1000  # (kh/m^3) https://www.google.com/search?sourceid=chrome-psyapi2&ion=1&espv=2&ie=UTF-8&q=density%20of%20water&oq=density%20of%20water&aqs=chrome..69i57j0l5.2454j0j7

""" albedos """
soil_albedo = 0.17  # https://en.wikipedia.org/wiki/Albedo

""" emmisivities """
soil_emissivity = 0.92  # http://www.thermoworks.com/emissivity_table.html

""" ########################
#####  GAME SETTINGS  ######
######################## """

time_step_size = 60*60*24  # (s)


""" ########################
#####  WORLD SETTINGS  #####
######################## """

""" world size """
world_circumference = 1.0 * earths_circumference  # (m)
world_radius = world_circumference/(2*math.pi)  # (m)
total_water_volume = 0.75*earths_water_volume  # (m^3)
world_cell_circumference = 100  # (cells)
world_water_mass = 1.0*earths_water_mass  # (kg)
cell_degree_width = 360.0/float(world_cell_circumference)  # (degrees)
cell_width = world_circumference/world_cell_circumference  # (m)
cell_area = pow(cell_width, 2)
world_mass = earths_mass


""" world shape """
# how smooth is the world
# the buffer sets a value at which different areas will tend to have similar heights
# a high value will produce things like plateaus
# for a chaotic world set the buffer to -5
# the units are distances in cells
smoothness_buffer = 10
# the rate affects the increase in independce of different areas as their distance increases
# though change might not be obvious at first if the buffer is high
# it is unitless and ranges from 0 to +inf
# for a smooth world set the rate to 0
smoothness_rate = 1
max_ground_height = 10000  # (m)
min_ground_height = -10000  # (m)
# how are random ground heights generated? beta_a and beta_b are the two parameters of a beta distribution
# a=b=1 -> uniform
# a=b > 1 -> increasingly normal
# a=b < 1 -> u-shaped
# a > b -> negative skew
# b>a -> positive skew
beta_a = 1.2
beta_b = 4

""" land properties """
land_density = earths_crust_density  # (kg/m^3)
land_depth = 5  # (m)
land_specific_heat_capacity = earths_crust_specific_heat_capacity  # (J/K kg)
land_thermal_conductivity = earths_crust_thermal_conductivity
land_albedo = soil_albedo
land_emissivity = soil_emissivity

""" world energy budgets """
initial_land_temperature = 283  # (K)
world_power = earths_energy_production  # (W)


""" sun properties """
sun_power = suns_power  # (W)
sun_distance = earth_sun_distance*1  # (m)


""" ########################
######  MAP SETTINGS  ######
######################## """

# width of map in px
map_width = 1200
# height of map in px
map_height = 600
# width of border around map in px
map_border = 0
# size of each cell
tile_height = map_height/float(world_cell_circumference/2 + 1)
tile_width = map_width/float(world_cell_circumference)
# boolean, draw water?
draw_water = True
# what mode are we drawing
draw_mode = "terrain"
draw_water = True

""" ########################
#####  MISC SETTINGS  ######
######################## """

verbose = True
debug = False
