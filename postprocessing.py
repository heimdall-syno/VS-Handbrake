#################################################
##           Scope: Docker-Container           ##
#################################################
import os, sys, time, argparse, subprocess
from datetime import datetime

## Add modules from the submodule (vs-utils)
cur_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(cur_dir, "VS-Utils"))
sys.path.append(os.path.join(cur_dir, "VS-SynoIndex"))
from naming_series import naming_episode
from parse import parse_cfg
from client import client

def get_convert_source_path(args):
    """ Get the convert file path and the source path inside it.

    Arguments:
        args {Namespace} -- Namespace containing the shell arguments.

    Returns:
        tuple -- (convert file path, source file path)
    """

    ## check whether the convert directory exists
    file_name = os.path.basename(args.file)
    convert_file = "%s.txt" % os.path.splitext(file_name)[0]
    convert_path = os.path.abspath(os.path.join("data", "convert"))
    if not os.path.isdir(convert_path):
        exit("Error: Seems like the data mount does not exist, [VS-Handbrake] -> /data")

    ## check whether the convert file exists
    args.convert_path = os.path.join(convert_path, convert_file)
    if args.test:
        args.convert_path = args.convert_path.replace("convert", "test")
    if not os.path.isfile(args.convert_path):
        exit("Error: Convert file does not exist")

    ## Get the source path
    with open(convert_path, "r") as f:
        args.root_host = f.readlines()[0].split(":")[1]
        args.source_host = f.readlines()[1].split(":")[1]
        args.output_host = f.readlines()[2].split(":")[1]
    return args

def processing_file(cfg, args):

    ## Check the file type
    file_dst = None
    if any(season_type in args.root_host.split(os.sep) for season_type in cfg.handbrake_series):
        print("  Type: Episode")
        file_dst = naming_episode(args)

    elif any(season_type in args.root_host.split(os.sep) for season_type in cfg.handbrake_series):
        print("  Type: Movie")
        print("  NOT SUPPORTED RIGHT NOW")
        #file_dst = naming_movies(args)
    else:
        exit("Error: Unsupported type of converted file")

    ## Delete the corresponding convert file and add to synoindex
    if file_dst:
        print("Delete convert file at %s" % (args.convert_path))
        os.remove(args.convert_path)
        print("Add to synoindex database")
        client(file_dst, args.output_host)

def main():
    """ Name:    VS-Handbrake (Part of the VS-Package)
        Summary: After handbrake finished the convertion process, the script is called and
                 handles the right naming for the video file and relocates it according to
                 its video type (episode or movie).
    """

    ## Get the shell arguments
    args = argparse.Namespace()
    parser = argparse.ArgumentParser(description='Naming and locate script for Handbrake docker container')
    parser.add_argument('-f','--file', help='Path to the video file', required=True)
    parser.add_argument('-t','--test', help='Testing mode', action='store_true', required=False)
    args = parser.parse_args()

    ## Parse the config
    config_file = os.path.join(cur_dir, "config.txt")
    cfg = parse_cfg(config_file, "vs-handbrake", "docker")

    ## Print the date and the file
    cur_date = datetime.strftime(datetime.now(), "%Y-%m-%d-%H-%M")
    print("[%s] Handbrake finished converting file: %s" % cur_date, args.file)

    ## Check for the source file, continue if convert file doesnt exist
    args = get_convert_source_path(args)

    ## Check which media type it is and process it accordingly
    processing_file(cfg, args)

if __name__ == "__main__":
    main()