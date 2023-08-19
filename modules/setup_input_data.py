import os
import sys
import logging
import datetime
from itertools import chain

import pandas as pd

from modules.setup_argparse import ClassSetupArgparse


#%%


class ClassSetupFileConditions(ClassSetupArgparse):
    def __init__(self):
        super().__init__()
        self.list_input_columns = self.meth_return_input_columns()
        self.date_min, self.date_max = self.meth_return_date_parameters()

    def meth_return_input_columns(self):
        """

        :return: creates list of all useful columns from all datasets to be inputted
        """
        list_cols = ["id", "date", "country", "region",  "region_code", "usher_lineage", "mutations"]

        self.logger.debug("calling input .csv columns :" f'{list_cols}')
        return list_cols

    def meth_return_custom_filename(self):
        if self.args.filename:
            temp_str_name = os.path.basename(self.args.filename)
            temp_str_name = ''.join([i for i in temp_str_name if not i.isdigit()])
            temp_str_name = [temp_str_name.replace(".csv", "", regex=False)]
            self.logger.debug("custom input filename: " + f'{temp_str_name}')
            return temp_str_name

    def meth_return_input_filenames(self):
        list_str_input_filenames = ["uk_last_100_days", "int_last_100_days"]
        self.logger.debug("input filenames: " f'{list_str_input_filenames}')
        return list_str_input_filenames

    def meth_return_date_parameters(self):

        # return date from last Sunday
        val_date_last_sunday = test = (pd.to_datetime('now') - pd.Timedelta(days=((pd.to_datetime('now').dayofweek - 6)
                                                                                  % 7))).date()
        # return date from 1 week ago
        # val_date_latest = pd.to_datetime(self.date) - pd.to_timedelta(7, unit='d')
        # return date from 1 week ago since last Sunday
        val_date_latest = pd.to_datetime(val_date_last_sunday) - pd.to_timedelta(7, unit="d")
        # return date from 7 weeks ago
        # val_date_earliest = pd.to_datetime(self.date) - pd.to_timedelta(49, unit='d')
        # return date from 7 weeks ago since last Sunday
        val_date_earliest = pd.to_datetime(val_date_last_sunday) - pd.to_timedelta(49, unit="d")
        self.logger.info(f"analysis date period: + {val_date_earliest}, - {val_date_latest}")
        return val_date_earliest, val_date_latest,

    def meth_remove_uk_entries(self, df):
        # removal of UK entries from international dataset
        self.logger.info("removing uk entries")
        temp_df_minus_uk = df[~df["country"].str.contains("United Kingdom", na=False, case=False)]
        return temp_df_minus_uk

    def meth_remove_non_england_entries(self, df):
        self.logger.info("removing non-england entries")
        temp_df_spec_eng = df[~df["country"].isna()]
        # print(temp_df_spec_eng.country.value_counts())
        temp_df_spec_eng = temp_df_spec_eng[temp_df_spec_eng["country"].eq("UK-ENG")]
        val_diff_eng_vs_uk = len(df) - len(temp_df_spec_eng)
        check = temp_df_spec_eng["country"].value_counts()
        self.logger.debug("check for non England UK entries: " f'{check}')
        self.logger.info(f"removed {val_diff_eng_vs_uk} non-england listed samples")
        return temp_df_spec_eng

    def meth_format_date_entries(self, df):
        temp_df_date = df.copy()
        # format date to usable format
        self.logger.info("formatting date column/s")
        temp_df_date["date"] = temp_df_date["date"].astype(str).str.replace("-", "")
        temp_df_date["date_check"] = temp_df_date["date"].astype(str).str.len()
        temp_df_date = temp_df_date[temp_df_date["date_check"] == 8]
        temp_df_date["date"] = pd.to_datetime(temp_df_date["date"], format="%Y%m%d")
        return temp_df_date

    def meth_select_date_period(self, df, start_date, end_date):
        """function that returns entries between one week and 12 weeks of date script run"""
        temp_df = df.copy()
        self.logger.info("filtering date -> last 6 weeks")
        # select data from beginning of 7 weeks ago
        val_start_date = start_date
        val_start_date = pd.to_datetime(val_start_date, format="%Y%m%d")
        # select data from beginning of 1 week ago -> 8-week period
        val_end_date = end_date
        val_end_date = pd.to_datetime(val_end_date, format="%Y%m%d")
        self.logger.debug(f"date period {val_start_date} -> {val_end_date}")
        # crop data to period between start and end date
        temp_df_date_period = temp_df[(temp_df['date'] > val_start_date) & (temp_df['date'] <= val_end_date)]
        return temp_df_date_period

    def meth_add_week_date_column(self, df):
        temp_df = df.copy()
        # use max as will just return row entry as want whole df
        temp_df['week_beginning'] = pd.to_datetime(temp_df['date']) - pd.to_timedelta(7, unit='d')
        df_week_grouped = temp_df.groupby(["id", pd.Grouper(key='week_beginning', freq='W-SUN')]
                                          ).max().reset_index().sort_values('week_beginning')
        return df_week_grouped

    def meth_process_filter_dates(self, df):
        temp_df = df.copy()
        temp_df = temp_df[~temp_df["date"].isna()]
        temp_df = self.meth_format_date_entries(temp_df)
        temp_df = self.meth_select_date_period(temp_df, self.date_min, self.date_max)
        temp_df = self.meth_add_week_date_column(temp_df)
        return temp_df

    def meth_process_filter_country(self, df):
        temp_df = df.copy()
        if self.args.data_region == "int":
            temp_df_region_filter = self.meth_remove_uk_entries(temp_df)
            return temp_df_region_filter
        elif self.args.data_region == "uk":
            temp_df_region_filter = self.meth_remove_non_england_entries(temp_df)
            return temp_df_region_filter
        elif self.args.data_region is None:
            self.logger.critical("!!!data region method not found!!!")
            return 0


