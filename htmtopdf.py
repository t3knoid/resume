import os
import sys
import argparse
import datetime
from typing import Optional

from azure.storage.blob import BlobServiceClient, ContentSettings
from weasyprint import HTML
from bs4 import BeautifulSoup


def is_github_actions() -> bool:
    return os.environ.get("GITHUB_ACTIONS", "").lower() == "true"


def should_skip_upload(cli_no_upload: bool) -> bool:
    return cli_no_upload or (os.environ.get('SKIP_UPLOAD', '').lower() in ('1', 'true', 'yes'))


def read_html(path: str) -> str:
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def write_html(path: str, html: str) -> None:
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)


def parse_html(html: str) -> BeautifulSoup:
    # html5lib parser is HTML5-aware and robust for modern markup
    return BeautifulSoup(html, 'html5lib')


def update_last_updated(soup: BeautifulSoup, now: datetime.datetime) -> bool:
    footer = soup.find(id='footer')
    if not footer:
        return False
    p = footer.find('p', class_='last-updated')
    if not p:
        return False
    new_text = f"Last updated: {now.strftime('%B %d, %Y')}"
    p.string = new_text
    return True


def generate_pdf(html_path: str, pdf_path: str) -> None:
    HTML(html_path).write_pdf(pdf_path)


def upload_to_azure(connection_string: str, container_name: str, pdf_path: str) -> None:
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)
    # upload dated PDF
    with open(pdf_path, 'rb') as data:
        container_client.upload_blob(name=os.path.basename(pdf_path), data=data, overwrite=True,
                                     content_settings=ContentSettings(content_type='application/pdf'))
    # upload latest
    with open(pdf_path, 'rb') as data:
        container_client.upload_blob(name='Frank_Refol_Resume_latest.pdf', data=data, overwrite=True,
                                     content_settings=ContentSettings(content_type='application/pdf'))


def write_github_outputs(pdf_name: str) -> None:
    gha_out = os.environ.get('GITHUB_OUTPUT')
    if gha_out:
        with open(gha_out, 'a') as gh:
            gh.write(f"dated_pdf={pdf_name}\n")
            gh.write("latest_pdf=Frank_Refol_Resume_latest.pdf\n")


def main(argv: Optional[list] = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    parser = argparse.ArgumentParser(description='Generate resume PDF and optionally upload to Azure blob')
    parser.add_argument('--no-upload', action='store_true', help='Skip uploading the PDF to Azure')
    parser.add_argument('--html', default='index.html', help='HTML file to convert')
    parser.add_argument('--out', default=None, help='Output PDF filename (optional)')
    args = parser.parse_args(argv)

    now = datetime.datetime.now()
    date_string = now.strftime('%Y%m%d')
    html_file = args.html
    resume_pdf_file = args.out if args.out else f'Frank_Refol_Resume_{date_string}.pdf'

    try:
        html = read_html(html_file)
        soup = parse_html(html)
        changed = update_last_updated(soup, now)
        if changed:
            write_html(html_file, str(soup))
            print(f'Updated last-updated date in {html_file}')
        else:
            print('No footer/last-updated tag found or updated.')
    except Exception as e:
        print(f'Error updating HTML: {e}')
        return 1

    try:
        generate_pdf(html_file, resume_pdf_file)
        print(f'Generated PDF: {resume_pdf_file}')
    except Exception as e:
        print(f'Error generating PDF: {e}')
        return 1

    no_upload = should_skip_upload(args.no_upload)
    if no_upload:
        print('Skipping upload (no-upload requested).')
        return 0

    conn = os.environ.get('AZURE_STORAGE_CONNECTION_STRING')
    container = os.environ.get('AZURE_STORAGE_CONTAINER')
    if not conn or not container:
        print('AZURE_STORAGE_CONNECTION_STRING or AZURE_STORAGE_CONTAINER not set; skipping upload.')
        return 0

    try:
        upload_to_azure(conn, container, resume_pdf_file)
        print(f"Uploaded {resume_pdf_file} to container {container}")
        if is_github_actions():
            write_github_outputs(resume_pdf_file)
        return 0
    except Exception as e:
        print(f'Error uploading PDF: {e}')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
import os
import datetime
from azure.storage.blob import BlobServiceClient, ContentSettings
from weasyprint import HTML
from bs4 import BeautifulSoup
import sys
def is_github_actions() -> bool:
    return os.environ.get("GITHUB_ACTIONS", "").lower() == "true"

def should_skip_upload(cli_no_upload: bool) -> bool:
    return cli_no_upload or (os.environ.get('SKIP_UPLOAD', '').lower() in ('1', 'true', 'yes'))

def read_html(path: str) -> str:
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_html(path: str, html: str) -> None:
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)

