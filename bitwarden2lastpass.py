#!/usr/bin/env python3
 
import csv
import errno
import getopt
import inspect
import ntpath
import os
from pathlib import Path
import platform
import re
import logging
from logging.handlers import RotatingFileHandler
import sys

VERSION = "20181209-linux"

LOG_FORMAT = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) - %(message)s')
LOGLEVEL = logging.DEBUG # one of (logging.CRITICAL, logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG, logging.NOTSET)
LOGFILE = "journal.txt"  # or set to "/dev/null" to completely ride of logs"

if platform.system() == "Windows":
    # LOGFILE_PATH = F"{os.environ['USERPROFILE']}/bitwarden2lastpass" # => C:\Users\<name>
    LOGFILE_PATH = F"{os.environ['APPDATA']}\\bitwarden2lastpass" # => C:\Users\<name>\AppData\Roaming
else:
    LOGFILE_PATH = F"{os.environ['HOME']}/.cache/bitwarden2lastpass"

try:
    os.makedirs(LOGFILE_PATH)
except OSError as e:
    if e.errno != errno.EEXIST:
        raise

LOGFILE = LOGFILE_PATH + "/journal.txt"
# LOGFILE = "/dev/null"

# logging.disable(sys.maxsize) # but file journal.txt is still created with 0 byte.

my_handler = RotatingFileHandler(LOGFILE, mode='a', maxBytes=1*1024*1024, backupCount=2, encoding=None, delay=0)    
my_handler.setFormatter(LOG_FORMAT)
my_handler.setLevel(LOGLEVEL) 

logger = logging.getLogger()
logger.setLevel(LOGLEVEL)
logger.addHandler(my_handler)


