import pandas as pd
import streamlit as st
import os
from pathlib import Path
import shutil
import io, zipfile
# page parameters
st.set_page_config(layout="wide")
N_COLS = 2
columns = st.columns(N_COLS)

#Session state to check if data is downloaded
if 'data_downloaded' not in st.session_state:
    st.session_state['data_downloaded'] = False

# function to highlight rows
def highlight_unique_rows(s):
    if s['Specification Number'] in cols_unique_df:
        return ['background-color: red'] * len(s)
    elif s['Specification Number'] in diff_Qty:
        return ['background-color: yellow'] * len(s)
    return [''] * len(s)

def open_files(files):
    frames = []
    for file in files:
        file_name = file.name
        frames.append((file_name, pd.read_excel(file, skiprows=9, index_col=0)))
    return frames
# Sidebar
st.sidebar.title('Excel Diff')
reference_file = st.sidebar.file_uploader("Choose reference file", accept_multiple_files=False)
comparing_files = st.sidebar.file_uploader("Choose files to compare with", accept_multiple_files=True)
comparing_frames = None
#Button to perform check Difference
st.sidebar.title('Check Difference')
if st.sidebar.button("Show"):
    st.sidebar.markdown(f'''<table>
                        <tr>
                        <th><div style="width: 50px; height: 50px; background-color: #FF5733; border: 0px solid black;"></div></th>
                        <th><p style="font-size: 16px; color: {st.get_option("theme.textColor")}; text-align: center;">Spec Number not in reference file</p></th>
                        </tr>
                        <tr>
                        <th><div style="width: 50px; height: 50px; background-color: #FFFF00; border: 0px solid black;"></div></th>
                        <th><p style="font-size: 16px; color: {st.get_option("theme.textColor")}; text-align: center;">Spec Number with different Qty</p></th>
                        </tr>
                        </table>''',
                         unsafe_allow_html=True)
    if not reference_file:
        st.error("Please upload reference file")
    if not comparing_files:
        st.error("Please upload comparing files")

    # Read reference file
    reference_df = pd.read_excel(reference_file, index_col=0, skiprows=9)

    columns[0].write(f'''<h2>Ref: {reference_file.name.split('.')[0]}</h2>''', unsafe_allow_html=True)
    columns[0].write(f'''<p style="color: #0E1117;">...</p>''', unsafe_allow_html=True)
    columns[0].dataframe(reference_df)

    # Read files to be compared
    comparing_frames = open_files(comparing_files)

    for i,frame in enumerate(comparing_frames):        
        # Display tables in columns
        name, df = frame
        columns[(i+1)%N_COLS].write(f'''<h2>{name.split('.')[0]}</h2>''', unsafe_allow_html=True)
        
        # Identify unique specification numbers
        cols_unique_df = list(df[~df["Specification Number"].isin(reference_df["Specification Number"])]["Specification Number"])

        merged_table = pd.merge(df, reference_df, on='Specification Number', suffixes=('_df1', '_df2'))
        diff_Qty = list(merged_table[merged_table['Qty_df1'] != merged_table['Qty_df2']]["Specification Number"])
        
        #Calculate similarity
        count_common = len(list(reference_df[reference_df["Specification Number"].isin(df["Specification Number"])]["Specification Number"]))
        # count_unique_in_df = len(cols_unique_df)
        # count_common = len(reference_df) - count_unique_in_ref

        # similarity = (count_common/(count_unique_in_ref + count_unique_in_df + count_common))*100
        similarity = (count_common/len(reference_df))*100
        columns[(i+1)%N_COLS].write(f"Simillarity: {similarity:0.2f}%")
        columns[(i+1)%N_COLS].dataframe(df.style.apply(highlight_unique_rows, axis=1))

#Download zip of processed files
st.sidebar.title('Download Files')
if st.sidebar.button("Download"):
    if comparing_frames is None:
        if not comparing_files:
            st.error("Please upload comparing files")
        else:
            comparing_frames = open_files(comparing_files)

    def create_excel_zip(frames):
    # Create a BytesIO buffer to hold the zip file in memory
        zip_buffer = io.BytesIO()
        # Create a zip file in memory
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Iterate over the list of dataframes and filenames
            for filename, df in frames:
                # Create an in-memory BytesIO buffer to hold each Excel file
                excel_buffer = io.BytesIO()
                
                # Write the DataFrame to the Excel file (in memory)
                with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False)

                # Ensure the buffer is ready for reading
                excel_buffer.seek(0)
                
                # Add the Excel file to the zip
                zipf.writestr(f'{filename.split('.')[0]}.xlsx', excel_buffer.getvalue())

        # Set the file pointer to the beginning of the zip buffer
        zip_buffer.seek(0)

        return zip_buffer

    zip_data = create_excel_zip(comparing_frames)
    st.title("Please Click the Download button to begin Downloading...")
    st.download_button(
        label="Download Files",
        data=zip_data,
        file_name='processed_files.zip',
        mime='application/zip'
    )