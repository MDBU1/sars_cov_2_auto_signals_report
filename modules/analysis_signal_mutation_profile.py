import datetime
import pandas as pd

from modules.analysis_signal_epi import ClassSignalAnalysisEPI

#%%


class ClassSignalAnalysisMutationProfile(ClassSignalAnalysisEPI):
    def __init__(self, class_signal):
        super().__init__(class_signal)
        self.list_top_10_lineage, self.list_top_10_lineages_alt = self.meth_return_top_10_lineages()
        self.list_df_top_10_lineage_alt = self.meth_return_top_10_lineages_df()
        self.df_signal_mutations = self.meth_split_mutation_col(self.df_unfiltered_signal)
        self.df_signal_mutations_stats = self.meth_calc_mutations_statistics(self.df_signal_mutations)
        self.df_profile_mutation, self.df_profile_gene_mutation = self.meth_calc_mutations_conserved(
            self.df_signal_mutations_stats)
        self.meth_save_mutations_conserved_perc()
        self.df_profile_mutation_ordered = self.meth_order_mutations(self.df_profile_mutation)
        self.meth_save_mutation_profile()
        self.df_profile_gene_mutation_top_10, self.df_profile_mutation_ordered_top_10 \
            = self.meth_return_top_10_mutation_weightings()

    def meth_return_top_10_lineages(self):
        """
        :return: list containing top 10 lineages circulating in time-period of SIGNAL selection.
        """
        list_top_10_lineages = self.df_filtered_signal["usher_lineage"].value_counts().head(10).copy()
        list_top_10_lineages_alt = self.df_filtered_signal["usher_lineage"].value_counts()[:10].index.tolist().copy()
        self.logger.info(f"top 10 lineages = {list_top_10_lineages_alt}")
        return list_top_10_lineages, list_top_10_lineages_alt

    def meth_return_top_10_lineages_df(self):
        """
        :return: Checks that category of "Unassigned" lineage is not in top 10 lineage list, if it is found removes from
        list and returns amended list, if not found returns original list.
        """
        list_df_top_10_lineage = []
        if "Unassigned" in self.list_top_10_lineages_alt:
            self.list_top_10_lineages_alt.remove("Unassigned")

        for lineage in range(len(self.list_top_10_lineages_alt)):
            temp_df = self.df_unfiltered_signal[self.df_unfiltered_signal["usher_lineage"].eq(
                "%s" % self.list_top_10_lineages_alt[lineage])]
            list_df_top_10_lineage.append(temp_df)
        return list_df_top_10_lineage

    def meth_split_mutation_col(self, input_df):
        """
        :param input_df:
        :return: splits the mutations column into df containing one mutation per column per sequence row of
        lineage/SIGNAL.
        """
        temp_df = input_df.copy()
        temp_df["mutation"] = temp_df["mutations"]
        temp_df["mutation"] = temp_df["mutation"].str.replace("(", "", regex=True)
        temp_df["mutation"] = temp_df["mutation"].str.replace(")", "", regex=True)
        df_mutations = temp_df["mutation"].str.split(",", expand=True)
        return df_mutations

    def meth_calc_mutations_statistics(self, input_df):
        """
        :param input_df:
        :return: df that calculates mutation percentages conserved between matching sequences.
        """
        temp_df = input_df.copy()
        temp_df1 = temp_df.apply(pd.value_counts).copy()
        temp_df = (temp_df1.sum(axis=1, skipna=True) / len(temp_df) * 100).reset_index()
        # set df_mut_prof column headers
        list_column_headers = ["mutations",
                               "percentage_conserved"]
        temp_df.columns = list_column_headers
        return temp_df

    def meth_calc_mutations_conserved(self, input_df):
        """
        :param input_df:
        :return: calculated lineage/SIGNAL mutations profile dfs based off of 75% conservation threshold.
        """
        # os.chdir(self.path_save)
        temp_df = input_df.copy()
        # filter out mutations <75%.
        df_temp_profile = temp_df[temp_df["percentage_conserved"] >= 75].copy()
        self.logger.info(f"mutations conserved = {len(df_temp_profile)}")
        df_profile_gene_mutation = df_temp_profile.rename(columns={'mutations': 'gene_mutation'})
        df_profile_gene_mutation[["gene", "mutations"]] = df_profile_gene_mutation["gene_mutation"] \
            .str.split(":", n=1, expand=True)
        # df_profile_gene_mutation.to_csv(datetime.datetime.now().strftime('%Y%m%d')
        #                                 + "_signal_mutation_conservation.csv", encoding="utf-8", index=False)
        # ! Fix issue if poorly conserved -> breaks
        # split gene from mutation (str)
        df_temp_profile[["gene", "mutations"]] = df_temp_profile["mutations"].str.split(":", n=1, expand=True)
        # return df with gene + mutation -> format needed for therapeutics weighting lookup
        # group mutations by gene
        df_profile_mutation = pd.DataFrame(df_temp_profile.groupby(["gene"])["mutations"].apply(lambda x: ','.join(x))
                                           .reset_index())

        return df_profile_mutation, df_profile_gene_mutation

    def meth_save_mutations_conserved_perc(self):
        """
        :return: saves a copy of the df with the mutations found vs percentage coverage of the lineage/SIGNAL as .csv.
        """
        self.logger.info(f"saving mutations conserved percentages to dir: {self.path_save_dir}")
        self.df_profile_gene_mutation.to_csv(self.path_save_dir + "/" + datetime.datetime.now().strftime("%Y%m%d")
                                             + "_signal_mutations_conserved.csv", encoding="utf-8", index=False)

    def meth_order_mutations(self, input_df):
        """
        :param input_df:
        :return: merged df with mutations found in mutations profile ordered by position (rather than alphabetically).
        """
        # os.chdir(self.path_save)
        temp_df = input_df.copy()
        l1 = []
        df_gene = pd.DataFrame(temp_df["gene"]).copy()
        temp_df["mutations"] = temp_df["mutations"].str.replace("del", "-", regex=True)
        temp_df["mutations"] = temp_df["mutations"].str.replace("stop", ".", regex=True)
        # temp_df.rename(columns={"mutations": "mutation"}, inplace=True)
        for i in range(len(temp_df)):
            df_split = temp_df.loc[[i]]
            list_split = df_split["mutations"].str.split(",", expand=True)
            list_split = list_split.iloc[0].tolist()
            list_split = sorted(list_split, key=lambda x: int(x[1:-1]))
            # list_split = sorted([i for i in list_split if not i.isdigit()])
            l1.append(list_split)
        df_merged = pd.DataFrame(l1).copy()
        df_merged = pd.DataFrame(df_merged[df_merged.columns[0:]].apply(lambda x: ', '.join(x.dropna().astype(str)),
                                                                        axis=1)).copy()
        df_merged.columns = ["mutations"]
        df_merged = df_gene.join(df_merged)
        df_merged.columns = ["Gene", "Non-synonymous mutations >=75%"]
        return df_merged

    def meth_save_mutation_profile(self):
        """
        :return: saves a copy of the df with ordered lineage/SIGNAL mutations profile to save folder as .csv.
        """
        self.logger.info(f"saving mutation profile to dir {self.path_save_dir}")
        self.df_profile_mutation_ordered.to_csv(self.path_save_dir + "/" + datetime.datetime.now().strftime('%Y%m%d')
                                                + "_signal_mutation_profile.csv", encoding="utf-8", index=False)

    def meth_return_top_10_mutation_weightings(self):
        """
        :return: list of dfs for top 10 lineages' mutation profiles
        """
        list_top_10_lineage_t_weightings = []
        list_top_10_expanded = []
        for x in range(len(self.list_df_top_10_lineage_alt)):
            df_lineage = self.list_df_top_10_lineage_alt[x]
            lineage = df_lineage["usher_lineage"].max()
            self.logger.info(f"generating top 10 lineage mutation profiles, {x}: {lineage}")
            temp_df_mutations = self.meth_split_mutation_col(df_lineage)
            temp_df_signal_mutations_stats = self.meth_calc_mutations_statistics(temp_df_mutations)
            temp_df_profile_mutation, temp_df_profile_gene_mutation = self.meth_calc_mutations_conserved(
                temp_df_signal_mutations_stats)
            temp_df_ordered = self.meth_order_mutations(temp_df_profile_mutation)
            temp_df_ordered = temp_df_ordered.assign(usher_lineage=lineage)
            first_column = temp_df_ordered.pop('usher_lineage')
            temp_df_ordered.insert(0, 'usher_lineage', first_column)
            list_top_10_expanded.append(temp_df_profile_gene_mutation)
            list_top_10_lineage_t_weightings.append(temp_df_ordered)

        list_top_10_expanded = pd.concat(list_top_10_expanded)
        self.logger.info("calculating top 10 lineage mutation weightings")
        pd.concat(list_top_10_lineage_t_weightings).to_csv(self.path_save_dir + "/" +
                                                           datetime.datetime.now().strftime('%Y%m%d') +
                                                           "_top_10_lineage_mutation_profiles.csv", encoding="utf-8",
                                                           index=False)
        return list_top_10_expanded, list_top_10_lineage_t_weightings

    def meth_return_closest_variant_profile(self):
        """

        :return: note. currently need to manually add new variants to list (find alternate way).
        """
        temp_df = self.df_lineages_alias_list
        list_str_variant_names = ["BQ.1", "XBB.", "CH.1.1", "XBB.1.5", "XBB.1.16", "EG.5.1", "BA.2.86", "BA.2", "BA.5",
                                  "BA.2.75", "BA.4.6", "B.1.617.2", "BA.1", "BA.4"]

        for x in temp_df.parent:
            if x == "":
                temp_df.parent = temp_df.alias  # if there is no parent lineage set parent lineage to alias name

        list_variants = []
        for var in list_str_variant_names:
            # print(var)
            alias = var.split(".")[0]  # split on comma and take first element (prefix letter/s)
            number = var.split(".", 1)[
                1]  # split on first occurrence of comma and take second element (suffix number/s)
            # print(var)
            df_t = temp_df[temp_df["alias"].eq(alias)]
            df_t = df_t.assign(unaliased_lineage=df_t["parent"].astype(str) + "." + number)
            list_variants.append(df_t)
        df_variants_unaliased = pd.concat(list_variants)
        return df_variants_unaliased
