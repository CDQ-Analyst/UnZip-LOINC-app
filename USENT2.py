import streamlit as st
import pandas as pd
import zipfile
import io
import os
import time

# Create a permanent unzip directory
UNZIP_DIR = "unzipped_files"
os.makedirs(UNZIP_DIR, exist_ok=True)

# Title & Sidebar
st.sidebar.header('Unzip Summary of Episode Note (USENT)')
st.header('Unzip Summary of Episode Note (USENT)')

# Upload Meta File
uploaded_file = st.sidebar.file_uploader("Choose a Meta File", type=['csv'])

df = None  # Placeholder for the dataframe
file_names = []  # Placeholder for file names

# If Meta file is uploaded
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.header("Meta File Data")
    st.title("_Data Upload Completed_ :sunglasses:")
    st.text(f'Data Frame Shape : {df.shape}')
    st.write(df.head())

    loinc_file = pd.crosstab(df['Organization'], df['LOINC'])
    st.write(loinc_file.head())

else:
    st.warning("Please upload a Meta File to proceed.")

# Upload ZIP file
uploaded_zip = st.sidebar.file_uploader("Choose a Zipped File", type=["zip"])
zip_bytes = None
if uploaded_zip is not None:
    zip_bytes = io.BytesIO(uploaded_zip.read())

    with zipfile.ZipFile(zip_bytes, "r") as zip_ref:
        file_list = zip_ref.namelist()

        # Filter only .csv files and get base file names
        excel_files = [f for f in file_list if f.endswith(".csv")]
        file_names = [os.path.basename(f) for f in excel_files]


# Proceed if Meta file is uploaded
if df is not None:

    # Sidebar Filters
    loinc_options = ["Select All"] + sorted(df['LOINC'].dropna().unique())
    selected_loinc = st.sidebar.selectbox("Filter by LOINC", loinc_options)

    org_options = ["Select All"] + sorted(df['Organization'].dropna().unique())
    selected_org = st.sidebar.selectbox("Filter by Organization", org_options)

    # Start with full data
    filtered_df = df.copy()

    # Apply LOINC filter
    if selected_loinc != "Select All":
        filtered_df = filtered_df[filtered_df["LOINC"] == selected_loinc]

    st.subheader(f"Filtered Data (LOINC: {selected_loinc})")
    st.write(filtered_df.head())

    # Apply Organization filter
    if selected_org == "Select All":
        filtered_df_by_loinc_org = filtered_df
    else:
        filtered_df_by_loinc_org = filtered_df[filtered_df["Organization"] == selected_org]

    st.subheader(f"Filtered Data (LOINC: {selected_loinc}, Organization: {selected_org})")
    st.write(filtered_df_by_loinc_org.head())

    # Show matching file names regardless of selected_org
    st.subheader("Matching File Names from ZIP:")
    st.write("Number of Matched Files", len(filtered_df_by_loinc_org))
    st.write("First 3 Files:")
    st.write(filtered_df_by_loinc_org['File_Name'].to_list()[:3])


    # Show unzip button only if ZIP is uploaded
    if uploaded_zip is not None:
        if st.button("UnZip Matching Files"):
            start_time = time.time()  # ⏱️ Start timer

            with zipfile.ZipFile(zip_bytes, "r") as zip_ref:
                matched_files = filtered_df_by_loinc_org['File_Name'].dropna().unique().tolist()
                matched_files_set = set(matched_files)

                extracted_files = []
                total_files = len(matched_files_set)
                progress = st.progress(0, text="Extracting matching files...")

                for i, file in enumerate(zip_ref.namelist()):
                    base_name = os.path.basename(file)
                    if base_name in matched_files_set:
                        zip_ref.extract(file, UNZIP_DIR)
                        extracted_files.append(base_name)

                    progress.progress(min((i + 1) / total_files, 1.0),
                                      text=f"Extracting: {min(i+1, total_files)} / {total_files}")

            end_time = time.time()  # ⏱️ End timer
            time_taken = end_time - start_time

            if extracted_files:
                progress.progress(1.0, text="✅ Extraction complete!")
                st.title("_Unzip and Extrac is Completed_ :sunglasses:")
                st.success(f"✅ Extracted {len(extracted_files)} matching file(s) to '{UNZIP_DIR}' folder.")
#                 st.write(extracted_files)
                st.info(f"🕒 Time taken: {time_taken:.3f} seconds")
            else:
                st.warning("⚠️ No matching files found in the ZIP archive.")


    
