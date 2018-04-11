"""Various utility methods."""

import settings
import numpy as np


def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    r = settings.world_radius
    return c * r


def log(str, force=False):
    """Print to the logs."""
    if force or settings.verbose:
        print str


def debug(str):
    """Print a debugging message."""
    if settings.debug:
        print "DEBUG: " + str


def log_welcome():
    """Print the welcome splash."""
    print "\n\
                                                                            \n\
                          _ _                    _ _                        \n\
                         ( ` )                  (_I_)                       \n\
                        (_{;}_)                (_(=)_)                      \n\
                         (_,_)                  (_I_)                       \n\
                .-''-.   ______         .-''-.  ,---.   .--._ _           \n\
   _          .'_ _   \ |    _ `''.   .'_ _   \ |    \  |  |_I_)   _      \n\
 _( )_       / ( ` )   '| _ | ) _  \ / ( ` )   '|  ,  \ |  |(=)_)_( )_    \n\
(_ o _)     . (_ o _)  ||( ''_'  ) |. (_ o _)  ||  |\_ \|  |_I_)(_ o _)   \n\
 (_,_)    /)|  (_,_)___|| . (_) `. ||  (_,_)___||  _( )_\  |)/   (_,_)    /)\n\
(/``|\._.'/ '  \   .---.|(_    ._) ''  \   .---.| (_ o _)  |     (/``|\._.'/\n\
     `._.'   \  `-'    /|  (_.\.' /  \  `-'    /|  (_,_)\  |          `._.'\n\
              \       / |       .'    \       / |  |    |  |                \n\
               `'-..-'  '-----'`       `'-..-'  '--'    '--'                \n\
                  _ _                                  _ _                  \n\
                 ( ' )  _ _                           ( ' )                 \n\
                (_{;}_)( ' )                         (_{;}_)                \n\
                 (_,_)(_{;}_)                         (_,_)                 \n\
                       (_,_)                                                \n\
                                                                            \n\
                                                                            "
    print "Loading . . ."