class BitwardenCsvConverterToolbox:
    def __init__(self):
        self.bitwarden_data = []
        self.bitwarden_firstline = "folder,favorite,type,name,notes,fields,login_uri,login_username,login_password,login_totp"
        self.bitwarden_header = ["bw_folder", "bw_favorite", "bw_type", "bw_name", "bw_notes", "bw_fields", 
                "bw_login_uri", "bw_login_username", "bw_login_password", "bw_login_totp"]
        self.lastpass_header  = ["url", "username", "password", "extra", "name", "grouping", "fav"]
        self.last_file_bitwarden_opened = ""
        self.last_file_lastpass_generated = ""
        self.msg = []

    def displaylog(self):
        for l in self.msg:
            print(l)
    
    def logger_function_in(self, where_i_am):
        logger.info(F"enter in fct '{where_i_am}()'")
        #logger.info(F"enter in fct '{inspect.stack()[1][3].f_code.co_name}()'")
        

    def logger_function_out(self, where_i_am):
        logger.info(F"exit from fct '{where_i_am}()'")
        #logger.info(F"exit from fct  '{inspect.stack()[0][3].f_code.co_name}()'")
    
    def read_bitwarden_file(self, fullpathfile_csv):
        """Read the bitwarden file in memory."""
        self.logger_function_in(sys._getframe().f_code.co_name)
        #logger.info(F"enter in fct: {inspect.currentframe().f_code.co_name}")
        myfile = Path(fullpathfile_csv)
        self.bitwarden_data = []
        if not myfile.is_file():
            msg = F"file '{fullpathfile_csv}' is not a file! Aborting."
            self.last_file_bitwarden_opened = ''
            self.msg.append(msg)
            logger.debug(msg)
            self.logger_function_out(sys._getframe().f_code.co_name)
            return False
        self.last_file_bitwarden_opened = fullpathfile_csv
        try:
            logger.info(F"open '{fullpathfile_csv}'")
            file_r = open(fullpathfile_csv, encoding='utf-8', newline='')
            reader = csv.reader(file_r)
            header = next(reader) # the first line is the header
            header_string = ','.join(header)
            if header_string != self.bitwarden_firstline:
                msg = F"CSV header from '{fullpathfile_csv}' mismatchs with fields from a BitWarden CSV exportfile! Aborting."
                self.msg.append(msg)
                logger.critical(msg)
                self.logger_function_out(sys._getframe().f_code.co_name)
                file_r.close
                return False
            data = []
            for row in reader:
                bw_folder, bw_favorite, bw_type, bw_name, bw_notes, bw_fields, bw_login_uri, \
                bw_login_username, bw_login_password, bw_login_totp = row
                data.append([bw_folder, bw_favorite, bw_type, bw_name, bw_notes, bw_fields, bw_login_uri, 
                            bw_login_username, bw_login_password, bw_login_totp])
            file_r.close
            self.bitwarden_data = data
            msg = F"{len(data)} lines read from file '{fullpathfile_csv}'."
            self.msg.append(msg)
            logger.info(msg)
            self.logger_function_out(sys._getframe().f_code.co_name)
            return True
        except Exception as e:
            file_r.close
            msg = F"Exception ({e}) occured when reading file '{fullpathfile_csv}'. Aborting."
            self.msg.append(msg)
            logger.error(msg)
            self.logger_function_out(sys._getframe().f_code.co_name)
            return False

    def create_lastpass_file(self, fullpathfile_csv):
        """Create the lastpass file on disk."""
        self.logger_function_in(sys._getframe().f_code.co_name)
        mypath = os.path.dirname(fullpathfile_csv)
        if  mypath != '': # On Windows, os.path.dirname(file_without_directory) returns an empty string. and 
            try:
                os.makedirs(mypath)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
            logger.info(F"create '{fullpathfile_csv}'")
        self.last_file_lastpass_generated = fullpathfile_csv
        try:
            file_w = open(fullpathfile_csv, 'w', encoding='utf-8', newline='')
            writer = csv.writer(file_w)
            writer.writerow(self.lastpass_header)
            for i in range(len(self.bitwarden_data)-1):
                row = self.bitwarden_data[i]
                lp_url = row[6]
                lp_username = row[7]
                lp_password = row[8]
                lp_extra = row[4]
                lp_name = row[3]
                lp_grouping = row[0]
                lp_fav = "" # this field in Lastpass ??
                writer.writerow([lp_url, lp_username, lp_password, lp_extra, lp_name, lp_grouping, lp_fav]) 
            file_w.close
            msg = F"file '{fullpathfile_csv}' fully created."
            self.msg.append(msg)
            logger.info(msg)
            self.logger_function_out(sys._getframe().f_code.co_name)
            return True
        except Exception as e:
            file_w.close
            self.last_file_lastpass_generated = ""
            msg = F"Exception ({e}) occured when writing file '{fullpathfile_csv}'. Aborting."
            self.msg.append(msg)
            logger.error(msg)
            self.logger_function_out(sys._getframe().f_code.co_name)
            return False

    def convert_bitwarden_exportfile_to_lastpass_exportfile(self, bitwarden_file, lastpass_file):
        """Read a bitwarden CSV-file and convert it in Lastpass CSV-file."""
        self.logger_function_in(sys._getframe().f_code.co_name)
        rc = self.read_bitwarden_file(bitwarden_file)
        if rc:
            rc = self.create_lastpass_file(lastpass_file)
        self.logger_function_out(sys._getframe().f_code.co_name)
        return rc

    def convert_exportfile_to_lastpass(self, bitwarden_file):
        """Read a bitwarden CSV-file, convert it in Lastpass CSV-file with a replaced name 'lastpass'."""
        self.logger_function_in(sys._getframe().f_code.co_name)
        rc = self.read_bitwarden_file(bitwarden_file)
        if rc:
            lp_path_csv = bitwarden_file.replace("bitwarden", "lastpass")
            rc = self.create_lastpass_file(lp_path_csv)
        self.logger_function_out(sys._getframe().f_code.co_name)
        return rc

    def convert_last_exportfile_to_lastpass(self, directory_to_scan='.'):
        """Search the most recent bitwarden CSV-file in the directory and convert it in Lastpass CSV-file with a replaced name 'lastpass'."""
        self.logger_function_in(sys._getframe().f_code.co_name)
        logger.info(F"directory_to_scan = '{directory_to_scan}'")
        # mypath = os.path.dirname(directory_to_scan)
        if not os.path.isdir(directory_to_scan):
            self.last_file_bitwarden_opened = ""
            self.last_file_lastpass_generated = ""
            self.bitwarden_data = []
            msg = F"directory '{directory_to_scan}' do not exist! Abort"
            self.msg.append(msg)
            logger.debug(msg)
            self.logger_function_out(sys._getframe().f_code.co_name)
            return False
        files = [f for f in os.listdir(directory_to_scan) if re.match(r'bitwarden_export_.*\.csv', f)]
        files.sort()
        path_bitwarden_csv = ''.join(files[-1:])
        if path_bitwarden_csv == '':
            msg = F"no file to convert in directory '{directory_to_scan}'! Aborting."
            self.msg.append(msg)
            logger.debug(msg)
            self.logger_function_out(sys._getframe().f_code.co_name)
            return False
        rc = self.convert_exportfile_to_lastpass(path_bitwarden_csv)
        self.logger_function_out(sys._getframe().f_code.co_name)
        return rc

