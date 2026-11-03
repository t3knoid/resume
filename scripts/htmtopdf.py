from html import parser
import os
import sys
import base64
import posixpath
import copy
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
    p = footer.find('div', class_='last-updated')
    if not p:
        return False
    new_text = f"Last updated: {now.strftime('%B %d, %Y')}"
    p.string = new_text
    return True


def update_download_link(soup: BeautifulSoup, blob_name: str) -> bool:
    """Point the obfuscated download link at blob_name, keeping its base URL."""
    link = soup.find(id='download-resume')
    if not link or not link.get('data-resume'):
        return False
    current = base64.b64decode(link['data-resume']).decode('utf-8')
    new_url = posixpath.join(posixpath.dirname(current), blob_name)
    if new_url == current:
        return False
    link['data-resume'] = base64.b64encode(new_url.encode('utf-8')).decode('ascii')
    return True


def contact_from_env() -> dict:
    """Private contact details for the PDF, kept out of the public index.html."""
    return {
        'email': os.environ.get('RESUME_EMAIL', '').strip(),
        'phone': os.environ.get('RESUME_PHONE', '').strip(),
    }


def inject_contact(soup: BeautifulSoup, contact: dict) -> BeautifulSoup:
    """Return a copy of soup with email/phone added to the contact block."""
    pdf_soup = copy.copy(soup)
    address = pdf_soup.find('address', class_='contact-info')
    if not address:
        return pdf_soup
    for cls in ('email', 'phone'):
        if contact.get(cls) and not address.find(class_=cls):
            div = pdf_soup.new_tag('div', attrs={'class': cls})
            div.string = contact[cls]
            address.append(div)
    return pdf_soup


def generate_pdf(html_path: str, pdf_path: str, html_string: Optional[str] = None) -> None:
    if html_string is None:
        HTML(html_path).write_pdf(pdf_path)
    else:
        # base_url keeps relative links (assets/css/print.css) resolving as they would from the file
        base_url = os.path.dirname(os.path.abspath(html_path)) + os.sep
        HTML(string=html_string, base_url=base_url).write_pdf(pdf_path)


# Served at the root of the Azure static website so crawlers skip the PDFs.
AZURE_ROBOTS_TXT = "User-agent: *\nDisallow: /\n"


def pdf_content_settings(download_name: str) -> ContentSettings:
    # Make browsers save the file (with a clean name) instead of opening it inline.
    return ContentSettings(content_type='application/pdf',
                           content_disposition=f'attachment; filename="{download_name}"')


def upload_to_azure(connection_string: str, container_name: str, pdf_path: str, upload_latest: bool = True, latest_file_path: str = None, latest_blob_name: str = None, download_name: str = 'Resume.pdf') -> None:
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)
    # robots.txt must live on the same host as the PDFs for crawlers to honor it
    container_client.upload_blob(name='robots.txt', data=AZURE_ROBOTS_TXT.encode('utf-8'), overwrite=True,
                                 content_settings=ContentSettings(content_type='text/plain'))
    # upload dated PDF
    with open(pdf_path, 'rb') as data:
        container_client.upload_blob(name=os.path.basename(pdf_path), data=data, overwrite=True,
                                     content_settings=pdf_content_settings(download_name))
    # upload latest if requested (using a separate latest file)
    if upload_latest and latest_file_path and latest_blob_name:
        with open(latest_file_path, 'rb') as data:
            container_client.upload_blob(name=latest_blob_name, data=data, overwrite=True,
                                         content_settings=pdf_content_settings(download_name))


