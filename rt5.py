import os
import struct
import sys
import hashlib

from os import listdir
from os.path import isfile, join

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


# def parse_file_list(params):
#     if KEY_FILE_LIST not in params.keys():
#         for filename in os.listdir():
#             thisdir = os.path.dirname(os.path.abspath(__file__))
#             return [f for f in listdir(thisdir) if f != "rt5.py" and isfile(join(thisdir, f))]
#     else:
#         with open(params[KEY_FILE_LIST]) as flist:
#             return [file[:-1] for file in flist]

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

    if os.path.isfile(input_filename):
        return [input_filename]

    if os.path.isdir(input_filename):
        thisdir = os.path.dirname(os.path.abspath(__file__))
        return [f for f in listdir(thisdir) if f != "rt5.py" and isfile(join(thisdir, f))]

    return None


def concat(pasword, input_filename, output_filename):

    err_code = 0

    files = get_files(input_filename)

    with open(output_filename, 'wb+') as ofile:


    # md5 = get_md5(params[KEY_PASSWORD].encode())
    #
    # # out_filename = params[KEY_OUTPUT_NAME] if KEY_OUTPUT_NAME in params.keys() else DEFAULT_ARCHIVE_NAME
    #
    # # file_list = parse_file_list(params)
    #
    # try:
    #
    #     ofile = open(out_filename, 'wb+')
    #
    #     # writing password
    #     # length
    #     ofile.write(len(md5).to_bytes(INT_LENGTH, 'big'))
    #     ofile.write(bytearray(md5))
    #
    #     ofile.write(len(file_list).to_bytes(INT_LENGTH, 'big'))
    #
    #     for filename in file_list:
    #
    #         try:
    #             file = open(filename, 'rb+')
    #             file_statistics = os.stat(filename)
    #
    #             ofile.write(len(filename).to_bytes(INT_LENGTH, 'big'))
    #             ofile.write(bytes(filename.encode()))
    #             ofile.write(file_statistics.st_size.to_bytes(INT_LENGTH, 'big'))
    #
    #             with open(filename, 'rb+') as file_2_copy:
    #                 size = file_statistics.st_size
    #                 buf_size = 2048
    #
    #                 while size > 0:
    #                     read_size = buf_size if size > buf_size else size
    #                     ofile.write(cifer.encrypt(file_2_copy.read(read_size)))
    #                     size -= read_size
    #
    #         except Exception as e:
    #
    #             err_code = 3
    #         finally:
    #             file.close()
    #
    #     ofile.close()
    #
    # except Exception as e:
    #
    #     print("error while writing file: " + e.strerror)
    #     err_code = 3
    # finally:
    #     ofile.close()

    return err_code


def get_file_data(file):
    name_size = struct.unpack('>I', file.read(INT_LENGTH))[0]
    filename = struct.unpack('%ds' % name_size, file.read(name_size))[0].decode('utf-8')

    filesize = struct.unpack('>I', file.read(INT_LENGTH))[0]

    return filename, filesize


def scatter(pasword, intput_filename, output_filename):

    err_code = 0

    # filename = params[KEY_INPUT_FILE_NAME] if KEY_INPUT_FILE_NAME in params.keys() else DEFAULT_ARCHIVE_NAME
    #
    # try:
    #
    #     ifile = open(filename, 'rb+')
    #
    #     buf = ifile.read(INT_LENGTH)  # md5 length read
    #     md5len = struct.unpack('>L', buf)[0]
    #
    #     buf = ifile.read(md5len)  # reading md5
    #     md5 = struct.unpack('%ds' % md5len, buf)[0]
    #
    #     if md5 != get_md5(params[KEY_PASSWORD].encode()):
    #         ifile.close()
    #         print("wrong password")
    #         return 4
    #
    #     buf = ifile.read(INT_LENGTH)
    #     files_amount = struct.unpack('>L', buf)[0]
    #
    #     containing_dir = os.path.join(os.getcwd(), params[KEY_OUTPUT_NAME] if KEY_OUTPUT_NAME in params.keys() else "")
    #
    #     for x in range(0, files_amount):
    #         cur_filename, cur_filesize = get_file_data(ifile)
    #
    #         if not os.path.exists(containing_dir):
    #             os.makedirs(containing_dir)
    #
    #         ofile = open(os.path.join(containing_dir, cur_filename), "wb+")
    #
    #         while cur_filesize > 0:
    #             buf_size = 2048
    #             read_size = buf_size if cur_filesize > buf_size else cur_filesize
    #             ofile.write(cifer.decrypt(ifile.read(read_size)))
    #             cur_filesize -= buf_size
    #
    #         ofile.close()
    #
    #     ifile.close()
    #
    # except Exception as e:
    #     print("Error while reading: " + e.strerror)
    #     err_code = 3
    # finally:
    #     ifile.close()

    return err_code


def man():
    print("""
    Disclaimer: Developer doesn't take any responsibility for harm that this script may bring to your PC.
    This scrip does no guarantee the high level of information security or data compression.

    Script parameters:

        -p - password (key param)
    """)


def verssion():
    print("Hider v0.5b")


def main():
    operation, password, input_file, output_file = parse_params()

    if operation == "man":
        man()
    elif operation == "version":
        verssion()
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
