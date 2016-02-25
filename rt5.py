import os
import struct
import sys
import hashlib

from os import listdir
from os.path import isfile, join

# -mconcat -oout -idir -ppasword

# -m / -s : operation mode [merge / scatter] (keyparam)
# -o : output (default:arch.tr5)
# -p : password (keyparam)
# -l : filelist (default:disdir)
import cifer

DEFAULT_ARCHIVE_NAME = "arch.tr5"

INT_LENGTH = 4

KEY_PASSWORD = "-p"

KEY_MODE = "-m"
KEY_OUT_NAME = "-o"
KEY_INPUT_NAME = "-i"

KEY_HELP_ACTION = "-h"
KEY_VERSION = "-v"

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
    else:
        with open(params[KEY_FILE_LIST]) as flist:
            return [file[:-1] for file in flist]


def extract_param(param_key):
    for param in sys.argv:
        if param.startswith(param_key):
            return param[2:]

    return None


def parse_params():
    operation = extract_param(KEY_MODE)
    if operation is None:
        operation = "help" if extract_param(KEY_HELP_ACTION) is not None else None

    if operation is None:
        operation = "version" if extract_param(KEY_VERSION) is not None else None

    password = extract_param(KEY_PASSWORD)
    input_filename = extract_param(KEY_INPUT_NAME)
    output_filename = extract_param(KEY_OUT_NAME)

    return operation, password, input_filename, output_filename


def concat(params):
    err_code = 0

    md5 = get_md5(params[KEY_PASSWORD].encode())

    out_filename = params[KEY_OUTPUT_NAME] if KEY_OUTPUT_NAME in params.keys() else DEFAULT_ARCHIVE_NAME

    file_list = parse_file_list(params)

    try:

        ofile = open(out_filename, 'wb+')

        # writing password
        # length
        ofile.write(len(md5).to_bytes(INT_LENGTH, 'big'))
        ofile.write(bytearray(md5))

        ofile.write(len(file_list).to_bytes(INT_LENGTH, 'big'))

        for filename in file_list:

            try:
                file = open(filename, 'rb+')
                file_statistics = os.stat(filename)

                ofile.write(len(filename).to_bytes(INT_LENGTH, 'big'))
                ofile.write(bytes(filename.encode()))
                ofile.write(file_statistics.st_size.to_bytes(INT_LENGTH, 'big'))

                with open(filename, 'rb+') as file_2_copy:
                    size = file_statistics.st_size
                    buf_size = 2048

                    while size > 0:
                        read_size = buf_size if size > buf_size else size
                        ofile.write(cifer.encrypt(file_2_copy.read(read_size)))
                        size -= read_size

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
    filename = struct.unpack('%ds' % name_size, file.read(name_size))[0].decode('utf-8')

    filesize = struct.unpack('>I', file.read(INT_LENGTH))[0]

    return filename, filesize


def scatter(params):
    err_code = 0

    filename = params[KEY_INPUT_FILE_NAME] if KEY_INPUT_FILE_NAME in params.keys() else DEFAULT_ARCHIVE_NAME

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

        buf = ifile.read(INT_LENGTH)
        files_amount = struct.unpack('>L', buf)[0]

        containing_dir = os.path.join(os.getcwd(), params[KEY_OUTPUT_NAME] if KEY_OUTPUT_NAME in params.keys() else "")

        for x in range(0, files_amount):
            cur_filename, cur_filesize = get_file_data(ifile)

            if not os.path.exists(containing_dir):
                os.makedirs(containing_dir)

            ofile = open(os.path.join(containing_dir, cur_filename), "wb+")

            while cur_filesize > 0:
                buf_size = 2048
                read_size = buf_size if cur_filesize > buf_size else cur_filesize
                ofile.write(cifer.decrypt(ifile.read(read_size)))
                cur_filesize -= buf_size

            ofile.close()

        ifile.close()

    except Exception as e:
        print("Error while reading: " + e.strerror)
        err_code = 3
    finally:
        ifile.close()

    return err_code


def man():
    print("""
    Disclaimer: Developer doesn't take any responsibility for harm that this script may bring to your PC.
    This scrip does no guarantee the high level of information security or data compression.

    Script parameters:

        -p - password (key param)
    """)


def verssion():
    print("Hider v0.0b")


def main():
    operation, password, input_filename, output_filename = parse_params()

    operations = {"concat": concat, "scatter": scatter, "help": man, "version": verssion}

    if operation is None:
        print("I don't know what to do.")
        return 2

    operations[operation](password, input_filename, output_filename)

    # try:
    #
    #     is_concat = KEY_CONCAT_OPERATION in params.keys()
    #     is_scatter = KEY_SCATTER_OPERATION in params.keys()
    #     show_help = KEY_HELP_OPERATION in params.keys()
    #
    #     if show_help:
    #         help()
    #         return 0
    #
    #     if KEY_PASSWORD not in params.keys():
    #         print("You didn't say magic word")
    #         return 2
    #
    #     if (is_concat and is_scatter) or (not is_concat and not is_scatter):
    #         print("I don't know what to do")
    #         return 1
    #
    #     if is_concat:
    #         return concat(params)
    #     elif is_scatter:
    #         return scatter(params)
    #
    #
    #
    # except Exception as e:
    #     print("error while merging: " + e.strerror)
    #     return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
