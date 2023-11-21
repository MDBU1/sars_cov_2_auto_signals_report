import glob
import json

import numpy as np
import pandas as pd
import requests

from modules.setup_input_data import ClassSetupFileConditions


# %%


class ClassLoadData(ClassSetupFileConditions):
    def __init__(self, class_signal):
        super().__init__(class_signal)
        # self.path_input = self.meth_return_return_path_input_data()
        self.path_df = self.meth_select_df()
        self.df_unfiltered, self.df_filtered, self.df_lineages_unaliased, self.df_lineages_alias_list = \
            self.meth_load_df()
        self.logger.info(f"length unfiltered vs filtered dataframe: {len(self.df_unfiltered)}, {len(self.df_filtered)}")
        self.prs_slide_title, self.prs_slide_main, self.therapeutics_table, self.uk_geojson = self.meth_load_modules()

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
        list_input_csv = sorted(list_input_csv)
        input_csv = list(filter(lambda files: input_df_string in files, list_input_csv))[-1]
        self.logger.info("finding latest csv: " + input_df_string)
        self.logger.info(f"loading csv: {input_csv}")
        temp_df = pd.read_csv(input_csv, usecols=lambda x: x in self.list_input_columns, dtype='unicode')
        return temp_df

    def meth_select_df(self):
        list_dfs = self.meth_return_input_filenames()
        if not self.filename:
            if self.data_region == "eng":
                path_df = list_dfs[0]
                return path_df
            elif self.data_region == "int":
                path_df = list_dfs[1]
                return path_df
            elif self.data_region is None:
                self.logger.critical("!!!data region method not found!!!")
        elif self.filename:
            temp_str_name = self.meth_return_custom_filename()  # just for logs
            return self.filename
        return 0

    def meth_fill_nan_regions(self, input_df):
        self.logger.debug(f"filling empty cells in region and region_code columns with nan")
        temp_df = input_df.copy()
        temp_df[['region', 'region_code']] = temp_df[['region', 'region_code']].astype(str).apply(
            lambda x: x.str.strip()).replace('', np.nan)
        return temp_df

    def meth_add_region_totals(self, input_df):
        self.logger.debug("adding region_totals column")
        temp_df = input_df
        temp_df["region_totals"] = temp_df.groupby(["region"])["id"].transform(len)
        temp_df["region_totals"] = (temp_df["region"].astype(str) + ": " + temp_df["region_totals"].astype(str))
        return temp_df

    def meth_return_unaliased_lineages(self, input_df):
        self.logger.debug("adding unaliased lineages")
        temp_df = input_df.copy()
        url = 'https://raw.githubusercontent.com/cov-lineages/pangolin-data/main/pangolin_data/data/alias_key.json'
        rep = requests.get(url)
        data = json.loads(rep.text)
        df_lineages = pd.DataFrame(temp_df["usher_lineage"])

        df_lineages[["alias", "number"]] = temp_df["usher_lineage"].str.split(".", n=1, expand=True)
        df_lineages = df_lineages.fillna('')
        df_lineages = df_lineages.drop_duplicates()
        df1 = pd.DataFrame.from_dict(data, orient="index", columns=["parent"]).rename_axis("alias").reset_index()

        for x, i in enumerate(df1['parent']):
            if type(i) is list:
                i = ', '.join(i)
                df1['parent'][x] = i
            elif i == "":
                i = df1["alias"][x]
                df1["parent"][x] = i

        df_lineages_alias_list = df1.copy()
        df_lineages = df1.merge(df_lineages, on="alias")
        dfl1 = df_lineages.assign(unaliased_lineage=df_lineages["parent"].astype(str) + "." + df_lineages["number"])
        row_unassigned = pd.DataFrame(
            {"alias": "Unassigned", "parent": "Unassigned", "usher_lineage": "Unassigned", "number": "",
             "unaliased_lineage": "Unassigned"}, index=[0])
        df_lineages_unaliased = pd.concat([row_unassigned, dfl1.loc[:]]).reset_index(drop=True)
        df_unaliased_metadata = pd.merge(temp_df, dfl1, on="usher_lineage")
        self.logger.debug(f"added unaliased lineages:\n{df_lineages_unaliased}")

        return df_unaliased_metadata, df_lineages_unaliased, df_lineages_alias_list

    def meth_load_df(self):
        temp_df = self.meth_load_csv(self.path_df)
        temp_df = self.meth_fill_nan_regions(temp_df)
        temp_df = self.meth_process_filter_dates(temp_df)
        temp_df, df_lineages_unaliased, df_lineages_alias_list = self.meth_return_unaliased_lineages(temp_df)
        temp_df = self.meth_add_region_totals(temp_df)
        temp_df_filter_country = self.meth_process_filter_country(temp_df)
        return temp_df, temp_df_filter_country, df_lineages_unaliased, df_lineages_alias_list

    def meth_load_modules(self):
        self.logger.info(f"loading modules from path: {self.path_folder_modules}")
        temp_path = self.path_folder_modules

        file_strings = ["template_1_title.pptx", "template_2_main.pptx",
                        "20220214_therapeutic_weighted_contact_sites_long_format.csv"]

        search_csv = glob.glob(self.path_folder_modules + "/*.csv")
        search_pptx = glob.glob(self.path_folder_modules + "/*.pptx")
        search_geojson = glob.glob(self.path_folder_modules + "/*.geojson")
        slide_title = search_pptx[0]

        slide_standard = search_pptx[1]

        ref_therapeutics_weighting = pd.read_csv(search_csv[0])
        ref_therapeutics_weighting["treatment"] = ref_therapeutics_weighting["treatment"].replace(["S309"],
                                                                                                  "sotrovimab")
        uk_geojson = search_geojson[0]

        return slide_title, slide_standard, ref_therapeutics_weighting, uk_geojson
