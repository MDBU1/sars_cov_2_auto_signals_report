import glob
import os
import sys
from time import sleep
import pandas as pd
from tqdm import tqdm, trange
import uuid
import pathlib
import IPython

from modules.class_signal_specify import ClassSignalSpecify
from modules.output_signals_log import ClassSignalsLogUpdate, ClassLogInfo
from modules.output_pptx import ClassPresentationSetup
from modules.setup_argparse_commands import ClassSetupArgparseCommands

# %%


class ClassRoutineRunning(ClassSetupArgparseCommands):
    def __init__(self):
        super().__init__()
        self.path_input = self.meth_return_return_path_input_data()
        # self.df_logs = self.meth_is_routine()
        # self.df_log_sim_active, self.list_log_sim_active_no = self.meth_return_signals_active()
        # self.args.signal_no, self.args.lineage, self.args.mutations, self.args.data_region = \
        #    self.meth_automate_log_signal_calls()
        self.df_logs, self.df_log_sim_active, self.list_log_sim_active_no, self.signal_no, self.lineage,\
            self.mutations, self.data_region = self.meth_is_routine()

    def get_dbutils(self):
        from pyspark.sql import SparkSession
        spark = SparkSession.builder.getOrCreate()
        if spark.conf.get("spark.databricks.service.client.enabled") == "true":
            from pyspark.dbutils import DBUtils
            return DBUtils(spark)
        else:
            import IPython
            return IPython.get_ipython().user_ns["dbutils"]

    def meth_get_databricks_libaries(self):
        if self.args.location is True:
            print("online")
            from genomicslib import database as db
            from genomicslib import storage
            from genomicslib.database import get_genomics_creds, get_pheip_creds, spark_read_sql

    def meth_databricks_storage(self):
        # dbutils = IPython.get_ipython().user_ns["dbutils"]
        # dbutils.fs.ls("dbfs:/databricks/")
        self.meth_get_databricks_libaries()
        print("hi")
        print(storage)
        mount_point = storage.mount_genomics()
        phe_mount_point = storage.mount_phe_to_edge()

        local_working_directory = os.path.join(os.path.sep, f'{uuid.uuid4()}')
        os.environ["LOCAL_WORKING_DIR"] = local_working_directory

        if not os.path.exists(local_working_directory):
            os.mkdir(local_working_directory)
        return mount_point, phe_mount_point

    def meth_return_return_path_input_data(self):
        if self.args.location is True and self.args.filename is None:  # online
            mount_point, phe_mount_point = self.meth_databricks_storage()
            path_input_data = f'{phe_mount_point}Mike/sars_cov2_signals_development/'  # default online location
            # self.logger.debug("data being loaded from: " + path_input_data)
            return path_input_data
        elif self.args.location is True and self.args.filename:
            path_input_data = self.args.filename
            # self.logger.debug("data being loaded from: " + path_input_data)
            return path_input_data
        elif self.args.location is False and self.args.filename is None:
            path_input_data = self.args.path_data
            # self.logger.debug("data being loaded from: " + path_input_data)
            return path_input_data
        elif self.args.location is False and self.args.filename:
            path_input_data = self.args.filename
            # self.logger.debug("data being loaded from: " + path_input_data)
            return path_input_data
        else:
            # self.logger.critical("!!!data load method not found!!!")
            return 0

    def meth_return_blob_log_csvs(self):
        mount_point, phe_mount_point = self.meth_databricks_storage()
        path_blob = f'{phe_mount_point}Mike/sars_cov2_signals_development'
        list_blob_files = dbutils.fs.ls(path_blob)
        latest_file = str(list_blob_files[-1].name)  # add .sorted
        # print(latest_file)
        ste_ref_fp = pathlib.Path(phe_mount_point, path_blob,
                                  latest_file)
        wd = pathlib.Path.cwd()
        dbutils.fs.cp(f'dbfs:{ste_ref_fp}', f"file:{wd / str(latest_file)}")
        df_logs = pd.read_csv(latest_file)
        list_blob_csvs = []
        for f in range(len(list_blob_files)):
            df = list_blob_files[f]
            filename = df.name
            list_blob_csvs.append(filename)
        return df_logs,  # list_blob_csvs

    def meth_return_local_log_csvs(self):
        input_df_string = "log"
        list_input_csv = sorted(glob.glob(self.path_input + "/*.csv"))
        latest_log = list(filter(lambda files: input_df_string in files, list_input_csv))[-1]
        latest_log = pd.read_csv(latest_log)
        return latest_log

    def meth_is_routine(self):
        if self.args.routine and self.args.location is True:
            print("routine analysis, log to be overwritten")
            df_logs = self.meth_return_blob_log_csvs()
            df_log_sim_active, list_log_sim_active_no = self.meth_return_signals_active(df_logs)
            self.meth_break_if_non_active()
            signal_no, lineage, mutations, data_region = self.meth_automate_log_signal_calls(df_log_sim_active,
                                                                                             list_log_sim_active_no,
                                                                                             df_logs)
            return df_logs, df_log_sim_active, list_log_sim_active_no, signal_no, lineage, mutations, data_region
        elif self.args.routine is True and self.args.location is False:
            df_logs = self.meth_return_local_log_csvs()
            self.meth_break_if_non_active()
            df_log_sim_active, list_log_sim_active_no = self.meth_return_signals_active(df_logs)
            signal_no, lineage, mutations, data_region = self.meth_automate_log_signal_calls(df_log_sim_active,
                                                                                             list_log_sim_active_no,
                                                                                             df_logs)
            return df_logs, df_log_sim_active, list_log_sim_active_no, signal_no, lineage, mutations, data_region
        else:
            print("non-routine analysis, no log interaction")
            df_logs = None
            df_log_sim_active, list_log_sim_active_no = None, None
            signal_no, lineage, mutations, data_region = self.args.signal_no, self.args.lineage, self.args.mutations,\
                self.args.data_region
            self.meth_automate_manual_call()
            return df_logs, df_log_sim_active, list_log_sim_active_no, signal_no, lineage, mutations, data_region

    def meth_remove_na_rows(self, input_logs):
        temp_df = input_logs
        temp_df["review_date"] = pd.to_datetime(temp_df["review_date"], format="%Y%m%d").dt.date
        temp_df = temp_df.dropna(how="all")
        return temp_df

    def meth_return_signals_active(self, input_logs):
        input_df_log = self.meth_remove_na_rows(input_logs)
        list_log_sim_active_no = []
        list_log_sim_active = []
        for x in input_df_log["signal_id"].unique():
            temp_df = input_df_log[input_df_log["signal_id"].eq(x)]
            temp_df_last_entry = temp_df.sort_values(['signal_id', 'review_date']).drop_duplicates('signal_id',
                                                                                                   keep='last')
            status = temp_df_last_entry[temp_df_last_entry["signal_status"].str.contains("Open", na=False, case=False)]
            if len(status) == 0:
                pass
            else:
                df_input = temp_df
                list_log_sim_active.append(df_input)
                list_log_sim_active_no.append(x)
        df_log_sim_active = pd.concat(list_log_sim_active)
        print(f"active signals: {list_log_sim_active_no}")
        return df_log_sim_active, list_log_sim_active_no

    def meth_break_if_non_active(self):
        if len(self.list_log_sim_active_no) == 0:
            sys.exit("NO ACTIVE SIGNALS")

    def meth_automate_log_signal_calls(self, input_active_log, input_list_log_active_no, input_full_log):
        temp_df_log = input_active_log
        temp_df_log = temp_df_log.replace("none", "")
        logs_run = ClassLogInfo()
        for x in tqdm(input_list_log_active_no):
            temp_df = pd.DataFrame(temp_df_log[temp_df_log["signal_id"].eq(x)].max())
            # temp_df = pd.DataFrame(temp_df_log[temp_df_log["signal_id"].astype(str).eq(x)])
            # temp_df = temp_df[temp_df["review_no"].eq(temp_df["review_no"].max())]
            signal_id = temp_df.loc["signal_id"][0]
            lineage = temp_df.loc["lineage"][0]
            mutations = temp_df.loc["mutations"][0].split()
            nucleotides = temp_df.loc["nucleotides"][0].split()
            print(f"running signal with parameters: \n"
                  f"signal no: {signal_id} \n"
                  f"lineage: {lineage} \n"
                  f"mutations: {mutations} \n"
                  f"nucleotides: {nucleotides}")
            data_region = "eng"
            print(f"data region: {data_region}")

            temp_class_signal = ClassSignalSpecify(signal_id, data_region, lineage, mutations, nucleotides, temp_df_log,
                                                   self.args.logging_level, self.args.location, self.args.filename,
                                                   self.args.date_begin, self.path_input)
            logs_run.meth_add_line(ClassSignalsLogUpdate(temp_class_signal).line)
            # ClassSignalsLogUpdate(temp_class_signal)
            data_region = "int"
            print(f"data region: {data_region}")
            temp_class_signal = ClassSignalSpecify(signal_id, data_region, lineage, mutations, nucleotides, temp_df_log,
                                                   self.args.logging_level, self.args.location, self.args.filename,
                                                   self.args.date_begin, self.path_input)
            # temp_class_signal = ClassSetupFileConditions(temp_class_signal)
            logs_run.meth_add_line(ClassSignalsLogUpdate(temp_class_signal).line)
            # ClassLogInfo(ClassSignalsLogUpdate(temp_class_signal))
            sleep(0.00001)
        df_log_update = logs_run.meth_update_log(input_full_log)
        # df_log_update.to_csv(self.path_input + "/updated_log.csv")
        self.meth_save_log(df_log_update)
        return signal_id, lineage, mutations, data_region

    def meth_save_log(self, input_log):
        counter = 1
        filename = self.path_input + "/" + self.date.strftime("%Y%m%d") + "_sars_cov_2_signals_log_v{}.csv"
        while os.path.isfile(filename.format(counter)):
            counter += 1
        filename = filename.format(counter)
        input_log.to_csv(filename, index=False)

    def meth_automate_manual_call(self):
        temp_class_signal = ClassSignalSpecify(self.args.signal_no, self.args.data_region, self.args.lineage,
                                               self.args.mutations, "", None,
                                               self.args.logging_level, self.args.location, self.args.filename,
                                               self.args.date_begin, self.path_input)
        ClassPresentationSetup(temp_class_signal)  # no log supplied so don't need to call ClassSignalsLogUpdate
