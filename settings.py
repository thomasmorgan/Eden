"""Configurable game settings."""

import true_values as tv
import math

""" ########################
#####  GAME SETTINGS  ######
######################## """

time_step_size = 1  # (s)
time_step_description = "1s"


""" ########################
#####  WORLD SETTINGS  #####
######################## """

""" world size """
world_circumference = 1.0 * tv.earths_circumference  # (m)
world_radius = world_circumference/(2*math.pi)  # (m)
world_mass = tv.earths_mass

""" oceans """
world_water_mass = tv.earths_water_mass*1.0
water_init_mode = "even"

""" cells """
world_cell_circumference = 80  # (cells)
cell_degree_width = 360.0/float(world_cell_circumference)  # (degrees)
cell_width = world_circumference/world_cell_circumference  # (m)
cell_area = pow(cell_width, 2)  # m**2
degrees_per_cell = 360.0/float(world_cell_circumference)  # (degrees)
influence_lambda = 1.0 / cell_width

""" transport rates """
water_transport_rate = 1000  # (kg/s m^2)

""" world shape """
min_ground_height = -10000
max_ground_height = 10000


""" land properties """
land_depth = 5  # (m)

land_thermal_conductivity = tv.earths_crust_thermal_conductivity

""" world energy budgets """
initial_land_temperature = 283  # (K)
initial_water_temperature = 283
world_power = tv.earths_energy_production  # (W)

""" densities """
land_density = tv.earths_crust_density
water_density = tv.water_density

""" sun properties """
sun_power = tv.suns_power  # (W)
sun_distance = tv.earth_sun_distance*1  # (m)

""" albedos """


def water_albedo(facing):
    """Calcuate albedo of water given angle of incidence."""
    return 1.0*tv.water_albedo(facing)
land_albedo = tv.soil_albedo

"""heat capacities"""
water_specific_heat_capacity = 1.0*tv.water_specific_heat_capacity
land_specific_heat_capacity = tv.earths_crust_specific_heat_capacity
# (J/K kg)

""" attenuation coefficients """
water_attenuation_coefficient_sunlight =\
    tv.water_attenuation_coefficient_sunlight
water_attenuation_coefficient_infrared =\
    tv.water_attenuation_coefficient_infrared

""" emmisivities """
land_emissivity = tv.soil_emissivity
water_emissivity = tv.water_emissivity

""" thermal conductivities """
land_thermal_conductivity = tv.earths_crust_thermal_conductivity
water_thermal_conductivity = tv.water_thermal_conductivity

""" ############################
######  TERRAIN SETTINGS  ######
############################ """

# number of distortions when terrain initialized
n_distortions = 1000
# maximum altitude change due to distortion
max_distortion = 5000  # m

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
