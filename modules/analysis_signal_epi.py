import datetime
import pandas as pd

from modules.analysis_filter_signal import ClassSignalSelect

# %%

class ClassSignalAnalysisEPI(ClassSignalSelect):
    def __init__(self, class_signal):
        super().__init__(class_signal)
        self.start_date_period = self.meth_generate_date_period()
        self.stat_no_samples, self.stat_no_samples_per_region, self.stat_no_samples_per_subregion = \
            self.meth_generate_sample_counts()
        self.ids = self.meth_return_ids()
        self.val_signal_prop = self.meth_calculate_signal_proportion()
        self.df_filtered_signal = self.meth_calculate_region_totals()
        self.df_filtered_country_val = self.meth_format_country_vals()
        self.df_filtered_country_continent_val = self.meth_format_country_regions()
        self.df_lineage_perc, self.df_lineage_perc_mod, self.df_lineage_perc_mod_top = \
            self.meth_calc_lineage_percentages()
        self.df_filtered_signal_proportion_region = self.meth_calculate_region_proportions()
        self.df_filtered_signal_proportion_overall = self.meth_calculate_overall_proportions()

    def meth_generate_date_period(self):
        date_min = self.df_unfiltered_signal["date"].min()
        date_max = self.df_unfiltered_signal["date"].max()
        date_period = date_min, date_max
        return date_period

    def meth_generate_sample_counts(self):
        no_samples = len(self.df_filtered_signal)
        no_samples_per_region = self.df_filtered_signal["region"].value_counts()
        no_samples_per_subregion = self.df_filtered_signal["region_code"].value_counts()
        return no_samples, no_samples_per_region, no_samples_per_subregion

    def meth_return_ids(self):
        ids_unfiltered = self.df_unfiltered_signal["id"]
        self.logger.info(f"saving unfiltered SIGNAL ids to dir: {self.path_save_dir}")
        ids_unfiltered.to_csv(self.path_save_dir + "/" + datetime.datetime.now().strftime('%Y%m%d') + "_"
                              + self.signal_no + "_" + self.lineage + "_unfiltered_signal_ids.csv",
                              encoding="utf-8", index=False)
        ids_filtered = self.df_filtered_signal["id"]
        self.logger.info(f"saving filtered SIGNAL ids to dir: {self.path_save_dir}")
        ids_filtered.to_csv(self.path_save_dir + "/" + datetime.datetime.now().strftime('%Y%m%d') + "_"
                            + self.signal_no + "_" + self.lineage + "_filtered_signal_ids.csv",
                            encoding="utf-8", index=False)

        return ids_unfiltered, ids_filtered

    def meth_calculate_signal_proportion(self):
        self.logger.info("calculating SIGNAL total proportion (within period)")
        val_signal_prop = (len(self.df_filtered_signal) / len(self.df_filtered)) * 100
        val_signal_prop = round(val_signal_prop, 2)

        return val_signal_prop

    def meth_calculate_region_totals(self):
        self.logger.info("creating merged region & respective total occurrence column")
        temp_df = self.df_filtered_signal.copy()
        # temp_df[['region', 'region_code']] = temp_df[['region', 'region_code']].astype(str).apply(lambda x: x.str.strip()).replace('', np.nan)
        temp_df["region_totals"] = temp_df.groupby(["region"])["id"].transform(len)
        temp_df["region_totals"] = temp_df["region"].astype(str) + ": " + temp_df["region_totals"].astype(str)

        return temp_df

    def meth_format_country_regions(self):
        self.logger.info("creating list of region (continents/uk regions) reporting")
        list_region = list(self.df_filtered_signal.region.unique())
        list_continent_dfs = []

        # for each region format to only display top 5 countries, group all other as "continent_name_other"
        for region in range(len(list_region)):
            temp_df = self.df_filtered_signal[self.df_filtered_signal["region_totals"].str.contains(
                "%s" % list_region[region])].copy()
            temp_filter_top_5 = temp_df["country"].value_counts().head(5).copy()
            temp_filter_top_5_2 = temp_filter_top_5.reset_index().copy()
            temp_filter_top_5_2 = temp_filter_top_5_2.mask(temp_filter_top_5_2["country"] == False).copy()
            temp_df.loc[:, "country_check"] = temp_df.loc[:, "country"].isin(temp_filter_top_5_2.loc[:, "index"]).copy()
            temp_df.loc[:, "country"] = temp_df.loc[:, "country"].mask(temp_df.loc[:, "country_check"] == False, "%s" %
                                                                       list_region[region] + "_other").copy()
            list_continent_dfs.append(temp_df)

        df_filtered_continents = pd.concat(list_continent_dfs).copy()

        # create column with country and total count (": " seperated)
        df_country_count = pd.DataFrame(
            df_filtered_continents["country"].value_counts()).reset_index().rename(columns={"index": "country",
                                                                                            "country": "samples"})
        df_country_count["location"] = (df_country_count["country"].astype(str) + ": "
                                        + df_country_count["samples"].astype(str))

        # merge with filtered (top countries/region)
        df_filtered_country_continent_val = df_filtered_continents.merge(df_country_count, on="country")
        self.logger.debug(f"df_filtered_country_val top 5 rows = {df_filtered_country_continent_val.head(5)}")

        return df_filtered_country_continent_val

    def meth_format_country_vals(self):
        self.logger.info("creating list of region (continents/uk regions) reporting")
        temp_df = self.df_filtered_signal.copy()

        # create column with country and total count (": " seperated)
        temp_df1 = pd.DataFrame(temp_df["country"].value_counts()).reset_index().rename(columns={"index": "country",
                                                                                                 "country": "samples"})
        temp_df1["location"] = (temp_df1["country"].astype(str) + ": " + temp_df1["samples"].astype(str))
        # merge with filtered (top countries/region)
        df_filtered_country_val = temp_df.merge(temp_df1, on="country")

        return df_filtered_country_val

    def meth_calc_lineage_percentages(self):
        temp_df_filtered = self.df_filtered.copy()
        temp_df_filtered_signal = self.df_filtered_signal.copy()
        self.logger.info("calculating lineage percentages")

        # overall percentage lineages
        df_lineage_perc = temp_df_filtered['usher_lineage'].value_counts(normalize=True) * 100

        # modified percentage lineages -> include signal (overwrites assignment matching seqs. - only counted once)
        # use id presence as lineage presence won't work if using mutations.
        temp_df_filtered["id_cross_ref"] = temp_df_filtered["id"].isin(
            temp_df_filtered_signal["id"])
        log_check_ids = len(temp_df_filtered["id_cross_ref"].value_counts())
        self.logger.debug(f"filtered lineage check: {log_check_ids} = {len(temp_df_filtered_signal)}")
        temp_df_filtered["mod_lineage"] = temp_df_filtered["usher_lineage"].mask(
            temp_df_filtered["id_cross_ref"] == True, "SIGNAL")
        # create dataframe
        df_lineage_perc_mod = temp_df_filtered['mod_lineage'].value_counts(normalize=True) * 100
        self.logger.debug(f"lineage percentage modification: {df_lineage_perc_mod.head(5)}")
        df_lineage_perc_mod = df_lineage_perc_mod.reset_index()
        # create top 10 lineages dataframe
        df_lineage_perc_mod_top = df_lineage_perc_mod.head(10)
        df_lineage_perc_mod_top = df_lineage_perc_mod_top.reset_index()
        self.logger.debug(f"top 10 lineage percentage dataframe: {df_lineage_perc_mod_top}")

        return df_lineage_perc, df_lineage_perc_mod, df_lineage_perc_mod_top

    def meth_calculate_region_proportions(self):
        temp_df_filtered_signal = self.df_filtered_signal.copy()
        temp_df_filtered = self.df_filtered.copy()

        list_regions = list(temp_df_filtered_signal.region.unique())
        list_df_proportion = []

        for region in range(len(list_regions)):
            temp_df = temp_df_filtered[temp_df_filtered["region"].eq("%s" % list_regions[region])]
            df_count_region_total = temp_df.groupby(temp_df.date.dt.date)["region"].count().reset_index()
            temp_df_total = temp_df_filtered_signal[temp_df_filtered_signal["region"].eq("%s" % list_regions[region])]
            df_count_region = temp_df_total.groupby(temp_df_total.date.dt.date)["region"].count().reset_index()
            df_count_region_total = df_count_region_total.merge(df_count_region,
                                                                on="date",
                                                                how="outer")
            df_count_region_total['date_epi'] = pd.to_datetime(
                df_count_region_total['date']) - pd.to_timedelta(7, unit='d')
            df_count_region_total["region"] = "%s" % list_regions[region]
            test = df_count_region_total.groupby(
                ['region', pd.Grouper(key='date_epi', freq='W-SUN')]).sum().reset_index().sort_values('date_epi')
            test["proportion"] = (test["region_y"] / test["region_x"]).round(1)
            test["proportion"] = test["proportion"].fillna(0)

            list_df_proportion.append(test)
        df_proportion = pd.concat(list_df_proportion).copy()

        # merge to get Country/Count column
        df_proportion = df_proportion.merge(temp_df_filtered_signal,
                                            on="region",
                                            how="outer")

        # replicate column if original df is international -> use of calling column header for identification
        if "region_code" in temp_df_filtered_signal.columns:
            df_proportion["identifier"] = df_proportion["region"]
        return df_proportion

    def meth_calculate_overall_proportions(self):

        # temp. df of all uk data -> date, cog_uk_id
        temp_df_uk_all = pd.DataFrame(self.df_filtered, columns=["date", "id"])

        # Bad repetition -> groups dataframes by dates/samples
        temp_df_uk_all = temp_df_uk_all.groupby("date")["id"].count().cumsum().reset_index()
        temp_df_uk_all = temp_df_uk_all.set_index("date").resample("D").first().fillna(method="ffill").reset_index()
        temp_df_uk_all = temp_df_uk_all.rename(columns={"id": "all_samples"})

        temp_df_uk = self.df_filtered_signal.groupby("date")["id"].count().cumsum().reset_index()
        temp_df_uk = temp_df_uk.set_index("date").resample("W").first().fillna(method="ffill").reset_index()
        temp_df_uk = temp_df_uk.rename(columns={"id": "signal_samples"})

        # merge temp dfs
        df_proportion = temp_df_uk.merge(temp_df_uk_all, on="date")

        df_proportion["percentage_total"] = (df_proportion["signal_samples"] / df_proportion["all_samples"]) * 100

        return df_proportion
