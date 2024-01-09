# <span style="color:maroon">SARs-CoV-2 Signals Analysis</span>
<span style="color:grey">Version: 2.2.</span> \
<span style="color:grey">Last updated: 29.11.23.</span>


## 1. Summary

This package is intended for the manual and or automation running of signal review analysis which serves function within 
Horizon Scanning (GPHA) bi-weekly reporting and meetings.
Signals are defined as groups of sequences that share categorically collective attributes of interest concerning 
epidemiological clusters. These can be specified by a signal number; lineage, mutation/s and or nucleotides present with 
sequences.

## 2. Instructions

### 2.1 Setup
- Local
  - Acquire access to GPHA Gitlab repo
  - Gitlab repo can be found: https://gitlab.phe.gov.uk/gpha/horizon-scanning/sars_cov2_signals_automation.git
  - clone local copy of repo (master branch)
  - Use requirements.txt to install packages (added specific versioning to prevent clashes)
  - Run signals_data_ingest notebook to acquire most recent linked data (alternatively these are set to run weekly)
  - signals_data_ingest notebook can be found: 
  https://adb-5707723050064194.14.azuredatabricks.net/?o=5707723050064194#notebook/3701775936234666
  - Note. signals_data_ingest notebook requires Databricks access
  - Create folder for storing data, recommended: /home/phe.gov.uk/{user}/Desktop/latest_data
  - From StorageExplorer copy most recent metadata_source_files: [yyyymmdd_{region}_last_100_days.csv]
  - If required from StorageExplorer copy most recent signals_log: [yyyymmdd_sars_cov_2_signals_log_v1.csv]
  - StorageExplorer metadata data folder can be found: 
  https://edgeprdphestr.blob.core.windows.net/phe-to-edge/horizon_scanning_data/sars_cov2_signals_reporting/
  - StorageExplorer signals_log folder can be found: 
  https://edgeprdphestr.blob.core.windows.net/phe-to-edge/horizon_scanning_data/sars_cov2_signals_reporting/
- Online
  - Acquire access to GPHA Databricks
  - Online repo can be found:
  - Use signals_trigger notebook in which the entry box acts as a terminal
  - signals_trigger notebook can be found:
  - note default signal analysis save location: 
  https://edgeprdphestr.blob.core.windows.net/phe-to-edge/horizon_scanning_data/sars_cov2_signals_reporting/
  - note default signals_log save location:
  https://edgeprdphestr.blob.core.windows.net/phe-to-edge/horizon_scanning_data/sars_cov2_signals_reporting/

  
### 2.2 Inputs (files)
- Data
  - yyyymmdd_{region}_last_100_days.csv: int or uk metadata files
  - yyyymmdd_sars_cov_2_signals_log_v1.csv: signals log recording signal activity, monitoring history and any related 
    actions taken
- Modules
  - template_1_title.pptx: presentation title slide template
  - template_2_main.ppx: presentation general slide template
  - Counties_and_Unitary_Authorities__December_2017___EW_BGC.geojson: used in geographic mapping of cases
  - 20220214_therapeutic_weighted_contact_sites_long_format.csv: used for the therapeutic scoring of signals against
    different treatments (no longer in use)

### 2.3 Terminal Commands
- Log specifications
  - -logging: argument to set the logging level, default set to ERROR (optional)
- Environment specifications
  - -i: path to data directory (int/uk data csv, signal_logs when applicable) (required if -local and not -f)
  - -f: path to data with custom filename, mutually exclusive to -i (optional)
  - -o: specified save location direction, default will create sub-folder in main.py parent directory (optional)
  - -local: flag to set to local (user machine) environment, mutually exclusive to -online (required)
  - -online: flag to set to online (Databricks) environment, mutually exclusive to -local (required)
- Running specifications
  - -routine: flag to turn on routine analysis (optional)
  - -date_begin: set start date (optional, used in validation)
  - -eng: flag for running eng/uk analysis, mutually exclusive to -int (required if not -int or -routine)
  - -int: flag for running int analysis, mutually exclusive to -eng (required if not -eng or -routine)
