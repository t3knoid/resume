
# Resume

This is a very simple resume format using HTML and CSS. You can view [my resume](https://resume.refol.us) in HTML using this technique in Github Pages.

My resume is also available as a PDF generated automatically when it is committed to GitHub as described [below](#automated-resume-pdf-generation--upload).

[![Resume PDF](https://img.shields.io/badge/View%20Resume-PDF-blue?style=flat&logo=adobe)](https://homelabstore1.blob.core.windows.net/$web/Frank_Refol_Resume_latest.pdf)

---

## Formatting

Each work experience is encapsulated in using the following div item.

``` html
<!-- Company name -->
<div class="resume-item">
  <table>
    <tr>
      <td>
        <div class="resume-position">
          Job position
        </div>
      </td>
      <td class="resume-date-worked">
        MMM YYYY-MMM YYYY<br/>
      </td>
    </tr>
    <tr>
      <td colspan="2">
        <div class="resume-company">
          <a href="https://www.companyurl.com/" target="_blank">Some Company Name</a> | Anytown, USA
        </div>
      </td>
    </tr>
    <tr>
      <td colspan="2">
        <div class="resume-company-description">
          Short description of the company.
        </div>
      </td>
    </tr>
    <tr>
      <td colspan="2">
        <ul>
          <li><div class="highlight">Responsibility 1.</div></li>
          <li><div class="highlight">Responsibility 2.</div></li>
          <li><div class="highlight">Responsibility 3.</div></li>
        </ul>
      </td>
    </tr>
  </table>
</div>
```

---

## Static Resume PDF Link in Footer

The HTML contains a static link to a PDF format of the resume. The download link is located at the footer of the document. It links to a URL in an Azure blob storage containing the PDF.

---

## Automated Resume PDF Generation & Upload

This repository includes a Python script, [`htmtopdf.py`](htmtopdf.py), which automates generating a PDF version of the HTML resume and uploading it to Azure Blob Storage. The script can be executed **manually** or automatically via GitHub Actions.

### **Local / Debug options**

---

`htmtopdf.py` provides a few options and environment variables useful when running locally or debugging:

- **CLI options:**
  - `--no-upload` : skip uploading the generated PDF (local testing)
  - `--html <path>` : specify an alternate HTML file to convert (default: `index.html`)
  - `--out <file>` : set the output PDF filename (default: `Frank_Refol_Resume_YYYYMMDD.pdf`)
- **Environment variables:**
  - `SKIP_UPLOAD=1` or `SKIP_UPLOAD=true` : same effect as `--no-upload`
  - `AZURE_STORAGE_CONNECTION_STRING` and `AZURE_STORAGE_CONTAINER` : required to perform uploads
  - When running in GitHub Actions the script will write outputs to the `GITHUB_OUTPUT` file if available.

Recommended local debug workflow:

1. Create and activate a virtual environment and install dependencies:

```powershell
$env:VENV=.venv
python -m venv $env:VENV
& $env:VENV\Scripts\Activate.ps1
pip install -r requirements.txt
```

1. Run the script without uploading to verify footer update and PDF generation:

```powershell
python htmtopdf.py --no-upload
```

1. Verify results:

- `index.html` should have an updated `Last updated:` date in the footer (script prints a message).
- A timestamped PDF (e.g. `Frank_Refol_Resume_20260107.pdf`) should be created in the repo root.

1. If you want to test upload, set the Azure env vars and run without `--no-upload` (or unset `SKIP_UPLOAD`):

```powershell
$env:AZURE_STORAGE_CONNECTION_STRING='...'
$env:AZURE_STORAGE_CONTAINER='$web'
python htmtopdf.py
```

Troubleshooting notes:

- If the script attempts to upload but you don't want to, pass `--no-upload` or set `SKIP_UPLOAD`.
- If upload fails, confirm the connection string and container are correct; the script prints any upload errors.
- For CI, ensure `AZURE_STORAGE_CONNECTION_STRING` and `AZURE_STORAGE_CONTAINER` are stored as repository secrets.

---

### **1. Get Azure Storage Credentials**

To upload the PDF, you need:

1. **Azure Storage account connection string**

   - Go to the [Azure Portal](https://portal.azure.com/) → your **Storage Account** → **Security + networking → Access keys**
   - Click **Show keys** and copy the **Connection string**

2. **Container name**

   - For static website hosting, use `$web`
   - Otherwise, specify the container where you want the PDF uploaded

---

### **2. Manual Execution**

1. **Install dependencies**:

```bash
pip install -r requirements.txt
```

1. **Set Azure credentials as environment variables**:

**Linux / macOS:**

```bash
export AZURE_STORAGE_CONNECTION_STRING='your_connection_string_here'
export AZURE_STORAGE_CONTAINER='$web'
```

**Windows (PowerShell):**

```powershell
$env:AZURE_STORAGE_CONNECTION_STRING='your_connection_string_here'
$env:AZURE_STORAGE_CONTAINER="$web"
```

1. **Run the script**:

```bash
python3 htmtopdf.py
```

- The script performs:

  - Converts `index.html` to a **timestamped PDF** (e.g., `Frank_Refol_Resume_20251209.pdf`)
  - Uploads the PDF to Azure Blob Storage
  - Uploads a  `Frank_Refol_Resume_Latest.pdf` as well

> Using timestamped PDF filenames ensures that every generated version is unique and provides clear versioning history in Azure.

---

### **3. Automated Execution via GitHub Actions**

- A GitHub Actions workflow can automate the process on every push to the `main` branch or via manual trigger.
- Store the Azure credentials as **GitHub Secrets**:

  - `AZURE_STORAGE_CONNECTION_STRING` → your connection string
  - `AZURE_STORAGE_CONTAINER` → your container name (`$web`)

---

### **4. Workflow Overview**

```text
       +-----------------+
       |  index.html     |
       +-----------------+
                |
                v
       +-----------------+
       |  htmtopdf.py    |
       | - Update footer |
       | - Generate PDF  |
       | - Timestamped   |
       |   PDF filename  |
       +-----------------+
                |
                v
       +-----------------+
       | Azure Blob      |
       | Storage ($web)  |
       +-----------------+
                ^
                |
        GitHub Actions (optional)
         - Pulls changes
         - Sets secrets
         - Runs script automatically
```

- The **timestamped naming convention** ensures each resume PDF uploaded to Azure has a unique URL while preserving historical versions.
- The footer URL in the HTML is automatically updated to point to the latest version.

---

## Evaluating the page with Lighthouse

You can use Google's Lighthouse CLI to audit Performance, Accessibility, Best Practices and SEO for the local copy of this site.

Prerequisites:

- Node.js and npm (Lighthouse runs via npm / npx)
- A recent Google Chrome installation (Lighthouse uses Chrome to run audits)
- A local web server to serve the files (for example, Python's `http.server`)

Quick steps:

1. Start a local server from the repository root (example using Python):

```bash
python -m http.server 8000
```

1. Run Lighthouse from another terminal (example CLI):

```bash
npx -y lighthouse http://localhost:8000/index.html --only-categories=performance,accessibility,best-practices,seo --output html --output-path lighthouse-report.html --chrome-flags="--headless"
```

1. Open the generated report [lighthouse-report.html](lighthouse-report.html) in a browser to review results and suggestions.

Notes:

- Run the web server in a separate terminal from the Lighthouse command to avoid conflicts.
- If you prefer a GUI, Chrome Developers Tools (F12) contains Lighthouse under the "Lighthouse" panel.
- For CI runs, install Chrome on your runner and execute the same `npx lighthouse` command. GitHub Actions runners already include Chrome and Node on hosted images.
