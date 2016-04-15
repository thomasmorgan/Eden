""" ########################
#####  WORLD SETTINGS  #####
######################## """

""" world size """
# how wide is the world
# this absolutely needs to be a power of 2!
world_tile_width = pow(2, 8)
# how tall is the world
# this absolutely needs to be a power of 2!
world_tile_height = pow(2, 8)
# total water volume
total_water_volume = 4*world_tile_width*world_tile_height

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
smoothness_rate = 0.4
# tallest possible ground height
# must be > 0
max_ground_height = 50
# lowest possible ground height
# must be < 0
min_ground_height = -50
# how are random ground heights generated? beta_a and beta_b are the two parameters of a beta distribution
# a=b=1 -> uniform
# a=b > 1 -> increasingly normal
# a=b < 1 -> u-shaped
# a > b -> negative skew
# b>a -> positive skew
beta_a = 1.2
beta_b = 2

""" sun properties """
# how hot is the sun
sun_strength = 1.0


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
