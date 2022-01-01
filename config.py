import configparser
import parse
from math import gcd

config = configparser.ConfigParser()
config.read('config.ini')


# Returns star label as a tuple of integers
def star_label():
    config_star_label = config['DEFAULT']['StarLabel']
    parsed_star_label = parse.parse('{{{points}/{distance_between_points}}}', config_star_label)
    points, distance_between_points = int(parsed_star_label.named['points']), int(parsed_star_label.named['distance_between_points'])
    g = gcd(points, distance_between_points)
    return points//g, distance_between_points//g


# Duration drawing the star
def star_path_duration():
    return float(config['DEFAULT']['StarPathDuration'])


# Duration generating one green polygon
def green_polygon_duration():
    return float(config['DEFAULT']['GreenPolygonDuration'])


# Duration generating one blue polygon
def blue_polygon_duration():
    return float(config['DEFAULT']['BluePolygonDuration'])


# Animation duration
def animation_duration():
    return float(config['DEFAULT']['AnimationDuration'])


# Animation repeats
def animation_repeats():
    return int(config['DEFAULT']['AnimationRepeats'])