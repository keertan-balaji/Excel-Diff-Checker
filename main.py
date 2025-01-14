import pandas as pd
import streamlit as st

st.set_page_config(layout="wide")
st.sidebar.title('Compare two CSV files')
left_column, right_column = st.columns(2)

uploaded_files = st.sidebar.file_uploader("Choose files", accept_multiple_files=True)
if uploaded_files:
    frames = []
    for uploaded_file in uploaded_files:
        file_name = uploaded_file.name
        frames.append((file_name, pd.read_excel(uploaded_file, skiprows=9, index_col=0)))

if st.sidebar.button("Show diff"):
    if not frames:
        st.error("Please upload files")
    elif len(frames) != 2:
        st.error("Please upload two files")
    else:
        name1, df1 = frames[0]
        name2, df2 = frames[1]
        
        # Display tables in columns
        left_column.title(f"Table: {name1}")
        right_column.title(f"Table: {name2}")
        
        # Identify unique specification numbers
        cols_unique_d1 = list(df1[~df1["Specification Number"].isin(df2["Specification Number"])]["Specification Number"])
        cols_unique_d2 = list(df2[~df2["Specification Number"].isin(df1["Specification Number"])]["Specification Number"])

        merged_table = pd.merge(df1, df2, on='Specification Number', suffixes=('_df1', '_df2'))
        diff_Qty = list(merged_table[merged_table['Qty_df1'] != merged_table['Qty_df2']]["Specification Number"])
        print(diff_Qty)
        # Highlight unique rows
        def highlight_unique_rows(s):
            if s['Specification Number'] in cols_unique_d1:
                return ['background-color: red'] * len(s)
            elif s['Specification Number'] in cols_unique_d2:
                return ['background-color: red'] * len(s)
            elif s['Specification Number'] in diff_Qty:
                return ['background-color: yellow'] * len(s)
            return [''] * len(s)

        # Show the tables with highlights
        left_column.dataframe(df1.style.apply(highlight_unique_rows, axis=1))
        right_column.dataframe(df2.style.apply(highlight_unique_rows, axis=1))
