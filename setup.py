from cx_Freeze import setup, Executable
import os

# Function to parse the requirements.txt file
def get_requirements():
    with open('requirements.txt') as f:
        requirements = f.readlines()
    return [r.strip() for r in requirements]

# Automatically include the required libraries from requirements.txt
install_requires = get_requirements()

# Specify build options for cx_Freeze
build_exe_options = {
    "packages": install_requires,  # Include all packages from requirements.txt
    "excludes": ["tkinter"],  # Exclude unnecessary packages
    "include_files": ['main.py']  # Add extra files if necessary (like data files)
}

# Setup the application
setup(
    name="Diff Checker",
    version="0.1",
    description="Streamlit App to Executable",
    options={"build_exe": build_exe_options},
    executables=[Executable("run.py", base=None)]  # Entry point of the Streamlit app
)
