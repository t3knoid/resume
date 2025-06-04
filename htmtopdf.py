import os
import datetime
from azure.storage.blob import BlobServiceClient
from weasyprint import HTML
from bs4 import BeautifulSoup

# Get the current date and time
now = datetime.datetime.now()

# Format the date and time as a string
date_string = now.strftime("%Y%m%d")
resume_pdf_file = f'Frank_Refol_Resume_{date_string}.pdf'

try:
    # Read the HTML file
    html_file = "index.html"  # Resume file
    with open(html_file, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")

    # Find the section with id="footer" and class="footer"
    footer_section = soup.find("section", {"id": "footer", "class": "footer"})

    # Modify the href inside the <a> tag
    if footer_section:
        link_tag = footer_section.find("a")
        if link_tag:
            link_tag["href"] = f"https://homelabstore1.blob.core.windows.net/$web/{resume_pdf_file}"  # New URL

    # Write the updated HTML back to the file
    with open(html_file, "w", encoding="utf-8") as file:
        file.write(str(soup.prettify()))
except Exception as e:
    print(f"An error occurred trying to modify the html resume file: {e}")

try:
    # Convert HTML to PDF
    HTML('https://t3knoid.github.io/resume/index.html').write_pdf(resume_pdf_file) 

except Exception as e:
    print(f"An error occurred trying to convert the resume to PDF: {e}")

# Replace with your Azure Storage account details
connection_string = "" #  Obtain from Azure portal under the storage account's "Access keys" section.
container_name = "$web"

try:
    # Create a BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Get a client for the container
    container_client = blob_service_client.get_container_client(container_name)

    # Upload the file
    with open(resume_pdf_file, "rb") as data:
        container_client.upload_blob(name=resume_pdf_file, data=data, overwrite=True)

    print(f"File '{resume_pdf_file}' uploaded to blob '{resume_pdf_file}' in container '{container_name}'.")

except Exception as e:
    print(f"An error occurred trying to upload the resume PDF: {e}")