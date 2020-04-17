import sys, os, re, argparse, subprocess
from shutil import move
from collections import Counter
from argparse import Namespace

## Add modules from the submodule (vs-utils)
cur_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(cur_dir, "VS-Utils"))
from parse import parse_cfg
from prints import errmsg, debugmsg

season_desc = "Staffel"

config_file = os.path.dirname(os.path.abspath(__file__)) + '/config.txt'
cfg = parse_cfg(config_file, "vs-handbrake", "host")

def get_resolution(file_name):

    ## Call mediainfo via command line
    cmds = ['mediainfo', file_name]
    p = subprocess.Popen(cmds, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdout, stderr) = p.communicate()
    if (len(stderr) > 1): errmsg(stderr)

    ## Parse the mediainfo output as dictionary
    mediainfo_output = stdout.decode("UTF-8").split("\n")
    mediainfo_output = [' '.join(m.split()).split(" : ") for m in mediainfo_output]
    mediainfo_output = dict([tuple(m) for m in mediainfo_output if len(m) > 1])

    ## Parse the height of the video resolution
    res = mediainfo_output["Height"]
    res = int(res.replace(" ", "").replace("pixels", ""))

    ## Round the real resolution of the video file to the common resolution
    if (res == 0): return -1
    if (0 < res and res <= 360): return "360p"
    elif (360 < res and res <= 480): return "480p"
    elif (480 < res and res <= 720): return "720p"
    elif (720 < res and res <= 1080): return "1080p"
    elif (1080 < res and res <= 2160): return "2160p"
    else: return -1

def delimiter_get(filename):
    ## Get the delimiter of the video filename
    delimiters = [".", "-", "_"]
    delimiter_count = Counter(filename).most_common()
    delimiter_count = [(key, val) for key, val in delimiter_count if key in delimiters]
    delimiter = sorted(delimiter_count, key=lambda x: x[1])[-1][0]
    debugmsg("Delimiter counts and the selected one", "Naming", (delimiter_count, delimiter))
    return delimiter

###############################################################################
###                               Series                                    ###
###############################################################################

def analyze_series(series):

    ## Get the extensions of the season
    series.file_base, series.extension = os.path.splitext(series.file)

    ## Analyze resolution of the season
    series.resolution = get_resolution(series.file)
    if(series.resolution == -1):
        errmsg("The resolution of the series episode was invalid", "Naming")
        exit()

    ## Analyze the current season number
    splitted = series.file_base.split(series.delim)
    try:
        debugmsg("Check for regular naming scheme (s01e01)", "Naming")
        season_ep = [f for f in splitted if "s0" in f.lower() or "s1" in f.lower()][0]
        series.season = "{}".format(re.split('s|e', season_ep.lower())[1])
        series.episode = "S%sE%s" % (series.season, re.split('s|e', season_ep.lower())[2])
        series.season = "%s %s" % (season_desc, series.season)
    except IndexError:
        debugmsg("Regular naming scheme not found, check for alternative naming scheme (101|1201)", "Naming")
        season_ep = splitted[-1]
        if (season_ep.isdigit()):
            if (int(season_ep) > 100 and int(season_ep) < 1000):
                series.season = "{:02d}".format(int(season_ep[0]))
                series.episode = "S{}E{}".format(series.season, season_ep[1:])
                series.season = "{} {}".format(season_desc, series.season)
                debugmsg("Alternative naming scheme found", "Naming")
            elif(int(season_ep) > 1000 and int(season_ep) < 2000):
                series.season = "{:02d}".format(int(season_ep[:2]))
                series.episode = "S{}E{}".format(series.season, season_ep[3:])
                series.season = "{} {}".format(season_desc, series.season)
                debugmsg("Alternative naming scheme found", "Naming")
            else:
                errmsg("Undefined naming scheme for episode", "Naming", (series.file,))
                exit()
        else:
            errmsg("Undefined naming scheme for episode", "Naming", (series.file,))
            exit()

    ## Get the series name of the file
    series.name_bk = series.original.replace(series.series_path, "").split(os.sep)[1]
    series.name = series.name_bk.replace(" ", "-")

    ## Get the destination directory
    series.dst = os.path.join(series.series_path, series.name_bk, series.season)
    return series

def naming_episode(args):

    ## Get the delimiter of the video filename
    delimiter = delimiter_get(args.file)

    ## Get all information about the episode and season
    path = os.path.abspath(os.path.join(args.file, os.pardir))
    series = Namespace(file=args.file, path=path, delim=delimiter, original=args.source_host, series_path=args.root_host)
    series = analyze_series(series)

    ## Move the file back to the original path
    file_name = "%s.%s.%s%s" % (series.name, series.episode, series.resolution, series.extension)
    file_dst = os.path.join(series.dst, file_name)
    debugmsg("The new file path is", "Naming", (file_dst,))
    return file_dst

###############################################################################
###                               Movies                                    ###
###############################################################################

def analyze_movie(movie):

    ## Get the extensions of the season
    movie.extension = os.path.splitext(movie.file)[1]

    ## Analyze resolution of the season
    movie.resolution = get_resolution(movie.file)
    if(movie.resolution == -1):
        errmsg("The resolution of the movie was invalid", "Naming")
        exit()

    ## Get the real movie name of the file
    movie.name_bk = movie.original.replace(movie.movies_path, "").split(os.sep)[1]
    movie.name = []
    for token in movie.name_bk.split(movie.delim):
        if (token.isdigit() and int(token) > 1925 and int (token) < 2050):
            break
        movie.name.append(token)
    movie.name = " ".join(movie.name)

    ## Get the destination directory
    movie.dst = os.path.join(movie.movies_path, movie.name_bk)
    return movie

def naming_movie(args):

    ## Get the delimiter of the video filename
    delimiter = delimiter_get(args.source_host)

    ## Get all information about the episode and season
    path = os.path.abspath(os.path.join(args.file, os.pardir))
    movie = Namespace(file=args.file, path=path, delim=delimiter,
                      original=args.source_host, movies_path=args.root_host)
    movie = analyze_movie(movie)

    ## Move the file back to the original path
    if (movie.resolution == "2160p"):
        file_name = "%s.%s%s" % (movie.name, movie.resolution, movie.extension)
    else:
        file_name = "%s%s" % (movie.name, movie.extension)
    file_dst = os.path.join(movie.dst, file_name)
    debugmsg("The new file path is", "Naming", (file_dst,))
    return file_dst

if __name__ == "__main__":

    args = argparse.Namespace()
    parser = argparse.ArgumentParser(description='Series naming script')
    parser.add_argument('-f','--file', help='Path to the converted coutput video file', required=True)
    parser.add_argument('-o','--original', help='Path to the original file', required=True)
    args = parser.parse_args()
    args.source_host = args.original
    naming_episode(args)