def parse_html(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, 'html5lib')

def update_last_updated(soup: BeautifulSoup, now: datetime.datetime) -> bool:
    footer = soup.find(id='footer')
    if not footer:
        p = footer.find('p', class_='last-updated')
    if not p:
        return False

    new_text = f"Last updated: {now.strftime('%B %d, %Y')}"
    p.string = new_text
    return True

def generate_pdf(html_path: str, pdf_path: str) -> None:
    HTML(html_path).write_pdf(pdf_path)

def upload_to_azure(connection_string: str, container_name: str, pdf_path: str) -> None:
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)

    with open(pdf_path, 'rb') as data:
        container_client.upload_blob(name=os.path.basename(pdf_path), data=data, overwrite=True,
                                     content_settings=ContentSettings(content_type='application/pdf'))

    with open(pdf_path, 'rb') as data:
        container_client.upload_blob(name='Frank_Refol_Resume_latest.pdf', data=data, overwrite=True,
                                     content_settings=ContentSettings(content_type='application/pdf'))

def write_github_outputs(pdf_name: str) -> None:
    gha_out = os.environ.get('GITHUB_OUTPUT')
    if gha_out:

        with open(gha_out, 'a') as gh:
            gh.write(f"dated_pdf={pdf_name}\n")
            gh.write("latest_pdf=Frank_Refol_Resume_latest.pdf\n")

