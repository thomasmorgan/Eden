"""Various utility methods."""

import settings


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
