import sys
import argparse
from datetime import datetime

# %%


class ClassSetupArgparseCommands:
    def __init__(self):
        self.args = self.meth_setup_command_line_args_options()
        self.date = datetime.now()

    def meth_setup_command_line_args_options(self):
        parser = argparse.ArgumentParser(description="")
        parser.add_argument("--logging_level",
                            "-logging",
                            dest="logging_level",
                            type=str,
                            choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                            default="INFO",
                            required=False,
                            help="optional argument to set the logging level, default set to ERROR")

        parser.add_argument("--routine",
                            "-routine",
                            dest="routine",
                            action="store_true",
                            help="flag to turn on routine analysis")

        parser.add_argument("--date_begin",
                            "-date_begin",
                            dest="date_begin",
                            type=lambda s: datetime.strptime(s, '%d-%m-%Y'),
                            required=False,
                            help=f"set start date, used for testing")

        group_location = parser.add_mutually_exclusive_group(required=True)
        group_location.add_argument("--online",
                                    "-online",
                                    dest="location",
                                    action="store_true")
        group_location.add_argument("--local",
                                    "-local",
                                    dest="location",
                                    action="store_false")

        # create data information group
        group_data = parser.add_argument_group("data"
                                               "data input/output information")
        group_data.add_argument("--path_data",
                                "-i",
                                dest="path_data",
                                required="-local" in sys.argv and "-f" not in sys.argv,
                                help="directory path of datafiles used for offline running")
        group_data.add_argument("--custom_filename",
                                "-f",
                                dest="filename",
                                required=False,
                                help="(path) custom filename for International or UK (pre-merged) datafile/s")
        group_data.add_argument("--path_save",
                                "-o",
                                dest="path_output",
                                required=False,
                                help="specified save location direction, default will create sub-folder in main.py "
                                     "parent directory")

        # create signal identifier group
        group_identifier = parser.add_argument_group("signal",
                                                     "signal description/identification arguments")
        group_identifier.add_argument("--signal_no",
                                      "-n",
                                      dest="signal_no",
                                      required="-routine" not in sys.argv,
                                      type=str,
                                      help="signal identification number, required if not running routine analysis")
        group_identifier.add_argument("--usher_lineage",
                                      "-l",
                                      dest="lineage",
                                      required=False,
                                      help="UShER lineage (add spec_ for specific)")
        group_identifier.add_argument("--mutations",
                                      "-m",
                                      dest="mutations",
                                      required=False,
                                      nargs="+",
                                      default=[],
                                      help="mutation/s in format E:484K, for multiple create space seperated list")
        group_identifier.add_argument("-nucleotides",
                                      "-ncul",
                                      dest="nucl",
                                      required=False,
                                      nargs="+",
                                      default=[],
                                      help="nucleotide/s, for multiple create space separated list")
        group_identifier.add_argument("--variant",
                                      "-v",
                                      dest="variant",
                                      required=False,
                                      help="variant reference")
        group_identifier.add_argument("--data_region",
                                      "-r",
                                      dest="data_region",
                                      choices=["uk", "eng"],
                                      required="-routine" not in sys.argv,
                                      help="option to select International or UK analysis to be run, required if not"
                                           "running routine analysis")
        args = parser.parse_args()
        print(args)
        return args

