import pandas as pd
import numpy as np

from modules.setup_load_data import ClassLoadData

#%%


class ClassSignalSelect(ClassLoadData):
    def __init__(self):
        super().__init__()

        self.df_unfiltered_signal = self.meth_select_lineage()
        self.df_unfiltered_signal = self.meth_select_mutations()
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
        return temp_df_lineage

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
        if mutations is not None:
            if mutations == "no_specified_mutations":
                df_mutations = temp_df
            else:
                mutations_s = set(mutations)
                df_mutations = temp_df[temp_df["mutations"].astype(str).str.split("|").map(mutations_s.issubset)]
        elif "any" in mutations:
            df_mutations = temp_df[temp_df["mutations"].astype(str).str.contains("|".join(mutations), na=False)]
        else:
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
        return temp_df_filtered_signal
