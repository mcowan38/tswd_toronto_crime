#### Preamble ####
# Purpose: Executes the full data processing pipeline for Toronto neighbourhood crime and Census profile data.
# Author: Mike Cowan
# Date: 19 May 2025
# Contact: m.cowan@mail.utoronto.ca
# License: MIT
# Pre-requisites:
# - Imports `importlib` to load and run scripts with prefix-numbered filenames.
# - Each script must define a `main()` function.
# - Progress messaging is handled inside each script's `main()`.
# References:
# - [https://realpython.com/python-main-function/]

#### Workplace setup ####
import importlib.util
from pathlib import Path
import traceback

import importlib.util  # For loading scripts dynamically
from pathlib import Path  # For handling file paths
import traceback  # For printing full error tracebacks

#### Pipeline: ordered list of Python filenames (no need for ".py") ####
pipeline = [
    "01.0-simulate_data",
    "02.0-download_data",
    "03.0-clean_crime_data",
    "03.1-clean_profile_data",
    "04.0-merge_crime_profile",
    "05.0-eda_neighbourhood_clusters",
    "06.0-table_crime_clusters",
    "07.0-plot_crime_clusters",
    "08.0-model_evaluation",
]


#### Import a Python script by its file path and load as a module ####
# Module spec: where is the module located, what name to give it and how to load it.
# [https://docs.python.org/3/library/importlib.html#importlib.util.spec_from_file_location]
def import_module_from_file(script_file: Path):
    module_name = script_file.stem.replace(".", "_")  # convert "." to "_"
    spec = importlib.util.spec_from_file_location(
        module_name, script_file
    )  # Create a module spec from the file path
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


#### Main Pipeline Execution ####
def main():
    for filename in pipeline:
        script_path = (
            Path(__file__).parent / f"{filename}.py"
        )  # Absolute path to script
        print(f"Running: {filename}.py")

        try:
            module = import_module_from_file(script_path)  # Load script as module
            module.main()  # Call its main() function
        except Exception:
            print(f"Error occurred while running: {filename}.py")
            traceback.print_exc()


#### Entry Point ####
if __name__ == "__main__":
    main()
    print("Pipeline completed successfully.")
