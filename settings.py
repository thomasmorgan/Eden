import math

""" ########################
##  SCIENTIFIC CONSTANTS  ##
######################## """

# determines rate of thermal radiation
stefan_boltzmann_constant = 5.6703*pow(10, -8)

""" ######################################
# ARBITRARY VALUES FROM THE REAL WORLD  ##
###################################### """

""" earth's parameters """
earths_circumference = 40.075*pow(10, 6)  # (m)
earths_water_volume = 1.386*pow(10, 18)  # (m^3) http://water.usgs.gov/edu/gallery/global-water-volume.html
earths_energy_production = 47*pow(10, 12)  # (W) https://en.wikipedia.org/wiki/Earth%27s_internal_heat_budget
earths_crust_density = 3000  # (kg/m^3) https://en.wikipedia.org/wiki/Structure_of_the_Earth#Core
earths_crust_specific_heat_capacity = 800  # (J/K kg) http://www.engineeringtoolbox.com/specific-heat-capacity-d_391.html

""" sun's parameters """
suns_power = 3.846*pow(10, 26)  # (W) https://en.wikipedia.org/wiki/Sun#Structure
earth_sun_distance = 149.6*pow(10, 9)  # (m) http://www.space.com/17081-how-far-is-earth-from-the-sun.html


""" ########################
#####  WORLD SETTINGS  #####
######################## """

""" world size """
world_circumference = 1.0 * earths_circumference  # (m)
world_radius = world_circumference/(1*math.pi)  # (m)
total_water_volume = 0*earths_water_volume  # (m^3)
# how wide is the world (in cells)
# this absolutely needs to be a power of 2!
world_cell_width = pow(2, 6)
# how tall is the world (in cells)
# this absolutely needs to be a power of 2!
world_cell_height = pow(2, 6)
# how big is each cell?
cell_size = world_circumference/world_cell_width  # (m)


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
# tallest possible ground height (km)
# must be > 0
max_ground_height = 10000
# lowest possible ground height (km)
# must be < 0
min_ground_height = -10000
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
# how thick is the land
land_depth = 0.005
# how much energy is needed to heat it (kJ per kg per K)
land_specific_heat_capacity = earths_crust_specific_heat_capacity  # (J/K kg)
# thermal conductivity of land (Watts per m per K)
land_thermal_conductivity = 1.5

""" world energy budgets """
initial_land_temperature = 283  # (K)
# rate of core energy production (kJ per cell per day)
thermal_energy_from_core_per_day_per_cell = earths_energy_production*(60*60*24)/(world_cell_height*world_cell_width)


""" sun properties """
# power of the sun
sun_power = suns_power
# how far away is the sun (in km, 150000000 is true value)
sun_distance = earth_sun_distance*1


""" ########################
######  MAP SETTINGS  ######
######################## """

# width of map in px
map_width = 750
# height of map in px
map_height = 750
# width of border around map in px
map_border = 0
# size of each cell
cell_height = map_height/float(world_cell_height)
cell_width = map_width/float(world_cell_width)
# boolean, draw water?
draw_water = True
# what mode are we drawing
draw_mode = "terrain"
