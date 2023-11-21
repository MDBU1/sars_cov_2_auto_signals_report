import logging
import os
from datetime import datetime
from pathlib import Path

# %%


class ClassSetupCommands:
    def __init__(self, input_signal_no, input_region, input_lineage, input_mutations, input_nucleotides, input_logs,
                 input_logging_level, input_location, input_filename, input_date_begin, input_path_input):
        self.date = datetime.now()
        self.df_logs = input_logs
        self.logging_level = input_logging_level
        self.location = input_location
        self.filename = input_filename
        self.date_begin = input_date_begin
        self.path_input = input_path_input
        self.logfile, self.signal_no = self.meth_return_logfile_name_str(input_signal_no)
        self.val_logging_level = self.meth_return_logging_value()
        self.logger = self.meth_setup_logger()
        self.logger.info(f"initialising log file of signal: {str(self.signal_no)}")
        self.logger.info(f"logging level: {str(self.logging_level)}")
        self.lineage = self.meth_return_input_conditions_lineage_str(input_lineage)
        self.mutations, self.mutations_folder_name = self.meth_return_input_conditions_mutations_str(input_mutations)
        self.nucleotides = self.meth_return_input_conditions_amino_acids_str(input_nucleotides)
        self.data_region = self.meth_return_input_conditions_data_region_str(input_region)
        self.path_setup_file, self.path_folder_modules, self.path_folder_working = self.meth_return_folders()
        self.path_parent_save_dir = self.meth_setup_parent_save_folder()
        self.path_save_dir = self.meth_setup_save_folder()
        Path(self.logfile).rename(self.path_save_dir + "/" + self.logfile)

    def meth_return_routine_signal_parameters(self, input_signal_no):
        if input_signal_no is None:
            args_signal_no = "none"
            return args_signal_no
        else:
            args_signal_no = input_signal_no
            return args_signal_no

    def meth_return_logfile_name_str(self, input_signal_no):
        signal_no = self.meth_return_routine_signal_parameters(input_signal_no)
        logfile = "LOGFILE_" + self.date.strftime("%Y%m%d") + "_" + signal_no + "_" + self.logging_level + ".log"
        return logfile, signal_no

    def meth_return_logging_value(self):
        """
        Return logging value from string selection input.
        :return:
        """
        if self.logging_level == "INFO":
            level = logging.INFO
        elif self.logging_level == "DEBUG":
            level = logging.DEBUG
        elif self.logging_level == "WARNING":
            level = logging.WARNING
        elif self.logging_level == "ERROR":
            level = logging.ERROR
        elif self.logging_level == "CRITICAL":
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
        # disable silly matplotlib and imagetk errors
        logging.getLogger('matplotlib.font_manager').disabled = True
        logging.getLogger("PIL").propagate = False
        logging.getLogger("")
        return logger

    def meth_return_input_conditions_lineage_str(self, input_lineage):
        if input_lineage is not None:
            temp_lineage = input_lineage
        # elif self.args.variant is not None:
        #    temp_lineage = self.args.variant
        else:
            temp_lineage = "no_specified_lineage"
        self.logger.info("lineage: " + temp_lineage)
        return temp_lineage

    def meth_return_input_conditions_mutations_str(self, input_mutations):
        temp_mutations = "_".join(input_mutations)
        temp_mutations = temp_mutations.replace(":", ".")
        temp_mutations_folder_name = input_mutations
        if not temp_mutations:
            temp_mutations = "no_specified_mutations"
            # set up folder conditions
            temp_mutations_folder_name = "no_specified_mutations"
        elif len(temp_mutations_folder_name) <= 3:
            temp_mutations_folder_name = temp_mutations
        elif len(temp_mutations_folder_name) > 3:
            temp_mutations_folder_name = "various_specified_mutations"
        elif "any" in temp_mutations_folder_name:
            temp_mutations_folder_name = "any_of_specified_mutations"
        self.logger.info("mutations: " + temp_mutations)
        return temp_mutations, temp_mutations_folder_name

    def meth_return_input_conditions_amino_acids_str(self, input_nucleotides):
        temp_nucl = "_".join(input_nucleotides)
        temp_nucl_folder_name = input_nucleotides
        if not temp_nucl:
            temp_nucl = "no_specified_aa"
        self.logger.info("amino acids: " + temp_nucl)
        return temp_nucl

    def meth_return_input_conditions_data_region_str(self, input_region):
        """
        Select location of analysis UK vs INT
        """
        if input_region == "int":
            temp_data_region = "int"
            self.logger.info("data_region: " + temp_data_region)
            return temp_data_region
        elif input_region == "uk":
            temp_data_region = "uk"
            self.logger.info("data_region: " + temp_data_region)
            return temp_data_region
        elif input_region is None:  # redundant?
            temp_data_region = "all_regions"
            self.logger.info("data_region: " + temp_data_region)
            return temp_data_region

    def meth_return_folders_local(self):
        # get path to current ("setup_argparse_commands_routine.py") script
        path_setup_file = os.path.realpath(__file__)
        self.logger.debug("path setup_argparse_commands_routine.py: " + path_setup_file)
        # get path to folder of python script
        path_folder_modules = os.path.dirname(path_setup_file)
        self.logger.debug("path modules folder: " + path_folder_modules)
        # get path to modules sub-folder
        path_folder_working = os.path.dirname(path_folder_modules)
        self.logger.debug("path working directory: " + path_folder_working)
        return path_setup_file, path_folder_modules, path_folder_working

    def meth_return_folders_online(self):
        # set path to storage explorer location
        path_setup_file = ""
        self.logger.debug(f"path storage explorer, signals: {path_setup_file}")
        # get path of modules folder
        path_folder_modules = path_setup_file + ""
        self.logger.debug(f"path storage explorer, signals modules: {path_folder_modules}")
        # get path to modules sub-folder
        path_folder_working = os.path.dirname(path_folder_modules)
        return path_setup_file, path_folder_modules, path_folder_working

    def meth_return_folders(self):
        if self.location is True:
            path_setup_file, path_folder_modules, path_folder_working = self.meth_return_folders_online()
            return path_setup_file, path_folder_modules, path_folder_working
        elif self.location is False:
            path_setup_file, path_folder_modules, path_folder_working = self.meth_return_folders_local()
            return path_setup_file, path_folder_modules, path_folder_working
        else:
            print("ERROR")

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
        if self.filename:
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


