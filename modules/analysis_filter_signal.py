import pandas as pd

from modules.setup_load_data import ClassLoadData

#%%


class ClassSignalSelect(ClassLoadData):
    def __init__(self, class_signal):
        super().__init__(class_signal)
        self.logger.debug(f"number of sequences in original dataframe: {len(self.df_unfiltered)}")
        self.df_unfiltered_signal, self.str_lineages_unaliased = self.meth_return_unaliased_lineage()
        self.logger.debug(f"number of sequences post lineage filter: {len(self.df_unfiltered_signal)}")
        self.df_unfiltered_signal = self.meth_select_mutations()
        self.logger.debug(f"number of sequences post mutations filter: {len(self.df_unfiltered_signal)}")
        self.df_lineage_subs = self.meth_return_sublineages()
        self.df_filtered_signal = self.meth_return_filtered_signal()

    def meth_select_lineage(self):
        """
        Description: Uses pre-defined lineage parameters from parent class.
        Options; "na" = no lineage to select -> returns inputted df, if "sub" present -> returns lineage incl.
        sub-lineages, else -> returns only specific lineage matching string.
        :return: df containing the pre-defined lineage parameter matching sequences based off usher lineage column.
        """
        lineage = self.lineage
        temp_df = self.df_unfiltered.copy()
        if lineage == "no_specified_lineage":
            temp_df_lineage = temp_df
        elif "spec_" in lineage:
            lineage = lineage.replace("spec_", "")
            temp_df_lineage = temp_df[temp_df["usher_lineage"].astype(str).eq(lineage)]
        else:
            temp_df_lineage = temp_df[temp_df["usher_lineage"].astype(str).str.contains(lineage, na=False)]
        self.logger.debug(f"pre lineage filter vs post lineage filter: {len(temp_df)}, {len(temp_df_lineage)}")
        return temp_df_lineage

    def meth_return_unaliased_lineage(self):
        self.logger.debug(f"matching lineage: {self.lineage} with unaliased lineage name")
        temp_df_lineages = self.df_lineages_unaliased.copy()
        temp_df_filtered = self.df_filtered.copy()
        if self.lineage == "":
            str_lineages_unaliased = ""
            df_lineage = temp_df_filtered
            self.logger.debug(f"sublineages: {str_lineages_unaliased}")
            return df_lineage, str_lineages_unaliased
        elif "spec_" in self.lineage:
            str_lineages_unaliased = temp_df_lineages[temp_df_lineages["usher_lineage"].eq(self.lineage)]
            df_lineage = temp_df_filtered[temp_df_filtered["usher_lineage"].eq(self.lineage)]
            self.logger.debug(f"unaliased call: {str_lineages_unaliased} (specific)")
            return df_lineage, str_lineages_unaliased
        else:
            str_lineages_unaliased = temp_df_lineages[
                temp_df_lineages["usher_lineage"].eq(self.lineage)]["unaliased_lineage"].item()
            df_lineage = temp_df_filtered[temp_df_filtered["unaliased_lineage"].str.contains(str_lineages_unaliased)]
            self.logger.debug(f"unaliased call: {str_lineages_unaliased}")
            self.logger.debug(f"sublineages: \n{df_lineage.usher_lineage.value_counts()}")
            self.logger.debug(f"unaliased df: \n{df_lineage}")
            return df_lineage, str_lineages_unaliased

    def meth_select_mutations(self):
        """
        Description Uses pre-defined mutations parameters from parent class.
        Options; "na"/use of custom id input = no mutations to select -> returns inputted df, if "any" present ->
        returns df of sequences containing 1 or more of specified mutation, else -> returns df of sequences with all
        mutations present.
        :return: df containing the pre-defined mutations parameter matching sequences based of mutations column.
        """

        mutations = self.mutations
        temp_df = self.df_unfiltered_signal.copy()
        if mutations:
            if mutations == "no_specified_mutations":
                df_mutations = temp_df
                return df_mutations
            elif "any" in mutations:
                self.logger.debug(f"mutations search to include any of: {mutations}")
                df_mutations = temp_df[temp_df["mutations"].astype(str).str.contains(",".join(mutations), na=False)]
                return df_mutations
            else:
                mutations_s = set(mutations)
                self.logger.debug(f"set mutations search: {mutations_s}")
                df_mutations = temp_df[temp_df["mutations"].astype(str).str.split(",").map(mutations_s.issubset)]
                return df_mutations
        else:
            self.logger.debug(f"no mutations specified, therefore not filtering dataframe for mutations")
            df_mutations = temp_df
            return df_mutations

    def meth_return_sublineages(self):
        list_lineage_subs = list(self.df_unfiltered_signal["usher_lineage"].unique())
        self.logger.info(f"sub-lineages present = {list_lineage_subs}")
        df_lineage_subs = pd.DataFrame(self.df_unfiltered_signal["usher_lineage"].value_counts())
        return df_lineage_subs

    def meth_return_filtered_signal(self):
        temp_df_filtered = self.df_filtered.copy()
        temp_df_unfiltered_signal = self.df_unfiltered_signal.copy()
        list_temp_df_filtered = list(temp_df_filtered["id"])
        temp_df_filtered_signal = temp_df_unfiltered_signal[temp_df_unfiltered_signal["id"].isin(
            list_temp_df_filtered)]
        self.logger.info(f"number of signal sequences post time filter, before vs after: "
                         f"{len(temp_df_unfiltered_signal)} vs {len(temp_df_filtered_signal)} \n"
                         f"note if unfiltered signal is greater than filtered suggests signal has been circulating "
                         f"for longer than time period analysed, i.e before {self.date_max}")
        return temp_df_filtered_signal
