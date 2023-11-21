import logging
from datetime import datetime


# %%

class ClassSignalSpecify:
    def __init__(self, input_signal_no, input_region, input_lineage, input_mutations, input_nucleotides, input_logs,
                 input_logging_level, input_location, input_filename, input_date_begin, input_path_input):
        self.date = datetime.now()
        self.df_logs = input_logs
        self.logging_level = input_logging_level
        self.location = input_location
        self.filename = input_filename
        self.date_begin = input_date_begin
        self.path_input = input_path_input
        self.data_region = input_region
        self.lineage = input_lineage
        self.mutations = input_mutations
        self.nucleotides = input_nucleotides
        self.logfile, self.signal_no = self.meth_return_logfile_name_str(input_signal_no)
        self.val_logging_level = self.meth_return_logging_value()
        self.logger = self.meth_setup_logger()
        self.logger.info(f"initialising log file of signal: {str(self.signal_no)}")
        self.logger.info(f"logging level: {str(self.logging_level)}")

    def meth_return_routine_signal_parameters(self, input_signal_no):
        if input_signal_no is None:
            args_signal_no = "none"
            return args_signal_no
        else:
            args_signal_no = input_signal_no
            return args_signal_no

    def meth_return_logfile_name_str(self, input_signal_no):
        signal_no = self.meth_return_routine_signal_parameters(input_signal_no)
        logfile = "LOGFILE_" + self.date.strftime("%Y%m%d") + "_" + signal_no + "_" + self.logging_level + ".log"
        return logfile, signal_no

    def meth_return_logging_value(self):
        """
        Return logging value from string selection input.
        :return:
        """
        if self.logging_level == "INFO":
            level = logging.INFO
        elif self.logging_level == "DEBUG":
            level = logging.DEBUG
        elif self.logging_level == "WARNING":
            level = logging.WARNING
        elif self.logging_level == "ERROR":
            level = logging.ERROR
        elif self.logging_level == "CRITICAL":
            level = logging.CRITICAL
        else:
            level = logging.INFO
        return level

    def meth_setup_logger(self):
        # clear/rest handlers
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        logging.basicConfig(filename=self.logfile,
                            filemode="a",
                            level=self.meth_return_logging_value(),
                            format="%(asctime)s %(levelname)s: %(message)s",
                            datefmt="%d/%m/%y %H:%M:%S")
        logger = logging.getLogger(self.logfile)
        # disable silly matplotlib and imagetk errors
        logging.getLogger('matplotlib.font_manager').disabled = True
        logging.getLogger("PIL").propagate = False
        return logger
