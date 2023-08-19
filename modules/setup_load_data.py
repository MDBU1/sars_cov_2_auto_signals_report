import functools
import glob
import os
import pandas as pd
from pptx import Presentation

from modules.setup_input_data import ClassSetupFileConditions


#%%


class ClassLoadData(ClassSetupFileConditions):
    def __init__(self):
        super().__init__()
        self.path_input = self.meth_return_return_path_input_data()
        self.path_df = self.meth_select_df()
        self.df_unfiltered, self.df_filtered = self.meth_load_df()
        print(f"length unfiltered vs filtered: {len(self.df_unfiltered)}, {len(self.df_filtered)}")
        self.prs_slide_title, self.prs_slide_main, self.therapeutics_table, self.uk_geojson = self.meth_load_modules()

    def meth_return_return_path_input_data(self):
        if self.args.location is True and self.args.filename is None:  # online
            path_input_data = ""  # default online location
            self.logger.debug("data being loaded from: " + path_input_data)
            return path_input_data
        elif self.args.location is True and self.args.filename:  # local
            path_input_data = self.args.filename
            self.logger.debug("data being loaded from: " + path_input_data)
            return path_input_data
        elif self.args.location is False and self.args.filename is None:
            path_input_data = self.args.path_data
            self.logger.debug("data being loaded from: " + path_input_data)
            return path_input_data
        elif self.args.location is False and self.args.filename:
            path_input_data = self.args.filename
            self.logger.debug("data being loaded from: " + path_input_data)
            return path_input_data
        else:
            self.logger.critical("!!!data load method not found!!!")
            return 0

    def meth_return_path_input_files(self):
        list_dfs = self.meth_return_input_filenames()
        list_path_dfs = []
        for df in list_dfs:
            path_df = self.path_input + "/" + df
            list_path_dfs.append(path_df)
        return list_path_dfs

    def meth_load_csv(self, input_df_string):
        # open input datafile (csv) only using pre-specified (useful) columns
        list_input_csv = glob.glob(self.path_input + "/*.csv")
        input_csv = list(filter(lambda files: input_df_string in files, list_input_csv))[-1]
        self.logger.info("loading csv: " + input_df_string)
        temp_df = pd.read_csv(input_csv, usecols=lambda x: x in self.list_input_columns, dtype='unicode')
        return temp_df

    def meth_select_df(self):
        list_dfs = self.meth_return_input_filenames()
        if not self.args.filename:
            if self.args.data_region == "uk":
                path_df = list_dfs[0]
                return path_df
            elif self.args.data_region == "int":
                path_df = list_dfs[1]
                return path_df
            elif self.args.data_region is None:
                self.logger.critical("!!!data region method not found!!!")
        elif self.args.filename:
            return self.args.filename
        return 0

    def meth_load_df(self):
        if not self.args.filename:
            temp_df = self.meth_load_csv(self.path_df)
            temp_df = self.meth_process_filter_dates(temp_df)
            temp_df_filter_country = self.meth_process_filter_country(temp_df)
            return temp_df, temp_df_filter_country
        elif self.args.filename:
            temp_df = self.meth_load_csv(self.path_df)
            temp_df = self.meth_process_filter_dates(temp_df)
            temp_df_filter_country = self.meth_process_filter_country(temp_df)
            return temp_df, temp_df_filter_country
        return 0

    def meth_load_modules(self):
        self.logger.info("loading modules from path: ", self.path_folder_modules)
        temp_path = self.path_folder_modules

        file_strings = ["template_1_title.pptx", "template_2_main.pptx",
                        "20220214_therapeutic_weighted_contact_sites_long_format.csv"]

        search_csv = glob.glob(self.path_folder_modules + "/*.csv")
        search_pptx = glob.glob(self.path_folder_modules + "/*.pptx")
        search_geojson = glob.glob(self.path_folder_modules + "/*.geojson")
        #file_paths = []
        #for file in range(len(file_strings)):
        #    file_path = temp_path + "/" + file_strings[file]
        #    file_paths.append(file_path)
        slide_title = search_pptx[0]
        #print("hi")
        #print(slide_title)
        slide_standard = search_pptx[1]

        ref_therapeutics_weighting = pd.read_csv(search_csv[0])
        ref_therapeutics_weighting["treatment"] = ref_therapeutics_weighting["treatment"].replace(["S309"],
                                                                                                  "sotrovimab")
        uk_geojson = search_geojson[0]

        return slide_title, slide_standard, ref_therapeutics_weighting, uk_geojson
