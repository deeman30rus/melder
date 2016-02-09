import os
import struct
import sys
import hashlib

from os import listdir
from os.path import isfile, join

# -m / -s : operation mode [merge / scatter] (keyparam)
# -o : output (default:arch.tr5)
# -p : password (keyparam)
# -l : filelist (default:disdir)

DEFAULT_OUTPUT_NAME = "arch.tr5"

INT_LENGTH = 4

KEY_PASSWORD = "-p"

KEY_CONCAT_OPERATION = "-c"
KEY_SCATTER_OPERATION = "-s"

KEY_FILE_LIST = "-l"
KEY_OUTPUT_NAME = "-o"

KEY_INPUT_FILE_NAME = "-f"


def get_md5(value):
    m = hashlib.md5()
    m.update(value)

    return m.digest()


def parse_file_list(params):
    if KEY_FILE_LIST not in params.keys():
        for filename in os.listdir():
            thisdir = os.path.dirname(os.path.abspath(__file__))
            return [f for f in listdir(thisdir) if f != "rt5.py" and isfile(join(thisdir, f))]


def parse_param(param):
    if param.startswith(KEY_FILE_LIST):
        return KEY_FILE_LIST, param[2:]
    elif param.startswith(KEY_PASSWORD):
        return KEY_PASSWORD, param[2:]
    elif param.startswith(KEY_OUTPUT_NAME):
        return KEY_OUTPUT_NAME, param[2:]
    elif param.startswith(KEY_CONCAT_OPERATION):
        return KEY_CONCAT_OPERATION, "true"
    elif param.startswith(KEY_SCATTER_OPERATION):
        return KEY_SCATTER_OPERATION, "true"
    elif param.startswith(KEY_INPUT_FILE_NAME):
        return KEY_INPUT_FILE_NAME, param[2:]

    return None


def concat(params):
    err_code = 0

    md5 = get_md5(params[KEY_PASSWORD].encode())

    out_filename = params[KEY_OUTPUT_NAME] if KEY_OUTPUT_NAME in params.keys() else DEFAULT_OUTPUT_NAME

    file_list = parse_file_list(params);
    try:

        ofile = open(out_filename, 'wb+')

        # writing password
        # length
        ofile.write(len(md5).to_bytes(INT_LENGTH, 'big'))
        ofile.write(bytearray(md5))

        for filename in file_list:
            print(filename)
            try:
                file = open(filename, 'rb+')
                file_statistics = os.stat(filename)

                head = struct.pack('%ds' % (INT_LENGTH * 2 + len(filename)),
                                   bytes(("%d%s%d" % (len(filename), filename, file_statistics.st_size)).encode()))

                ofile.write(head)

            except Exception as e:

                err_code = 3
            finally:
                file.close()

        ofile.close()

    except Exception as e:

        print("error while writing file: " + e.strerror)
        err_code = 3
    finally:
        ofile.close()

    return err_code


def get_file_data(file):

    name_size = struct.unpack('>I', file.read(INT_LENGTH))[0]
    filename = struct.unpack('%ds' % name_size, file.read(name_size))[0]

    filesize = struct.unpack('>I', file.read(INT_LENGTH))[0]

    return filename, filesize


def scatter(params):
    err_code = 0

    filename = params[KEY_INPUT_FILE_NAME] if KEY_INPUT_FILE_NAME in params.keys() else DEFAULT_OUTPUT_NAME

    try:

        ifile = open(filename, 'rb+')

        buf = ifile.read(INT_LENGTH)  # md5 length read
        md5len = struct.unpack('>L', buf)[0]

        buf = ifile.read(md5len)  # reading md5
        md5 = struct.unpack('%ds' % md5len, buf)[0]

        if md5 != get_md5(params[KEY_PASSWORD].encode()):
            ifile.close()
            print("wrong password")
            return 4

        cur_filename, cur_filesize = get_file_data(ifile)

        print("name: %s, size: %d", cur_filename, cur_filesize)

        ifile.close()

    except Exception as e:
        print("Error while reading: " + e.strerror)
    finally:
        ifile.close()

    return err_code


def main():
    params = {}

    for arg in sys.argv[1:]:
        pair = parse_param(arg)

        if pair is None:
            print("parse params error")
            return 1

        params[pair[0]] = pair[1]

    if KEY_PASSWORD not in params.keys():
        print("You didn't say magic word")
        return 2

    try:

        is_concat = KEY_CONCAT_OPERATION in params.keys()
        is_scatter = KEY_SCATTER_OPERATION in params.keys()

        if (is_concat and is_scatter) or (not is_concat and not is_scatter):
            print("I don't know what to do")
            return 1

        if is_concat:
            return concat(params)
        elif is_scatter:
            return scatter(params)

    except Exception as e:
        print("error while merging: " + e.strerror)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
