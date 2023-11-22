import os
from pathlib import Path

from modules.class_signal_specify import ClassSignalSpecify


# %%

class ClassSetupFolders(ClassSignalSpecify):
    def __init__(self, class_signal):
        super().__init__(class_signal.signal_no, class_signal.data_region, class_signal.lineage, class_signal.mutations,
                         class_signal.nucleotides, class_signal.df_logs, class_signal.logging_level,
                         class_signal.location, class_signal.filename, class_signal.date_begin, class_signal.path_input)
        self.lineage = self.meth_return_input_conditions_lineage_str(class_signal.lineage)
        self.mutations_a, self.mutations_folder_name = self.meth_return_input_conditions_mutations_str(
            class_signal.mutations)
        self.nucleotides = self.meth_return_input_conditions_amino_acids_str(class_signal.nucleotides)
        self.data_region = self.meth_return_input_conditions_data_region_str(class_signal.data_region)
        self.path_setup_file, self.path_folder_modules, self.path_folder_working = self.meth_return_folders()
        self.path_parent_save_dir = self.meth_setup_parent_save_folder()
        self.path_save_dir = self.meth_setup_save_folder()
        Path(self.logfile).rename(self.path_save_dir + "/" + self.logfile)

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
        elif input_region == "eng":
            temp_data_region = "eng"
            self.logger.info("data_region: " + temp_data_region)
            return temp_data_region
        elif input_region is None:  # redundant?
            temp_data_region = "all_regions"
            self.logger.info("data_region: " + temp_data_region)
            return temp_data_region

    def meth_return_folders_local(self):
        # get path to current ("setup_folders.py") script
        path_setup_file = os.path.realpath(__file__)
        self.logger.debug("path setup_folders.py: " + path_setup_file)
        # get path to folder of python script
        path_folder_modules = os.path.dirname(path_setup_file)
        self.logger.debug("path modules folder: " + path_folder_modules)
        # get path to modules sub-folder
        path_folder_working = os.path.dirname(path_folder_modules)
        self.logger.debug("path working directory: " + path_folder_working)
        return path_setup_file, path_folder_modules, path_folder_working

    def meth_return_folders_online(self):
        # set path to storage explorer location
        path_setup_file = self.path_input
        self.logger.debug(f"path storage explorer, signals: {path_setup_file}")
        # get path of modules folder
        path_folder_modules = os.path.dirname(path_setup_file)
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
