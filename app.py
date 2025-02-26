import streamlit as st
import pandas as pd
import os 
from io import BytesIO
import fitz  # PyMuPDF for PDF text extraction

# Setup our app
st.set_page_config(page_title="Data Sweeper", layout='wide', initial_sidebar_state='expanded')
st.title("Data Sweeper")
st.markdown("### Transform your files between CSV and Excel formats with built-in data cleaning and visualization!")

# Sidebar Navigation
st.sidebar.header("Navigation")
page = st.sidebar.radio("Go to:", ["Upload Files", "Data Cleaning", "Visualization", "Text Extractor"])

st.sidebar.markdown("### Quick Tips:")
st.sidebar.info("Upload CSV or Excel files to start.")
st.sidebar.info("Use 'Data Cleaning' to remove duplicates.")
st.sidebar.info("Convert your files between formats easily.")

st.sidebar.markdown("### Feedback")
feedback = st.sidebar.text_area("Have any suggestions?")
if st.sidebar.button("Submit Feedback"):
    st.sidebar.success("Thanks for your feedback!")

uploaded_files = st.file_uploader("Upload your files (CSV and Excel):", type=["csv", "xlsx"], accept_multiple_files=True)

if uploaded_files:
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[-1].lower()

        if file_ext == ".csv":
            df = pd.read_csv(file)
        elif file_ext == ".xlsx":
            df = pd.read_excel(file)
        else:
            st.error(f"Unsupported file format: {file_ext}")
            continue

        st.write(f"File Name: {file.name}")
        st.write(f"File Size: {file.size/1024:.2f} KB")

        st.subheader("Data Preview")
        st.dataframe(df.head())

        st.subheader("Data Cleaning Options")
        if st.checkbox(f"Clean data for {file.name}"):
            col1, col2 = st.columns(2)

            with col1:
                if st.button(f"Remove Duplicates from {file.name}"):
                    df.drop_duplicates(inplace=True)
                    st.success("Duplicates Removed!")

            with col2:
                if st.button(f"Fill Missing Values for {file.name}"):
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                    st.success("Missing Values have been Filled!")

        st.subheader("Select Columns to Convert")
        columns = st.multiselect(f"Choose columns for {file.name}", df.columns, default=df.columns)
        df = df[columns]

        st.subheader("Data Visualization")
        if st.checkbox(f"Show Visualization for {file.name}"):
            st.bar_chart(df.select_dtypes(include='number').iloc[:, :2])

        buffer = None
        file_name = None
        mime_type = None

        st.subheader("Conversion Options")
        conversion_type = st.radio(f"Convert {file.name} to:", ["CSV", "Excel"], key=file.name)
        if st.button(f"Convert {file.name}"):
            buffer = BytesIO()
            if conversion_type == "CSV":
                df.to_csv(buffer, index=False)
                file_name = file.name.replace(file_ext, ".csv")
                mime_type = "text/csv"

            elif conversion_type == "Excel":
                df.to_excel(buffer, index=False)
                file_name = file.name.replace(file_ext, ".xlsx")
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            buffer.seek(0)

        if buffer:
            st.download_button(
                label=f"Download {file_name} as {conversion_type}",
                data=buffer,
                file_name=file_name,
                mime=mime_type,
            )

st.subheader("File to Text Extractor")
text_file = st.file_uploader("Upload a file (TXT, CSV, Excel, or PDF):", type=["txt", "csv", "xlsx", "pdf"])

if text_file:
    file_ext = os.path.splitext(text_file.name)[-1].lower()
    extracted_text = ""

    if file_ext == ".txt":
        extracted_text = text_file.read().decode("utf-8")
    elif file_ext == ".csv":
        df = pd.read_csv(text_file)
        extracted_text = df.to_string(index=False)
    elif file_ext == ".xlsx":
        df = pd.read_excel(text_file)
        extracted_text = df.to_string(index=False)
    elif file_ext == ".pdf":
        pdf_reader = fitz.open(stream=text_file.read(), filetype="pdf")
        extracted_text = "\n".join([page.get_text("text") for page in pdf_reader])

    st.text_area("Extracted Text:", extracted_text, height=300)

    if extracted_text:
        st.download_button(
            label="Download Extracted Text",
            data=extracted_text,
            file_name="extracted_text.txt",
            mime="text/plain"
        )

st.success("All files processed!")
