import logging
import os
import sys
import argparse
from datetime import datetime


# %%


class ClassSetupArgparse:
    def __init__(self):
        self.args = self.meth_command_line_args_routine_option()
        self.date = datetime.now()
        self.logfile, self.signal_no = self.meth_return_logfile_name_str()
        self.val_logging_level = self.meth_return_logging_value()
        self.logger = self.meth_setup_logger()
        self.logger.info("initialising log file for SIGNAL: " + self.signal_no)
        self.logger.info("logging level: " + str(self.args.logging_level))
        self.lineage = self.meth_return_input_conditions_lineage_str()
        self.mutations, self.mutations_folder_name = self.meth_return_input_conditions_mutations_str()
        self.data_region = self.meth_return_input_conditions_data_region_str()
        self.path_setup_file, self.path_folder_modules, self.path_folder_working = self.meth_return_folders()
        print(self.path_folder_modules)
        self.path_parent_save_dir = self.meth_setup_parent_save_folder()
        self.path_save_dir = self.meth_setup_save_folder()

    def meth_command_line_args_routine_option(self):
        """
        Sort command line arguments.
        :param:

        :return:
        """
        parser = argparse.ArgumentParser(description="")
        parser.add_argument("--logging_level",
                            "-logging",
                            dest="logging_level",
                            type=str,
                            choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                            default=["ERROR"],
                            required=False,
                            help="optional argument to set the logging level, default set to ERROR")

        parser.add_argument("--routine",
                            "-routine",
                            dest="routine",
                            action="store_true",
                            help="flag to turn on routine analysis")

        group_location = parser.add_mutually_exclusive_group(required=True)
        group_location.add_argument("--online",
                                    "-online",
                                    dest="location",
                                    action="store_true")
        group_location.add_argument("--local",
                                    "-local",
                                    dest="location",
                                    action="store_false")

        # create data information group
        group_data = parser.add_argument_group("data"
                                               "data input/output information")
        group_data.add_argument("--path_data",
                                "-i",
                                dest="path_data",
                                required="-local" in sys.argv and "-f" not in sys.argv,
                                help="directory path of datafiles used for offline running")
        group_data.add_argument("--custom_filename",
                                "-f",
                                dest="filename",
                                required=False,
                                help="custom filename for International of UK (pre-merged) datafile/s")
        group_data.add_argument("--path_save",
                                "-o",
                                dest="path_output",
                                required=False,
                                help="specified save location direction, default will create sub-folder in main.py "
                                     "parent directory")

        # create signal identifier group
        group_identifier = parser.add_argument_group("signal",
                                                     "signal description/identification arguments")
        group_identifier.add_argument("--signal_no",
                                      "-n",
                                      dest="signal_no",
                                      required="-routine" not in sys.argv,
                                      type=str,
                                      help="signal identification number, required if not running routine analysis")
        group_identifier.add_argument("--usher_lineage",
                                      "-l",
                                      dest="lineage",
                                      required=False,
                                      help="UShER lineage (add spec_ for specific)")
        group_identifier.add_argument("--mutations",
                                      "-m",
                                      dest="mutations",
                                      required=False,
                                      nargs="+",
                                      default=[],
                                      help="mutation/s in format E:484K, for multiple create space seperated list")
        group_identifier.add_argument("--variant",
                                      "-v",
                                      dest="variant",
                                      required=False,
                                      help="variant reference")
        group_identifier.add_argument("--data_region",
                                      "-r",
                                      dest="data_region",
                                      choices=["uk", "int"],
                                      required="-routine" not in sys.argv,
                                      help="option to select International or UK analysis to be run, required if not"
                                           "running routine analysis")
        args = parser.parse_args()
        print(args)
        return args

    def meth_return_routine_signal_parameters(self):
        if self.args.signal_no is None:
            args_signal_no = "routine"
            return args_signal_no
        else:
            args_signal_no = self.args.signal_no
            return args_signal_no

    def meth_return_logfile_name_str(self):
        signal_no = self.meth_return_routine_signal_parameters()
        logfile = "LOGFILE_" + self.date.strftime("%Y%m%d") + "_" + signal_no + ".log"
        return logfile, signal_no

    def meth_return_logging_value(self):
        """
        Return logging value from string selection input.
        :return:
        """
        if self.args.logging_level == "INFO":
            level = logging.INFO
        elif self.args.logging_level == "DEBUG":
            level = logging.DEBUG
        elif self.args.logging_level == "WARNING":
            level = logging.WARNING
        elif self.args.logging_level == "ERROR":
            level = logging.ERROR
        elif self.args.logging_level == "CRITICAL":
            level = logging.CRITICAL
        else:
            level = logging.INFO
        return level

    def meth_setup_logger(self):
        # clear/rest handlers
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        logging.basicConfig(filename=self.logfile,
                            filemode="a",
                            level=self.meth_return_logging_value(),
                            format="%(asctime)s %(levelname)s: %(message)s",
                            datefmt="%d/%m/%y %H:%M:%S")
        logger = logging.getLogger(self.logfile)
        return logger

    def meth_return_input_conditions_lineage_str(self):
        if self.args.lineage is not None:
            temp_lineage = self.args.lineage
        elif self.args.variant is not None:
            temp_lineage = self.args.variant
        else:
            temp_lineage = "no_specified_lineage"
        self.logger.info("lineage: " + temp_lineage)
        return temp_lineage

    def meth_return_input_conditions_mutations_str(self):
        temp_mutations = ",".join(self.args.mutations)
        temp_mutations_folder_name = self.args.mutations.copy()
        if not temp_mutations:
            temp_mutations = "no_specified_mutations"
            # set up folder conditions
            temp_mutations_folder_name = "no_specified_mutations"
        elif len(temp_mutations_folder_name) <= 3:
            temp_mutations_folder_name = "_".join(temp_mutations_folder_name)
        elif len(temp_mutations_folder_name) > 3:
            temp_mutations_folder_name = "various_specified_mutations"
        elif "any" in temp_mutations_folder_name:
            temp_mutations_folder_name = "any_of_specified_mutations"
        self.logger.info("mutations: " + temp_mutations)
        return temp_mutations, temp_mutations_folder_name

    def meth_return_input_conditions_data_region_str(self):
        """
        Select location of analysis UK vs INT
        """
        if self.args.data_region == "int":
            temp_data_region = "int"
            self.logger.info("data_region: " + temp_data_region)
            return temp_data_region
        elif self.args.data_region == "uk":
            temp_data_region = "uk"
            self.logger.info("data_region: " + temp_data_region)
            return temp_data_region
        elif self.args.data_region is None:
            temp_data_region = "all_regions"
            self.logger.info("data_region: " + temp_data_region)
            return temp_data_region

    def meth_return_folders(self):
        # get path to current ("setup_argparse.py") script
        path_setup_file = os.path.realpath(__file__)
        self.logger.debug("path setup_argparse.py: " + path_setup_file)
        # get path to folder of python script
        path_folder_modules = os.path.dirname(path_setup_file)
        self.logger.debug("path modules folder: " + path_folder_modules)
        # get path to modules sub-folder
        path_folder_working = os.path.dirname(path_folder_modules)
        self.logger.debug("path working directory: " + path_folder_working)
        return path_setup_file, path_folder_modules, path_folder_working

    def meth_setup_parent_save_folder(self):
        """
        :return: creates parent output/save directory "signal_results" if it does not already exist. If exists does not
        overwrite. Returns path as variable.
        """
        folder_name = "/signal_results"
        os.makedirs(self.path_folder_working + folder_name, exist_ok=True)
        path_folder_parent_save = self.path_folder_working + "/" + folder_name
        self.logger.debug("path parent save folder: " + path_folder_parent_save)
        return path_folder_parent_save

    def meth_setup_save_folder(self):
        """

        :return: creates output/save directory. Generates string from input argument signal identifiers (signal no,
        lineage, variant, mutations, data region) and date of analysis to use as folder name. Iterates version number in
        case of the need to rerun to prevent overwriting previous results.
        """
        if self.args.filename:
            ref_custom = "custom_input_"
        else:
            ref_custom = ""
        string_output_folder = (self.path_parent_save_dir + "/" + self.date.strftime("%Y%m%d") + "_" + self.signal_no +
                                "_" + self.data_region + "_" + ref_custom + self.lineage + "_"
                                + self.mutations_folder_name + "_v1")
        # iterate run numbers so script doesn't overwrite itself -> if folder exists _v+1 ending
        count = 1
        if os.path.exists(string_output_folder):
            # start while (adding "count" to string")
            while True:
                new_dir_name = string_output_folder.strip("v1") + "v" + f'{count}'
                if os.path.exists(new_dir_name):
                    count += 1
                else:
                    os.mkdir(new_dir_name)
                    break
        else:
            # set new_dir_name -> None so that it won't run into an error of needing existing folder to run
            new_dir_name = None
            os.mkdir(string_output_folder)

        # select used save path name
        if new_dir_name is not None:
            path_save = new_dir_name
        else:
            path_save = string_output_folder
        self.logger.info("save directory: " + path_save)
        return path_save

