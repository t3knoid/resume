from html import parser
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
    p = footer.find('span', class_='last-updated')
    if not p:
        return False
    new_text = f"Last updated: {now.strftime('%B %d, %Y')}"
    p.string = new_text
    return True


def generate_pdf(html_path: str, pdf_path: str) -> None:
    HTML(html_path).write_pdf(pdf_path)


def upload_to_azure(connection_string: str, container_name: str, pdf_path: str, upload_latest: bool = True, latest_file_path: str = None, latest_blob_name: str = None) -> None:
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)
    # upload dated PDF
    with open(pdf_path, 'rb') as data:
        container_client.upload_blob(name=os.path.basename(pdf_path), data=data, overwrite=True,
                                     content_settings=ContentSettings(content_type='application/pdf'))
    # upload latest if requested (using a separate latest file)
    if upload_latest and latest_file_path and latest_blob_name:
        with open(latest_file_path, 'rb') as data:
            container_client.upload_blob(name=latest_blob_name, data=data, overwrite=True,
                                         content_settings=ContentSettings(content_type='application/pdf'))


def write_github_outputs(pdf_name: str, latest_uploaded: bool = True, latest_name: str = None) -> None:
    gha_out = os.environ.get('GITHUB_OUTPUT')
    if gha_out:
        with open(gha_out, 'a') as gh:
            gh.write(f"dated_pdf={pdf_name}\n")
            if latest_uploaded and latest_name:
                gh.write(f"latest_pdf={latest_name}\n")


def parse_args():
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
   
    return parser.parse_args()

def main(argv: Optional[list] = None) -> int:
    args = parse_args()

    now = datetime.datetime.now()
    date_string = now.strftime('%Y%m%d')
    html_file = args.html
    suffix = args.suffix or 'Resume'

    # build filename: Frank_Refol_{suffix}_{date_string}.pdf
    def ensure_pdf_extension(name: str) -> str:
        base, ext = os.path.splitext(name)
        return name if ext.lower() == '.pdf' else f"{name}.pdf"

    if args.out:
        # ensure user-provided name has .pdf extension
        resume_pdf_file = ensure_pdf_extension(args.out)
        base = os.path.splitext(os.path.basename(resume_pdf_file))[0]
        latest_pdf_file = f"{base}_latest.pdf"
    else:
        resume_pdf_file = f"Frank_Refol_{suffix}_{date_string}.pdf"
        # Use the configured suffix for the "latest" filename as well
        latest_pdf_file = f"Frank_Refol_{suffix}_latest.pdf"

    latest_blob_name = os.path.basename(latest_pdf_file)
    upload_latest = True

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
        # If requested, also generate a "latest" PDF with the ats_latest suffix
        if upload_latest and latest_pdf_file:
            generate_pdf(html_file, latest_pdf_file)
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
        upload_to_azure(conn, container, resume_pdf_file, upload_latest=upload_latest, latest_file_path=latest_pdf_file, latest_blob_name=latest_blob_name)
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