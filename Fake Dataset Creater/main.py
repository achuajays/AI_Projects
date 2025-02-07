import streamlit as st
import pandas as pd
from faker import Faker
import io
import json

# --- Language/Locale Option ---
st.sidebar.header("Faker Locale")
locale = st.sidebar.selectbox(
    "Select Faker Locale:",
    options=["en_US", "en_GB", "de_DE", "fr_FR", "es_ES", "it_IT"],
    index=0
)

# Initialize Faker instance with the selected locale
fake = Faker(locale)

# --- Define Available Fields ---
available_fields = {
    "Name": lambda: fake.name(),
    "Address": lambda: fake.address(),
    "Email": lambda: fake.email(),
    "Phone Number": lambda: fake.phone_number(),
    "Job": lambda: fake.job(),
    "Company": lambda: fake.company(),
    "Text": lambda: fake.text(max_nb_chars=200),
    "Country": lambda: fake.country(),
    "City": lambda: fake.city(),
    "Date": lambda: fake.date()
}

# --- App Title and Description ---
st.title("Enhanced Fake Data Generator")
st.write(
    """
    This application uses the Faker library to generate fake data. 
    You can select the fields you want to include, choose a language/locale, and select the output format (CSV, JSON, or JSONL).
    """
)

# --- User Input for Data Generation ---
# Select fields to include
selected_fields = st.multiselect(
    "Select fields to include:",
    options=list(available_fields.keys()),
    default=["Name", "Address", "Email"]
)

# Choose number of records to generate
num_records = st.number_input("Number of records:", min_value=1, max_value=1000000, value=10, step=1)

# Select output file format
file_format = st.radio(
    "Select output file format:",
    options=["CSV", "JSON", "JSONL"]
)

# --- Data Generation and File Creation ---
if st.button("Generate File"):
    if not selected_fields:
        st.error("Please select at least one field.")
    else:
        # Generate fake data
        data = []
        for _ in range(num_records):
            record = {field: available_fields[field]() for field in selected_fields}
            data.append(record)

        # Convert data into a DataFrame for CSV or JSON formatting if needed
        df = pd.DataFrame(data)

        # Prepare file data based on selected format
        if file_format == "CSV":
            file_buffer = io.StringIO()
            df.to_csv(file_buffer, index=False)
            file_data = file_buffer.getvalue()
            file_name = "fake_data.csv"
            mime = "text/csv"
        elif file_format == "JSON":
            file_data = df.to_json(orient="records", indent=4)
            file_name = "fake_data.json"
            mime = "application/json"
        elif file_format == "JSONL":
            # Create JSON Lines (each record is a JSON object per line)
            jsonl_lines = [json.dumps(record) for record in data]
            file_data = "\n".join(jsonl_lines)
            file_name = "fake_data.jsonl"
            mime = "application/jsonl"
        else:
            st.error("Unsupported file format selected.")
            file_data = None

        # Provide a download button if file_data is created
        if file_data is not None:
            st.download_button(
                label=f"Download {file_format}",
                data=file_data,
                file_name=file_name,
                mime=mime
            )
            st.success(f"{file_format} file generated successfully!")