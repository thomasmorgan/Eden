import math
""" ########################
#####  WORLD SETTINGS  #####
######################## """

""" world size """
# a tile size of 300 and tile_width/height of 2^7 approximates earth
# how big is each tile? (in km)
tile_size = 300
# how wide is the world (in tiles)
# this absolutely needs to be a power of 2!
world_tile_width = pow(2, 7)
# how tall is the world (in tiles)
# this absolutely needs to be a power of 2!
world_tile_height = pow(2, 7)
# total water volume (km^3)
total_water_volume = 1386000000
#8*world_tile_width*world_tile_height*tile_size*tile_size

""" world shape """
# how smooth is the world
# the buffer sets a value at which different areas will tend to have similar heights
# a high value will produce things like plateaus
# for a chaotic world set the buffer to -10
# the units are distances in tiles
smoothness_buffer = 10
# the rate affects the increase in independce of different areas as you cross the buffer.
# high values will produce steep cliffs
# it is unitless and ranges from 0 to +inf
# for a smooth world set the rate to 0
smoothness_rate = 1
# tallest possible ground height (km)
# must be > 0
max_ground_height = 10
# lowest possible ground height (km)
# must be < 0
min_ground_height = -10
# how are random ground heights generated? beta_a and beta_b are the two parameters of a beta distribution
# a=b=1 -> uniform
# a=b > 1 -> increasingly normal
# a=b < 1 -> u-shaped
# a > b -> negative skew
# b>a -> positive skew
beta_a = 1.2
beta_b = 4

""" other world settings """
# initial temp (K) (273 = 0C)
initial_temp = 283

""" atmosphere settings """
# what proportion of the suns energy bounces off the atmosphere?
atmosphere_albedo = 0.3
# how thick is the atmosphere (km)
atmophere_thickness = 20
# density of air (kg per km^3)
density_of_atmosphere = 1.225*pow(10, 9)
# atmosphere mass per tile (kg)
atmosphere_mass_per_tile = pow(tile_size, 2)*atmophere_thickness*density_of_atmosphere


""" sun properties """
# how much energy does the sun produce per day (kJ/day)
sun_total_daily_energy = 3.3*pow(10, 28)
# how far away is the sun (in km, 150000000 is true value)
sun_distance = 150000000*1
# how much energy could a tile possible receive (kJ/day)
# do not change, this is entirely determined by the above
max_solar_energy_per_tile = pow(tile_size, 2)/(4*math.pi*pow(sun_distance, 2))*sun_total_daily_energy


""" ########################
######  MAP SETTINGS  ######
######################## """

# width of map in px
map_width = 750
# height of map in px
map_height = 750
# width of border around map in px
map_border = 0
# size of each tile
tile_height = map_height/float(world_tile_height)
tile_width = map_width/float(world_tile_width)
# boolean, draw water?
draw_water = True
# what mode are we drawing
draw_mode = "terrain"
# draw a border around coastlines?
draw_coast = True
# width of border around coastlines
coast_width = 2.0
# color of border around coastlines
coast_color = "black"


""" ########################
######  OLD SETTINGS  ######
######################## """


degrees_per_altitude = 1
# draw_gradient = False
# draw_temperature = False

# how many tiles are there in the World
# this is old!
num_tiles = pow(2, 7)
