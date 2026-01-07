import os
import datetime
from azure.storage.blob import BlobServiceClient, ContentSettings
from weasyprint import HTML
from bs4 import BeautifulSoup

# Get the current date and time
now = datetime.datetime.now()

# Format the date and time as a string
date_string = now.strftime("%Y%m%d")
resume_pdf_file = f'Frank_Refol_Resume_{date_string}.pdf'
html_file = "index.html"  # Resume file

# Removing this whole section since we will point to latest pdf instead of dated pdf

try:
    # Read the HTML file
    with open(html_file, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")
    # Find the section with id="footer" and class="footer"
    footer_section = soup.find("section", {"id": "footer", "class": "footer"})

    # Modify Last updated date
    if footer_section:
        last_updated_tag = footer_section.find("p", class_="last-updated")
        if last_updated_tag:
            new_date = now.strftime("%B %d, %Y")
            last_updated_tag.string = f"Last updated: {new_date}"
            print(f"Updated last-updated date to: {last_updated_tag.string}")  # Success message
        else:
            print("No <p class='last-updated'> tag found in footer section.")
    else:
        print("Footer section not found.")

    #Write the updated HTML back to the file
    with open(html_file, "w", encoding="utf-8") as file:
        file.write(str(soup.prettify()))
except Exception as e:
    print(f"An error occurred trying to modify the html resume file: {e}")

try:
    # Convert HTML to PDF
    HTML(html_file).write_pdf(resume_pdf_file) 

except Exception as e:
    print(f"An error occurred trying to convert the resume to PDF: {e}")

connection_string = os.environ["AZURE_STORAGE_CONNECTION_STRING"]
container_name = os.environ["AZURE_STORAGE_CONTAINER"]

try:
    # Create a BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Get a client for the container
    container_client = blob_service_client.get_container_client(container_name)

    # Upload the file
    with open(resume_pdf_file, "rb") as data:
        container_client.upload_blob(
            name=resume_pdf_file, 
            data=data, overwrite=True, 
            content_settings=ContentSettings(content_type='application/pdf')
        )


    # Also upload as 'latest' for direct link
    with open(resume_pdf_file, "rb") as data:
        container_client.upload_blob(
            name="Frank_Refol_Resume_latest.pdf", 
            data=data, 
            overwrite=True,
            content_settings=ContentSettings(content_type='application/pdf')
        )

    print(f"File '{resume_pdf_file}' uploaded to blob '{resume_pdf_file}' in container '{container_name}'.")

    # Set GitHub Actions outputs
    with open(os.environ['GITHUB_OUTPUT'], 'a') as gh:
        gh.write(f"dated_pdf={resume_pdf_file}\n")
        gh.write(f"latest_pdf=Frank_Refol_Resume_latest.pdf\n")

except Exception as e:
    print(f"An error occurred trying to upload the resume PDF: {e}")
