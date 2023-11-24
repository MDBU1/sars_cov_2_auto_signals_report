import pandas as pd

from modules.output_pptx import ClassPresentationSetup


# %%


class ClassSignalsLogUpdate(ClassPresentationSetup):
    def __init__(self, class_signal):
        super().__init__(class_signal)
        # print(self.df_logs)
        self.line = self.meth_return_latest_signal_update_row()

    def meth_return_signal_specification_parameters(self):
        lineage = self.lineage
        mutations = str(" ".join(self.mutations))
        nucleotides = self.nucleotides

        if lineage is None or lineage == "":
            str_lineage = "none"
        else:
            str_lineage = lineage

        if mutations == "no_specified_mutations" or mutations == "":
            str_mutations = "none"
        else:
            str_mutations = mutations

        if nucleotides == "no_specified_aa" or "[]":
            nucleotides = "none"
        else:
            nucleotides = nucleotides

        return str_lineage, str_mutations, nucleotides

    def meth_return_eng_log_text(self):
        if self.data_region == "eng":
            text = self.log_text
        else:
            text = ""
        return text

    def meth_return_int_log_text(self):
        if self.data_region == "int":
            text = self.log_text
        else:
            text = ""
        return text

    def meth_return_latest_signal_update_row(self):
        # print(self.df_logs.columns)

        temp_df = self.df_logs[self.df_logs["signal_id"].eq(self.signal_no)]  # get only rows for active signal
        index_position = temp_df.index.max()  # get max index position of signal
        # print(index_position)

        lineage, mutations, nucleotides = self.meth_return_signal_specification_parameters()
        line = pd.DataFrame({
            "signal_id": self.signal_no,
            "lineage": lineage,
            "mutations": mutations,
            "nucleotides": nucleotides,
            "signal_status": "Open",
            "review_no": temp_df["review_no"].max() + 1,
            "review_date": self.date.strftime('%Y%m%d'),
            "review_assessment_eng": self.meth_return_eng_log_text(),
            "review_assessment_int": self.meth_return_int_log_text(),
            "actions": ""
        },
            index=[index_position])
        # print(line)
        return line
        # df2 = pd.concat([self.df_logs.iloc[:index_position], line, self.df_logs.iloc[
        # index_position:]]).reset_index(drop=True) print(df2)


class ClassLogInfo:
    def __init__(self):
        self._lines = []

    def meth_add_line(self, new_line):
        self._lines.append(new_line)
        # print(f"new line added, line length: {len(self._lines)}")

    def meth_combine_signal_region_rows(self):
        df = pd.concat(self._lines)
        new_df = df.groupby(['signal_id']).max().reset_index()
        return new_df

    def meth_update_log(self, input_log):
        df_log = input_log.copy()
        df_updates = self.meth_combine_signal_region_rows()
        for signal_no in df_log["signal_id"].unique():
            index_max = df_log[df_log["signal_id"].eq(signal_no)].index.max()
            if df_log["signal_status"][index_max] == "Open":
                # print(f"signal {signal_no} open, position {index_max}")
                new_row = df_updates[df_updates["signal_id"].eq(signal_no)]
                df_log.loc[float(index_max + 0.5)] = new_row.values.flatten().tolist()
                df_log = df_log.sort_index().reset_index(drop=True)
        df_log["review_date"] = df_log["review_date"].astype(str).str.replace("-", "")
        return df_log
