import streamlit as st
import requests
import csv
import os
import uuid
import shutil
from zipfile import ZipFile
from io import BytesIO
from dotenv import load_dotenv
import math

# Load environment variables
load_dotenv()

# Set page config
st.set_page_config(
    page_title="Image Downloader",
    page_icon="🖼️",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
        .stAlert {
            padding: 1rem;
            border-radius: 0.5rem;
        }
        .block-container {
            padding-top: 2rem;
        }
        .main > div {
            padding: 0.5rem 0;
        }
        [data-testid="stMetricValue"] {
            font-size: 1.8rem;
        }
    </style>
""", unsafe_allow_html=True)


def get_images_batch(query, start=0):
    """
    Call the SerpAPI Google Images endpoint with pagination and return the JSON response.
    """
    params = {
        "engine": "google_images",
        "q": query,
        "google_domain": "google.com",
        "hl": "en",
        "gl": "us",
        "api_key": os.getenv("SERPAPI_KEY"),
        "start": start,
        "num": 100,
    }
    response = requests.get("https://serpapi.com/search.json", params=params)
    response.raise_for_status()
    return response.json()


def get_all_required_images(query, required_count):
    """
    Make multiple API calls if necessary to get the required number of images.
    """
    all_images = []
    calls_needed = math.ceil(required_count / 100)
    progress_bar = st.progress(0)

    for i in range(calls_needed):
        try:
            data = get_images_batch(query, start=i * 100)
            images = data.get("images_results", [])
            if not images:
                break
            all_images.extend(images)

            if len(all_images) >= required_count:
                break

            progress = (i + 1) / calls_needed
            progress_bar.progress(progress)

        except Exception as e:
            st.warning(f"Warning: Error in API call {i + 1}: {e}")
            break

    progress_bar.progress(1.0)
    return all_images[:required_count]


def download_and_save_images(images, query, images_folder="downloaded_images/images"):
    """
    Downloads the specified images and saves them in 'downloaded_images/images/'.
    """
    os.makedirs(images_folder, exist_ok=True)
    image_info = []
    progress_bar = st.progress(0)
    status_text = st.empty()

    for index, image in enumerate(images):
        status_text.text(f"Downloading image {index + 1} of {len(images)} for label '{query}'")
        image_url = image.get("thumbnail")
        if not image_url:
            continue

        try:
            img_data = requests.get(image_url).content
        except Exception as e:
            st.error(f"Error downloading image {index + 1} for label '{query}': {e}")
            continue

        unique_filename = f"{uuid.uuid4().hex}.jpg"
        file_path = os.path.join(images_folder, unique_filename)
        with open(file_path, "wb") as f:
            f.write(img_data)

        image_info.append({"label": query, "path": file_path})
        progress_bar.progress((index + 1) / len(images))

    status_text.empty()
    return image_info


def create_csv(image_info, csv_path="downloaded_images/images.csv"):
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    with open(csv_path, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["label", "path"])
        writer.writeheader()
        for info in image_info:
            writer.writerow(info)
    return csv_path


def create_zip_file(file_list):
    zip_buffer = BytesIO()
    with ZipFile(zip_buffer, "w") as zip_file:
        for file_path in file_list:
            arcname = os.path.relpath(file_path, "downloaded_images")
            zip_file.write(file_path, arcname=arcname)
    zip_buffer.seek(0)
    return zip_buffer


def main():
    st.title("🖼️ Image Downloader")

    # Manage form display and the number of label/count rows using session state
    if "show_form" not in st.session_state:
        st.session_state.show_form = False
    if "num_rows" not in st.session_state:
        st.session_state.num_rows = 1

    # Initially, show a single button
    if not st.session_state.show_form:
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Generate Image Labels", type="primary", use_container_width=True):
                st.session_state.show_form = True
        with col2:
            st.write("Click the button to generate image labels.")
    # When the button is clicked, display the dynamic multi-label form
    if st.session_state.show_form:
        st.markdown("### Configure Your Image Downloads for Multiple Labels")

        # Button to add a new label/count row
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Add New Label"):
                st.session_state.num_rows += 1
                try:
                    st.experimental_rerun()
                except AttributeError:
                    st.write("Please refresh the page to see the updated form.")
        with col2:
            if st.button("Remove Last Label") and st.session_state.num_rows > 1:
                st.session_state.num_rows -= 1
                try:
                    st.experimental_rerun()
                except AttributeError:
                    st.write("Please refresh the page to see the updated form.")

        with st.form("multi_label_form"):
            label_count_list = []
            for i in range(st.session_state.num_rows):
                col1, col2 = st.columns(2)
                with col1:
                    label_val = st.text_input(f"Label {i+1}", key=f"label_{i}")
                with col2:
                    count_val = st.number_input(f"Count {i+1}", min_value=1, max_value=1000, value=10, key=f"count_{i}")
                label_count_list.append((label_val, count_val))
            submit_form = st.form_submit_button("Start Download")

        if submit_form:
            all_image_info = []
            # Process each label/count pair sequentially
            for label_val, count_val in label_count_list:
                if not label_val:
                    st.warning("One of the rows is missing a label; skipping that row.")
                    continue
                st.write(f"Processing label: **{label_val}** for **{count_val}** images.")
                with st.spinner(f"Searching for images for '{label_val}'..."):
                    try:
                        images = get_all_required_images(label_val, count_val)
                    except Exception as e:
                        st.error(f"Error calling the API for '{label_val}': {e}")
                        continue
                if not images:
                    st.error(f"No images found for label '{label_val}'.")
                    continue
                with st.spinner(f"Downloading images for '{label_val}'..."):
                    image_info = download_and_save_images(images, label_val)
                    if not image_info:
                        st.error(f"No images could be downloaded for '{label_val}'.")
                        continue
                all_image_info.extend(image_info)

            # Once all labels have been processed
            if not all_image_info:
                st.error("No images were downloaded for any label.")
                return

            # Create a CSV with all image info
            csv_path = create_csv(all_image_info)

            # Display metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Images Downloaded", len(all_image_info))
            with col2:
                st.write("Multiple labels processed")
            with col3:
                total_size = sum(os.path.getsize(info["path"]) for info in all_image_info)
                st.metric("Total Size", f"{total_size / 1024 / 1024:.1f} MB")

            # Prepare a ZIP file containing the CSV and all images
            files_to_zip = [csv_path] + [info["path"] for info in all_image_info]
            zip_file = create_zip_file(files_to_zip)

            st.download_button(
                label="📦 Download ZIP Archive",
                data=zip_file,
                file_name="images_and_data.zip",
                mime="application/zip",
                use_container_width=True
            )

            # Display the downloaded images
            st.markdown("### Downloaded Images")
            cols = st.columns(5)
            for idx, info in enumerate(all_image_info):
                with cols[idx % 5]:
                    st.image(info["path"], caption=f"{info['label']} - {idx+1}", use_container_width=True)

            # Cleanup temporary files
            try:
                shutil.rmtree("downloaded_images")
            except Exception as e:
                st.error(f"Error cleaning up temporary files: {e}")

            # Reset the form state
            st.session_state.show_form = False
            st.session_state.num_rows = 1


if __name__ == "__main__":
    main()