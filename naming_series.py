import sys, os, re, argparse, subprocess
from shutil import move
from collections import Counter
from argparse import Namespace

## Add modules from the submodule (vs-utils)
cur_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(cur_dir, "VS-Utils"))
sys.path.append(os.path.join(cur_dir, "VS-SynoIndex"))
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
    if (len(stderr) > 1): print(stderr)

    ## Parse the mediainfo output as dictionary
    mediainfo_output = stdout.split("\n")
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

def analyze_series(series):

    ## Get all file names inside the season
    path = series.path

    ## Get the extensions of the season
    series.extension = os.path.splitext(series.file)[1]

    ## Analyze resolution of the season
    series.resolution = get_resolution(series.file)
    if(series.resolution == -1):
        print("The resolution of the series episode was invalid")
        exit()

    ## Analyze the current season number
    splitted = series.file.split(series.delim)
    season_ep = [f for f in splitted if "s0" in f.lower() or "s1" in f.lower()][0]
    series.season = "{}".format(re.split('s|e', season_ep.lower())[1])
    series.episode = "S%sE%s" % (series.season, re.split('s|e', season_ep.lower())[2])
    series.season = "%s %s" % (season_desc, series.season)

    ## Get the series name of the file
    series.name = series.original.replace(series.series_path, "").split(os.sep)[1].replace(" ", "-")

    ## Get the destination directory
    series.dst = os.path.join(series.series_path, series.name, series.season)
    return series

def naming_episode(args):

    ## Get the delimiter of the video filename
    delimiters = [".", "-", "_"]
    delimiter_count = Counter(args.file).most_common()
    delimiter_count = [(key, val) for key, val in delimiter_count if key in delimiters]
    delimiter = sorted(delimiter_count, key=lambda x: x[1])[-1][0]

    ## Get all information about the episode and season
    path = os.path.abspath(os.path.join(args.file, os.pardir))
    series = Namespace(file=args.file, path=path, delim=delimiter, original=args.source_host, series_path=args.root_host)
    series = analyze_series(series)

    ## Move the file back to the original path
    file_name = "%s.%s.%s%s" % (series.name, series.episode, series.resolution, series.extension)
    file_dst = os.path.join(series.dst, file_name)
    debugmsg("The new file path is", (file_dst,))
    return file_dst

if __name__ == "__main__":

    args = argparse.Namespace()
    parser = argparse.ArgumentParser(description='Series naming script')
    parser.add_argument('-f','--file', help='Path to the converted coutput video file', required=True)
    parser.add_argument('-o','--original', help='Path to the original file', required=True)
    args = parser.parse_args()
    args.source_host = args.original
    naming_episode(args)