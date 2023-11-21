import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from modules.output_graphs import ClassOutputGraphs


# %%


class ClassSignalStatistics(ClassOutputGraphs):
    def __init__(self, class_signal):
        super().__init__(class_signal)
        self.stat_date_min = self.date_min.strftime("%d.%m.%Y")
        self.stat_date_max = self.date_max.strftime("%d.%m.%Y")
        self.stat_signal_percent_total = self.meth_return_signal_percent_total()
        self.stat_signal_sequences = len(self.df_filtered_signal)
        self.stat_total_sequences = len(self.df_filtered)
        self.stat_highest_country = self.meth_return_stat_highest_country()
        self.stat_highest_region = self.meth_return_stat_highest_region()
        self.stat_highest_weekly_sequences = self.meth_return_stat_highest_week()
        self.stat_highest_week_percent_per_region = \
            self.meth_return_stat_highest_week_percent_per_region()
        self.stat_subregion_outliers = self.meth_return_stat_outlier_regions_total_no()
        self.stat_growth_text, self.stat_growth_text_per_region = self.meth_return_stat_significant_regions_growth()
        self.stat_no_signal_mutations = len(self.df_profile_gene_mutation)
        self.stat_no_unique_mutations, self.stat_unique_mutations = self.meth_return_stat_unique_mutations_to_top_10()
        self.stat_no_uncommon_mutations, self.stat_uncommon_mutations = \
            self.meth_return_stat_low_prevalence_mutations_to_top_10()
        self.log_text = self.meth_generate_log_update_text()
        self.table_update_summary = self.meth_return_historic_log_text()

        # epi review
    def meth_return_signal_percent_total(self):
        stat_signal_percent_total = self.df_lineage_perc_mod[self.df_lineage_perc_mod["index"].eq("SIGNAL")]
        stat_signal_percent_total = stat_signal_percent_total.iloc[0]["mod_lineage"].round(2)
        return stat_signal_percent_total

    def meth_return_stat_highest_country(self):
        temp_df = self.df_filtered_country_continent_val.copy()
        temp_df_country_counts_max = temp_df["location"].value_counts().reset_index()
        val_max_country = temp_df_country_counts_max["index"][0]
        self.logger.info(f"max reporting country: {val_max_country}")
        return val_max_country

    def meth_return_stat_highest_region(self):
        temp_df = self.df_filtered_country_continent_val.copy()
        temp_df_region_counts_max = temp_df["region_totals"].value_counts().reset_index()
        val_max_region_counts = temp_df_region_counts_max["index"][0]
        self.logger.info(f"highest reporting region: {val_max_region_counts}")
        return val_max_region_counts

    def meth_return_stat_highest_week(self):
        temp_df = self.df_filtered_country_continent_val.copy()
        temp_df_week_counts_max = temp_df["week_beginning"].value_counts().reset_index()
        val_df_week_max = (temp_df_week_counts_max["index"][0]).strftime("%d.%m.%Y")
        val_max_week_count = (val_df_week_max + ": " + temp_df_week_counts_max["week_beginning"][0].astype(str))
        self.logger.info(f"highest reporting week: {val_max_week_count}")
        return val_max_week_count

    def meth_return_stat_highest_week_percent_per_region(self):
        return 0

    def meth_return_stat_outlier_regions_total_no(self):
        temp_df = self.df_filtered_country_val.copy()
        if temp_df["country"].nunique() == 1:
            col_to_use = "region_totals"
        else:
            col_to_use = "location"

        temp_df_location = pd.DataFrame(temp_df[col_to_use].unique())
        temp_df_location = temp_df_location.assign(
            samples=temp_df_location[0].str.split(": ", expand=True)[1].astype(int))
        fig, axes = plt.subplots(1, 2, figsize=(15, 5), )
        fig.suptitle('Sample Location Distribution')
        sns.histplot(ax=axes[0], data=temp_df_location, x="samples", kde=True, kde_kws=dict(cut=3))
        sns.boxplot(ax=axes[1], data=temp_df_location, x="samples")
        fig.savefig(self.path_save_dir + "/outlier_distribution.png")
        val_q1 = temp_df_location["samples"].quantile(0.25)
        val_q3 = temp_df_location["samples"].quantile(0.75)
        val_iqr = val_q3 - val_q1
        upper_limit = val_q3 + 1.5 * val_iqr
        temp_df_outliers = temp_df_location[temp_df_location["samples"] > upper_limit]
        str_outliers = ", ".join(temp_df_outliers[0])
        self.logger.info(f"outlier regions found: {str_outliers}")
        return str_outliers

    def meth_return_stat_significant_regions_growth(self):
        temp_df = self.df_filtered_signal_proportion_overall.copy()
        choices = ["sustained growth", "plateauing", "sporadic growth", "decline", "early growth", "significant"
                   "accelerating growth", "declining growth"]
        # conditions
        # sustained growth = week on week increase ~ same increase
        # plateauing = recent growth less than 1% growth compared to week before
        # sporadic growth = increasing but not observed in all weeks or goes up and down but trending upwards
        # sporadic presence = intermittent prevalence with no trend
        # decline = decreasing
        # early growth = not seen in earlier weeks
        # significant = x2 per week
        # accelerating growth = rate increasing week on week
        # declining growth = rate decreasing week on week but not at point of plateau
        return 0, 0

    # mutation review
    def meth_return_stat_unique_mutations_to_closest_variant(self):
        df_signal = self.df_profile_gene_mutation.copy()
        return 0

    def meth_return_stat_unique_mutations_to_top_10(self):
        df_signal = self.df_profile_gene_mutation.copy()
        df_top_10 = self.df_profile_gene_mutation_top_10.copy()
        df_unique_mutations = df_signal[~df_signal["gene_mutation"].isin(df_top_10["gene_mutation"])]
        val_no_unique_mutations = len(df_unique_mutations)
        str_unique_mutations = ", ".join(df_unique_mutations["gene_mutation"])
        self.logger.info(f"unique mutations found: {val_no_unique_mutations}, {str_unique_mutations}")
        return val_no_unique_mutations, str_unique_mutations

    def meth_return_stat_low_prevalence_mutations_to_top_10(self):
        df_signal = self.df_profile_gene_mutation.copy()
        df_top_10 = self.df_profile_gene_mutation_top_10.copy()
        df_mutation_prevalence = df_top_10["gene_mutation"].value_counts().reset_index()
        val_lineages = len(self.list_df_top_10_lineage_alt) / 2
        # return all mutations prevalent in over 50% of the top 10 circulating lineages
        df_mutation_prevalence = df_mutation_prevalence[df_mutation_prevalence["gene_mutation"] >= val_lineages]
        # compare prevalent mutations with mutations in signal. If mutation exclusive to signal return.
        df_compare = df_signal[~df_signal["gene_mutation"].isin(df_mutation_prevalence["index"])]
        val_no_uncommon_mutations = len(df_compare)
        str_uncommon_mutations = ", ".join(df_compare["gene_mutation"])
        self.logger.info(f"uncommon mutations found: {val_no_uncommon_mutations}, {str_uncommon_mutations}")
        return val_no_uncommon_mutations, str_uncommon_mutations

    def meth_generate_log_update_text(self):
        if self.stat_subregion_outliers:
            text_outlier = f"Significant contributors were identified as; {self.stat_subregion_outliers}"
        else:
            if self.data_region == "eng":
                choice = self.stat_highest_region
            else:
                choice = self.stat_highest_country
            text_outlier = f"Top contributor identified was {choice}"

        text_unique = f"{self.stat_no_unique_mutations} unique mutations ({self.stat_unique_mutations})"
        text_uncommon = f"{self.stat_no_uncommon_mutations} uncommon mutations ({self.stat_uncommon_mutations})"

        text_growth = f"and shows signs of {self.stat_growth_text}."
        text_growth_regions = f"Signal shows signs of {self.stat_growth_text_per_region}."

        text = (f"Signal accounts for {self.stat_signal_percent_total}% ({self.stat_signal_sequences}/"
                f"{self.stat_total_sequences} sequences) within the time period {self.stat_date_min}-"
                f"{self.stat_date_max}. {text_outlier}. Compared with the top 10 circulating lineages, signal was "
                f"found to contain {text_unique} and {text_uncommon}. Signal consists of {len(self.df_lineage_subs)-1} "
                f"sub-lineages.")

        print(text)
        return text

    def meth_return_historic_log_text(self):
        if self.data_region == "eng":
            review_assessment = "review_assessment_eng"
        elif self.data_region == "int":
            review_assessment = "review_assessment_int"
        row = [self.signal_no, self.date, self.log_text]
        if self.df_logs is not None:
            df_log = self.df_logs.copy()
            df_log_signal = df_log[df_log["signal_id"].eq(self.signal_no)]
            df_log_signal = df_log_signal[['signal_id', "review_date", review_assessment]]
            df_log_signal.loc[len(df_log_signal)] = row
            df_log_signal["review_date"] = pd.to_datetime(df_log_signal["review_date"]).dt.strftime('%d.%m.%Y')
            df_log_signal.to_csv(self.path_save_dir + "/signal_history.csv", index=False)
            return df_log_signal
        else:
            df_log_signal = pd.DataFrame(columns=['signal_id', 'review_date', review_assessment])
            df_log_signal.loc[len(df_log_signal)] = row
            df_log_signal["review_date"] = pd.to_datetime(df_log_signal["review_date"]).dt.strftime('%d.%m.%Y')
            df_log_signal.to_csv(self.path_save_dir + "/signal_history.csv", index=False)
            return df_log_signal

