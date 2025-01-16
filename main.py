import pandas as pd
import streamlit as st

# page parameters
st.set_page_config(layout="wide")
N_COLS = 2
columns = st.columns(N_COLS)

# function to highlight rows
def highlight_unique_rows(s):
    if s['Specification Number'] in cols_unique_df:
        return ['background-color: red'] * len(s)
    elif s['Specification Number'] in diff_Qty:
        return ['background-color: yellow'] * len(s)
    return [''] * len(s)

# Sidebar
st.sidebar.title('Excel Diff')
reference_file = st.sidebar.file_uploader("Choose reference file", accept_multiple_files=False)
comparing_files = st.sidebar.file_uploader("Choose files to compare with", accept_multiple_files=True)

if st.sidebar.button("Show diff"):
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

    columns[0].title("Ref: " + reference_file.name)
    columns[0].write(f'''<p style="color: #0E1117;">...</p>''', unsafe_allow_html=True)
    columns[0].dataframe(reference_df)

    # Read files to be compared
    comparing_frames = []
    for file in comparing_files:
        file_name = file.name
        comparing_frames.append((file_name, pd.read_excel(file, skiprows=9, index_col=0)))

    for i,frame in enumerate(comparing_frames):        
        # Display tables in columns
        name, df = frame
        columns[(i+1)%N_COLS].title(f"{name}")
        
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
