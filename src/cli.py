import src.common.input as input
import src.common.output as output

import sys

supported_arguments = {
    '--input':'--input=FOLDER_NAME - input folder with all kmls'
}

def print_supported():
    print('Supported inputs:')
    for arg, usage in supported_arguments.items():
        print(usage)

def parse_argvs():
    if (len(sys.argv) < 2):
        print("Too few arguments:")
        print_supported()
        exit(1)

    for i in range(1, len(sys.argv)):
        argv_splitted = sys.argv[i].split('=')
        if len(argv_splitted) != 2:
            print('Error argument format: ' + sys.argv[i])
            exit(1)
        arg, value = argv_splitted
        if arg in supported_arguments:
            match arg:
                case '--input':
                    input.folder = value
                    output.file = value + "-tiled"
        else:
            print('\'' + arg + '\'' + ' is not supported')
            print_supported()
            exit(1)
