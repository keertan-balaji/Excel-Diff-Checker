import pandas as pd
import streamlit as st

# page parameters
st.set_page_config(layout="wide",initial_sidebar_state="expanded")

st.session_state.sidebar_state = True 

# function to highlight rows
def highlight_unique_rows(s):
    if s['Specification Number'] in cols_unique_df:
        return ['background-color: red'] * len(s)
    elif s['Specification Number'] in diff_Qty:
        return ['background-color: yellow'] * len(s)
    return [''] * len(s)

st.markdown(
    """
    <style>
    .scrolling-wrapper {
        display: flex;
        overflow-x: auto;
    }
    .scrolling-wrapper > div {
        margin-right: 10px;
    }
    </style>
    """, unsafe_allow_html=True
)

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
    st.session_state.sidebar_state = False
    if not reference_file:
        st.error("Please upload reference file")
    if not comparing_files:
        st.error("Please upload comparing files")

    # Read reference file
    reference_df = pd.read_excel(reference_file, index_col=0, skiprows=9)
    st.title("Ref: " + reference_file.name)
    st.dataframe(reference_df)
    # Read files to be compared
    comparing_frames = []
    for file in comparing_files:
        file_name = file.name
        comparing_frames.append((file_name, pd.read_excel(file, skiprows=9, index_col=0)))
    
    st.markdown('<div class="scrolling-wrapper">', unsafe_allow_html=True)
    with st.container():
        cols = st.columns(len(comparing_frames))
        for i,frame in enumerate(comparing_frames):        
            # Display tables in columns
            name, df = frame
            cols[i].title(f"{name}")
            
            # Identify unique specification numbers
            cols_unique_df = list(df[~df["Specification Number"].isin(reference_df["Specification Number"])]["Specification Number"])

            merged_table = pd.merge(df, reference_df, on='Specification Number', suffixes=('_df1', '_df2'))
            diff_Qty = list(merged_table[merged_table['Qty_df1'] != merged_table['Qty_df2']]["Specification Number"])
            # Show the tables with highlights
            cols[i].dataframe(df.style.apply(highlight_unique_rows, axis=1))
    
    st.markdown('</div>', unsafe_allow_html=True)