- Signal specifications
  - -n: signal identification number (required if not -routine)
  - -l: UShER lineage (add spec_ for specific) (optional, cannot take multiple lineages)
  - -v: variant reference, mutually exclusive to -l (optional, no longer supported)
  - -m: mutation/s in format E:484K, for multiple create space seperated list, mutually exclusive to -nucl (optional)
  - -nucl: nucleotide/s, for multiple create space separated list, mutually exclusive to -m (optional)

### 2.4 Use
Once user's local or online environment has been initiated and libraries/pancakes successfully installed. User can run 
commands in their local terminal or call terminal within Databricks where package has been initialised as a wheel to 
run analysis for individual signals or those "Open" with supplied signals_log.csv.

## 3. Examples
#### <span style="color:maroon">python main.py -i /home/phe.gov.uk/{user}/Desktop/latest_data -local -n 455 -l FL.1 -r eng -o {path_to_output} Version: 2.2.</span> 
will run analysis with parameters; signal no (S455), lineage (FL.1), mutations (none), nucleotides (none). Analysis will
be performed within user's local environment using latest UK dataset .csv following standard naming pattern located in
specified directory -i (/home/phe.gov.uk/{user}/Desktop/latest_data). Results will be saved in specified output location
-o (path_to_output).

#### <span style="color:maroon">python main.py -i /home/phe.gov.uk/{user}/Desktop/latest_data -local -n S451 -l BA.2 -m S:F456L S:L456F -r int</span> 
will run manual single signal analysis with parameters; signal no (S451), lineage (BA.2), mutations (S:F456L & S:L456F),
nucleotides (none). Analysis will be performed within user's local environment using latest Int. dataset .csv following 
standard naming pattern located in specified directory -i (/home/phe.gov.uk/{user}/Desktop/latest_data). Results will be
saved in default location (main.py parent folder).

#### <span style="color:maroon">python main.py -i {path_to_blob_container} -routine -online -logging DEBUG</span> 
will run automated, online, routine analysis for all signals with current "OPEN" status within the
signals_automation_log.csv. Data will be loaded from -i {path_to_blob_container} (signals logs, UK & Int. csv). Results 
will be saved to default location within StorageExplorer. Logfile will be run with DEBUG setting as opposed to the 
default, INFO.

#### <span style="color:maroon">python main.py -i /home/phe.gov.uk/{user}/Desktop/latest_data -routine -local</span> 
will run automated local, routine analysis for all signals with current "OPEN" status within the 
signals_automation_log.csv. Data will be loaded from -i (/home/phe.gov.uk/{user}/Desktop/latest_data) (signals logs, UK
& Int. csv). Results will be saved to default location (main.py parent folder).

#### <span style="color:maroon">python main.py -f /home/phe.gov.uk/{user}/Home/{custom_folder}/{custom_name.csv} - local -n S555 -l BA.2 -m S:F456L S:L456F any -r eng</span>  
will run manual single signal analysis with parameters, signal no (S555), lineage (BA.2), mutations (S:F456L &/OR 
S:L456F), nucleotides (none). Analysis will be performed within user's local environment using UK dataset supplied in -f
(home/phe.gov.uk/{user}/Home/{custom_folder}/{custom_name.csv}). Results will be saved in default location (main.py 
parent folder).

## 4. Troubleshooting
- python main.py -h returns list of help information for commands
- Run in debug mode: -logging DEBUG
- See logfiles
- Package no longer supports variant calls
- Package not currently supportive of nucleotide command option
- Package not currently tested for custom input and output commands -f, -o
- Cannot designate a signal to multiple lineage calls, but can do with mutations, and nucleotides
- The mutation (-m) and nucleotide (-) are mutually exclusive to one another
- -local UK map generation requires internet access

## 5. Miscellaneous
- ~~URGENT fix issue with collapsing lineage nomenclature aliases!~~ (14.11.23)
- Fix compare lineage mutation profile to closest variant
- ~~Fix DataBricks integration~~
- ~~Fix date_begin command~~ (16.11.23)
- Finish growth analysis methods
- ~~Finish updates to logs when -routine settings~~ (17.11.23)
- Add unit testing
