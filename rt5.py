import hashlib
import os
import pickle
import sys
from os import listdir

# -mconcat -oout -idir -ppasword

import cifer

DEFAULT_ARCHIVE_NAME = "arch.tr5"
DEFAULT_ARCHIVE_OUT_DIR = "out"

INT_LENGTH = 4

KEY_PASSWORD = "-p"

KEY_MODE = "-m"
KEY_OUT_NAME = "-o"
KEY_INPUT_NAME = "-i"

KEY_HELP_ACTION = "-h"
KEY_VERSION = "-v"


def get_md5(value):
    m = hashlib.md5()
    m.update(bytes(value))
    return m.digest()


def parse_params():
    params = {}

    for param in sys.argv:
        if not param.startswith('-'):
            continue

        params[param[:2]] = param[2:]

    if len(set(params.keys()).intersection((KEY_MODE, KEY_HELP_ACTION, KEY_VERSION))) != 1:
        raise Exception("Operation mismatch")

    if KEY_HELP_ACTION in params.keys():
        return "man", None, None, None

    if KEY_VERSION in params.keys():
        return "version", None, None, None

    if KEY_PASSWORD not in params.keys():
        raise Exception("You didn't say magic word")

    operation = params[KEY_MODE]
    password = params[KEY_PASSWORD]
    input_file = params[KEY_INPUT_NAME] if KEY_INPUT_NAME in params.keys() else None
    output_file = params[KEY_OUT_NAME] if KEY_OUT_NAME in params.keys() else None

    return operation, password, input_file, output_file


def get_files(input_filename):
    if not os.path.isdir(input_filename):
        return None

    return listdir(input_filename)


def concat(password, input_dir, output_filename):
    files = get_files(input_dir)

    if len(files) == 0:
        return 1

    with open(output_filename, 'wb+') as ofile:
        pickle.dump(get_md5(password.encode()), ofile)
        pickle.dump(len(files), ofile)

        for filename in files:
            filepath = os.path.join(input_dir, filename)
            with open(filepath, 'rb+') as file_2_copy:
                buf_size = 2048
                size = os.stat(filepath).st_size

                pickle.dump(size, ofile)
                pickle.dump(filename, ofile)

                while size > 0:
                    read_size = buf_size if size > buf_size else size
                    ofile.write(cifer.encrypt(file_2_copy.read(read_size), password))
                    size -= read_size

    return 0


def scatter(password, input_filename, output_dir):
    with open(input_filename, 'rb') as ifile:
        pswd = pickle.load(ifile)
        files_amount = pickle.load(ifile)

        if pswd != get_md5(password.encode()):
            return 1

        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        for i in range(files_amount):
            size = pickle.load(ifile)
            filename = os.path.join(output_dir, pickle.load(ifile))

            with open(filename, 'wb+') as file:
                buf_size = 2048
                while size > 0:
                    read_size = buf_size if size > buf_size else size
                    file.write(cifer.decrypt(ifile.read(read_size), password))
                    size -= read_size

    return 0


def man():
    print("""
    Disclaimer: Developer doesn't take any responsibility for harm that this script may bring to your PC.
    This scrip does no guarantee the high level of information security or data compression.

    Script parameters:

        -p - password (key param)
    """)


def version():
    print("Hider v0.5b")


def main():
    operation, password, input_file, output_file = parse_params()

    if operation == "man":
        man()
    elif operation == "version":
        version()
    elif operation == "concat":

        if input_file is None:
            raise Exception("point me input dir")

        output_file = DEFAULT_ARCHIVE_NAME if output_file is None else output_file

        if concat(password, input_file, output_file):
            raise Exception("Error during concat")

    elif operation == "scatter":

        input_file = DEFAULT_ARCHIVE_NAME if input_file is None else input_file
        output_file = DEFAULT_ARCHIVE_OUT_DIR if output_file is None else output_file

        if scatter(password, input_file, output_file):
            raise Exception("Error during scatter")

    return 0


if __name__ == "__main__":
    sys.exit(main())
