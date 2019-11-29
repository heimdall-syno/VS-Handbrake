import os, struct
from ConfigParser import ConfigParser
from collections import namedtuple

cfg = namedtuple('cfg', 'handbrake handbrake_movies handbrake_series')

cfg.__new__.__defaults__ = (None,) * len(cfg._fields)

def parse_cfg(config_file):
    ''' Parse all configuration options of the config file. '''

    ## Read the config file
    config = ConfigParser()
    config.read(config_file)
    secs = ['Handbrake']
    _ = [exit('Error: Section missing') for s in secs if not config.has_section(s)]

    ## Get all handbrake related configs
    handbrake = config.get(secs[3], 'handbrake')
    handbrake_movies = config.get(secs[3], 'handbrake_movies')
    handbrake_series = config.get(secs[3], 'handbrake_series')
    handbrake_movies = handbrake_movies.replace(" ", "").split(",")
    handbrake_series = handbrake_series.replace(" ", "").split(",")


    return cfg(handbrake, handbrake_movies, handbrake_series)