def usage(prog):
    print(F"{prog} -i <inputfile> -o <outputfile> -d <directory>")
    texte =  \
F"""
Usage:
  {prog} 
         detect the last bitwarden exxport file in the current directory and convert it to a compatible lastpass export file.
         (same to '{prog} -d .')
  {prog} -d <directory>
         detect the last bitwarden exxport file in the directory <directory> and convert it to a compatible lastpass export file.
  {prog} -i <export-bitwarden-file>
         convert <export-bitwarden-file> to a compatible lastpass export file, in the same directory.
  {prog} -i <export-bitwarden-file> -o <export-lastpass-file>
         convert <export-bitwarden-file> to a compatible lastpass export file with name : <export-lastpass-file>
  {prog} (-h | --help)
  {prog} --version

Options:
  -h --help     Show this screen.
  -v --version  Show version.

"""
    print(texte)


def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def main(argv):
    PROGNAME = path_leaf(argv[0])
    PROGNAMEFULL = argv[0]
    argv = argv[1:]

    logger.info(F"{PROGNAMEFULL} starts.")

    logger.info("Python {}.{} detected".format(sys.version_info.major, sys.version_info.minor))
    if (sys.version_info.major < 3) or (sys.version_info.major == 3 and sys.version_info.minor < 7):
        msg = "Requires Python >= 3.7 to run. Aborting execution."
        logger.error(msg)
        print(msg)
        sys.exit()      

    directory = '.'
    bitwarden_inputfile = ""
    lastpass_outputfile = ""
    
    logger.info(F"Argv: {argv}")
    
    try:
        opts, args = getopt.getopt(argv,"hi:o:d:",["ifile=","ofile=","dir=","version"])
    except getopt.GetoptError:
        usage(PROGNAME)
        logger.info(F"{PROGNAMEFULL} end.")
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            usage(PROGNAME)
            sys.exit()
        elif opt in ("-i", "--ifile"):
            bitwarden_inputfile = arg
        elif opt in ("-o", "--ofile"):
            lastpass_outputfile = arg
        elif opt in ("-d", "--dir"):
            directory = arg
        elif opt in ("-v", "--version"):
            print(F"Script: {PROGNAMEFULL}\nVersion: {VERSION}")
            sys.exit()

    bitwarden_inputfile = bitwarden_inputfile.strip()
    lastpass_outputfile = lastpass_outputfile.strip()

    obox = BitwardenCsvConverterToolbox()

    if bitwarden_inputfile and lastpass_outputfile:
        rc = obox.convert_bitwarden_exportfile_to_lastpass_exportfile(bitwarden_inputfile, lastpass_outputfile)
        print(F"File read   : {obox.last_file_bitwarden_opened}")
        print(F"File created: {obox.last_file_lastpass_generated}")
        if not rc:
            print("Error in process!")
        obox.displaylog()
    elif lastpass_outputfile:
        print(F"Lastpass filename is '{lastpass_outputfile}'")
        print("")
        print("input Bitwarden filename unknown! Aborting!")
        print("")
        usage(PROGNAME)
        logger.info(F"{PROGNAMEFULL} end.")
        sys.exit(2)
    elif bitwarden_inputfile:
        rc = obox.convert_exportfile_to_lastpass(bitwarden_inputfile)
        print(F"File read   : {obox.last_file_bitwarden_opened}")
        print(F"File created: {obox.last_file_lastpass_generated}")
        if not rc:
            print("Error in process!")
        obox.displaylog()
    elif directory:
        rc = obox.convert_last_exportfile_to_lastpass(directory_to_scan=directory)
        print(F"File read   : {obox.last_file_bitwarden_opened}")
        print(F"File created: {obox.last_file_lastpass_generated}")
        if not rc:
            print("Error in process!")
        obox.displaylog()
    else:
        print("Arguments combinaison mismatched. Aborting!")
        print("")
        usage(PROGNAME)
        logger.info(F"{PROGNAMEFULL} end.")
        sys.exit(2)
    logger.info(F"{PROGNAMEFULL} end.")

main( sys.argv[:])
