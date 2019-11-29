import os, sys, time, argparse, subprocess
from datetime import datetime
from parse import parse_cfg, validate_input

from parse import parse_cfg
from naming_series import naming_episode

## Parse the config
config_file = os.path.dirname(os.path.abspath(__file__)) + '/config.txt'
cfg = parse_cfg(config_file)

def server(filepath):
    """ Validate the query, get all media infos and add it.

    Arguments:
        filepath {string} -- Converted and relocated video file path.
    """

    ## Check whether file exists
    print("[!] Get new query for file (%s)" % filepath)
    if not os.path.isfile(filepath):
        exit("[-] Error: Filepath seems invalid")

    ## Add file to synoindex database
    cmds = ['synoindex', '-A', filepath.encode('UTF-8')]
    print("[x] Executed query: synoindex -A %s " % filepath.encode('UTF-8'))
    p = subprocess.Popen(cmds, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.communicate()

def get_source_path(convert):
    """ Get the video source path of the convert file.

    Arguments:
        convert {string} -- Path to the convert file inside the handbrake docker mapping.

    Returns:
        string -- Video source path.
    """

    with open(convert, "r") as f: source_path = f.readlines()[0]
    return source_path

def get_convert_path(args):
    """ Get the convert file path and the source path inside it.

    Arguments:
        args {Namespace} -- Namespace containing the shell arguments.

    Returns:
        tuple -- (convert file path, source file path)
    """

    file_name = os.path.basename(args.file)
    convert_file = "%s.txt" % os.path.splitext(file_name)[0]
    convert_path = os.path.join(cfg.handbrake, "convert", convert_file)
    if args.test:
        convert_path = convert_path.replace("convert", "test")
    if not os.path.isfile(convert_path):
        exit("Convert file does not exist")
    source_path = get_source_path(convert_path)
    return (convert_path, source_path)

def processing_file(file_name, source_path, convert_path):

    ## Create the namespace for the naming methods
    args = argparse.Namespace(file=file_name, original=source_path)

    ## Check the file type
    file_dst = None
    if any(season_type in source_path.split(os.sep)[2] for season_type in cfg.handbrake_series):
        print("  Type: Episode")
        file_dst = naming_episode(args)

    elif any(season_type in source_path.split(os.sep)[2] for season_type in cfg.handbrake_series):
        print("  Type: Movie")
        print("  NOT SUPPORTED RIGHT NOW")
        #file_dst = naming_movies(args)
    else:
        exit("Unsupported type of converted file")

    ## Delete the corresponding convert file and add to synoindex
    if file_dst:
        print("Delete convert file at %s" % (convert_path))
        os.remove(convert_path)
        server(file_dst)

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

    ## Print the date and the file
    cur_date = datetime.strftime(datetime.now(), "%Y-%m-%d-%H-%M")
    print("[%s] Handbrake finished converting file: %s" % cur_date, args.file)

    ## Check for the source file, continue if convert file doesnt exist
    (convert_path, source_path) = get_convert_path(args)

    ## Check which media type it is and process it accordingly
    processing_file(args.file, source_path, convert_path)

if __name__ == "__main__":
    main()