def write_github_outputs(pdf_name: str, latest_uploaded: bool = True, latest_name: str = None) -> None:
    gha_out = os.environ.get('GITHUB_OUTPUT')
    if gha_out:
        with open(gha_out, 'a') as gh:
            gh.write(f"dated_pdf={pdf_name}\n")
            if latest_uploaded and latest_name:
                gh.write(f"latest_pdf={latest_name}\n")


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description='Generate resume PDF and optionally upload to Azure blob',add_help=True)

    parser.add_argument(
        '--no-upload', 
        action='store_true', 
        help='Skip uploading the PDF to Azure')
    parser.add_argument(
        '--html', 
        default='index.html', 
        help='HTML file to convert')
    parser.add_argument(
        '--out', default=None, 
        help='Output PDF filename (optional)')
    parser.add_argument(
        '--suffix', 
        default='Resume', 
        help="Suffix for generated filename (default: 'Resume')")
   
    return parser.parse_args(argv)

def main(argv: Optional[list] = None) -> int:
    args = parse_args(argv)

    now = datetime.datetime.now()
    date_string = now.strftime('%Y%m%d')
    html_file = args.html
    suffix = args.suffix or 'Resume'

    # build filename: Frank_Refol_{suffix}_{date_string}.pdf
    def ensure_pdf_extension(name: str) -> str:
        base, ext = os.path.splitext(name)
        return name if ext.lower() == '.pdf' else f"{name}.pdf"

    # A secret token in the blob names keeps the PDF URLs unguessable.
    # Set RESUME_PDF_TOKEN (a GitHub secret) to enable it.
    token = os.environ.get('RESUME_PDF_TOKEN', '').strip()
    token_part = f"_{token}" if token else ''
    download_name = f"Frank_Refol_{suffix}.pdf"

    if args.out:
        # ensure user-provided name has .pdf extension
        resume_pdf_file = ensure_pdf_extension(args.out)
        base = os.path.splitext(os.path.basename(resume_pdf_file))[0]
        latest_pdf_file = f"{base}_latest.pdf"
    else:
        resume_pdf_file = f"Frank_Refol_{suffix}_{date_string}{token_part}.pdf"
        # Use the configured suffix for the "latest" filename as well
        latest_pdf_file = f"Frank_Refol_{suffix}_latest{token_part}.pdf"

    latest_blob_name = os.path.basename(latest_pdf_file)
    upload_latest = True

    try:
        html = read_html(html_file)
        soup = parse_html(html)
        changed = update_last_updated(soup, now)
        if changed:
            print(f'Updated last-updated date in {html_file}')
        else:
            print('No footer/last-updated tag found or updated.')
        if update_download_link(soup, latest_blob_name):
            changed = True
            print(f'Pointed download link at {latest_blob_name}')
        if changed:
            write_html(html_file, str(soup))
        # Contact details go only into the PDF; index.html is never written with them.
        contact = contact_from_env()
        missing = [k for k, v in contact.items() if not v]
        if missing:
            print(f"Warning: RESUME_{'/RESUME_'.join(m.upper() for m in missing)} not set; PDF will omit it.")
        pdf_html = str(inject_contact(soup, contact))
    except Exception as e:
        print(f'Error updating HTML: {e}')
        return 1

    try:
        generate_pdf(html_file, resume_pdf_file, pdf_html)
        print(f'Generated PDF: {resume_pdf_file}')
        # If requested, also generate a "latest" PDF with the ats_latest suffix
        if upload_latest and latest_pdf_file:
            generate_pdf(html_file, latest_pdf_file, pdf_html)
            print(f'Generated latest PDF: {latest_pdf_file}')
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
        upload_to_azure(conn, container, resume_pdf_file, upload_latest=upload_latest, latest_file_path=latest_pdf_file, latest_blob_name=latest_blob_name, download_name=download_name)
        print(f"Uploaded {resume_pdf_file} to container {container}")
        if upload_latest:
            print(f"Uploaded latest as {latest_blob_name}")
        if is_github_actions():
            write_github_outputs(resume_pdf_file, latest_uploaded=upload_latest, latest_name=latest_blob_name)
        return 0
    except Exception as e:
        print(f'Error uploading PDF: {e}')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())