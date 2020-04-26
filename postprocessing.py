import os, sys, time, argparse, subprocess
from datetime import datetime

## Add modules from the submodule (VS-Utils)
cur_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(cur_dir, "VS-Utils"))
from prints import errmsg, debugmsg, infomsg, init_logging
from naming import naming_episode, naming_movie
from parse import parse_cfg
from scope import scope_get
from client import client

def switch_original(original):
    switcher = { 0: "leave", 1: "ignore", 2: "delete", 3: "delete|ignore"}
    return switcher.get(original, "Invalid original mode")

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
    convert_path = os.path.join(os.sep, "convert")
    if not os.path.isdir(convert_path):
        errmsg("Seems like the data mount does not exist, [VS-Handbrake] -> /convert", "Postprocessing"); exit()

    ## check whether the convert file exists
    args.convert_path = os.path.join(convert_path, convert_file)
    if not os.path.isfile(args.convert_path):
        errmsg("Convert file does not exist"); exit()

    ## Get the source path
    with open(args.convert_path, "r") as f: lines = f.readlines()
    convert_args = [l.replace("\n", "").split(":")[1] for l in lines]
    args.root_host, args.source_host, args.output_host = convert_args
    return args

def processing_file(cfg, args):

    ## Check the file type
    file_dst = None
    if any(file_type in args.root_host.split(os.sep) for file_type in cfg.series):
        infomsg("Type: Episode", "Postprocessing")
        file_dst = naming_episode(args, cfg)

    elif any(file_type in args.root_host.split(os.sep) for file_type in cfg.movies):
        infomsg("Type: Movie", "Postprocessing")
        file_dst = naming_movie(args)
    else:
        exit("Error: Unsupported type of converted file")

    ## Delete the corresponding convert and watch file and add to synoindex
    if file_dst:
        debugmsg("Delete convert file", "Postprocessing", (args.convert_path,))
        os.remove(args.convert_path)

        watch_path = os.path.join(os.sep, "watch", os.path.basename(args.output_host))
        debugmsg("Delete watch file", "Postprocessing", (watch_path,))
        os.remove(watch_path)

        msg = "Add converted file to synoindex and {} original file".format(switch_original(cfg.original))
        infomsg(msg, "Postprocessing")
        client(args.scope, cfg.port, file_dst, args.output_host, args.source_host, cfg.original)

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
    args = parser.parse_args()
    args.script_dir = cur_dir
    args.scope = scope_get()

    ## Parse the config
    config_file = os.path.join(cur_dir, "config.txt")
    cfg = parse_cfg(config_file, "vs-handbrake", "docker")

    ## Initialize the logging
    init_logging(args, cfg)

    ## Print the date and the file
    infomsg("Handbrake finished converting file", "Postprocessing", (args.file,))

    ## Check for the source file, continue if convert file doesnt exist
    args = get_convert_source_path(args)

    ## Check which media type it is and process it accordingly
    processing_file(cfg, args)

if __name__ == "__main__":
    main()