def main(argv: Optional[list] = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    parser = argparse.ArgumentParser(description='Generate resume PDF and optionally upload to Azure blob')

    parser.add_argument('--no-upload', action='store_true', help='Skip uploading the PDF to Azure')
    parser.add_argument('--html', default='index.html', help='HTML file to convert')
    parser.add_argument('--out', default=None, help='Output PDF filename (optional)')

    args = parser.parse_args(argv)

    now = datetime.datetime.now()
    date_string = now.strftime('%Y%m%d')

    html_file = args.html
    resume_pdf_file = args.out if args.out else f'Frank_Refol_Resume_{date_string}.pdf'

    try:
        html = read_html(html_file)
        soup = parse_html(html)

        changed = update_last_updated(soup, now)
        if changed:
            write_html(html_file, str(soup))

            print(f'Updated last-updated date in {html_file}')
        else:
            print('No footer/last-updated tag found or updated.')

    except Exception as e:
        print(f'Error updating HTML: {e}')
        return 1

    try:
        generate_pdf(html_file, resume_pdf_file)
        print(f'Generated PDF: {resume_pdf_file}')

    except Exception as e:
        print(f'Error generating PDF: {e}')
        return 1

    no_upload = should_skip_upload(args.no_upload)
    if no_upload:
        print('Skipping upload (no-upload requested).')

        return 0

    conn = os.environ.get('AZURE_STORAGE_CONNECTION_STRING')
    container = os.environ.get('AZURE_STORAGE_CONTAINER')

    if not conn or not container:
        print('AZURE_STORAGE_CONNECTION_STRING or AZURE_STORAGE_CONTAINER not set; skipping upload.')
        return 0

    try:
        upload_to_azure(conn, container, resume_pdf_file)
        print(f"Uploaded {resume_pdf_file} to container {container}")

        if is_github_actions():
            write_github_outputs(resume_pdf_file)
        return 0

    except Exception as e:
        print(f'Error uploading PDF: {e}')
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
import os
import datetime
from azure.storage.blob import BlobServiceClient, ContentSettings
from weasyprint import HTML
from bs4 import BeautifulSoup
import sys

# Get the current date and time
now = datetime.datetime.now()

# Format the date and time as a string
date_string = now.strftime("%Y%m%d")
resume_pdf_file = f'Frank_Refol_Resume_{date_string}.pdf'
html_file = "index.html"  # Resume file
# Skip upload if requested via CLI or environment
# CLI flag: --no-upload
# Env var: SKIP_UPLOAD=1|true|yes
skip_upload = ('--no-upload' in sys.argv) or (os.environ.get('SKIP_UPLOAD', '').lower() in ('1', 'true', 'yes'))

# Detect if running in GitHub Actions
running_in_actions = os.environ.get("GITHUB_ACTIONS", "").lower() == "true"

try:
    # Read the HTML file
    with open(html_file, "r", encoding="utf-8") as file:
        html = file.read()

    # Parse the HTML with BeautifulSoup using an HTML5-aware parser
    # (html5lib avoids libxml2/lxml HTML5 tag warnings and is robust for modern markup)
    soup = BeautifulSoup(html, "html5lib")

    # Find the footer by id (robust regardless of exact tag name or class ordering)
    footer_section = soup.find(id="footer")

    # Selectively modify Last updated date
    if footer_section:
        # Find the <p class="last-updated"> tag within the footer section
        last_updated_tag = footer_section.find("p", class_="last-updated")
        if last_updated_tag:
            new_date = now.strftime("%B %d, %Y")
            new_text = f"Last updated: {new_date}"

            # Update the text content of the tag
            old_text = last_updated_tag.get_text(strip=True)
            html = html.replace(old_text, new_text)
            last_updated_tag.string = new_text

            print(f"Updated last-updated date to: {last_updated_tag.string}")  # Success message
        else:
            print("No <p class='last-updated'> tag found in footer section.")
    else:
        print("Footer section not found.")

    # Write the updated HTML back to the file
    with open(html_file, "w", encoding="utf-8") as file:
        file.write(html)
except Exception as e:
    print(f"An error occurred trying to modify the html resume file: {e}")

try:
    # Convert HTML to PDF
    HTML(html_file).write_pdf(resume_pdf_file)

except Exception as e:
    print(f"An error occurred trying to convert the resume to PDF: {e}")

if skip_upload:
    print('Skipping upload (no-upload option set).')
else:
    connection_string = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
    container_name = os.environ.get("AZURE_STORAGE_CONTAINER")

    if not connection_string or not container_name:
        print('AZURE_STORAGE_CONNECTION_STRING or AZURE_STORAGE_CONTAINER not set; skipping upload.')
    else:
        try:
            # Create a BlobServiceClient
            blob_service_client = BlobServiceClient.from_connection_string(connection_string)

            # Get a client for the container
            container_client = blob_service_client.get_container_client(container_name)

            # Upload the dated PDF
            with open(resume_pdf_file, "rb") as data:
                container_client.upload_blob(
                    name=resume_pdf_file,
                    data=data,
                    overwrite=True,
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

        except Exception as e:
            print(f"An error occurred trying to upload the resume PDF: {e}")

# Set GitHub Actions outputs (if running in GH actions)
if os.environ.get('GITHUB_OUTPUT'):
    with open(os.environ['GITHUB_OUTPUT'], 'a') as gh:
        gh.write(f"dated_pdf={resume_pdf_file}\n")
        gh.write(f"latest_pdf=Frank_Refol_Resume_latest.pdf\n")