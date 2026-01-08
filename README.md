# HTML & PDF Resume Guide

This repository provides a simple **HTML/CSS resume** with automatic **PDF generation** and hosting on Azure Blob Storage.  

- View the HTML version on [GitHub Pages](https://resume.refol.us).  
- Download the latest PDF version:  
[![Resume PDF](https://img.shields.io/badge/View%20Resume-PDF-blue?style=flat&logo=adobe)](https://homelabstore1.blob.core.windows.net/$web/Frank_Refol_Resume_latest.pdf)  
- An **ATS-friendly PDF** is also available (`Frank_Refol_ats_latest.pdf`) for applicant-tracking systems.

---

## ATS-Friendly Resume

**ATS** stands for **Applicant Tracking System**. These are software tools used by many employers to automatically scan, parse, and rank resumes based on keywords, formatting, and experience.  

Standard PDFs or HTML resumes with complex formatting may not be read correctly by ATS software, which can result in your application being overlooked.  

This repository provides an **ATS-friendly PDF** (`Frank_Refol_ats_latest.pdf`) that preserves all content in a plain format optimized for these systems, ensuring your resume is correctly parsed.

> **Note:** The ATS-friendly resume HTML is automatically generated during the GitHub workflow using the script [`scripts/html_to_ats_resume.py`](scripts/html_to_ats_resume.py).  
> This script reads the main `index.html` and produces a simplified, plain HTML version by:
>
> - Extracting contact info, professional summary, work experience, core skills, and education  
> - Converting complex formatting (tables, nested divs) into standard headings, paragraphs, and lists  
> - Producing a clean HTML file that can be rendered or converted to PDF for ATS compatibility  

You can also run the script manually:

```bash
python scripts/html_to_ats_resume.py -i index.html -o resume_ats.html
```

- `-i` specifies the input HTML (default: `index.html`)
- `-o` specifies the output HTML (default: `resume_ats.html`)
- The generated HTML is optimized for ATS parsing and can be further converted to PDF if needed.

---

## Resume HTML Structure

Each work experience uses the following structure:

```html
<div class="resume-item">
  <table>
    <tr>
      <td class="resume-position">Job position</td>
      <td class="resume-date-worked">MMM YYYY-MMM YYYY</td>
    </tr>
    <tr>
      <td colspan="2">
        <span class="resume-company">
          <a href="https://www.companyurl.com/" target="_blank">Some Company Name</a>
        </span> | Anytown, USA
      </td>
    </tr>
    <tr>
      <td colspan="2">
        <span class="resume-company-description">Short description of the company.</span>
      </td>
    </tr>
    <tr>
      <td colspan="2">
        <div class="resume-responsibilities">
          <ul>
            <li><span class="highlight">Responsibility 1.</span></li>
            <li><span class="highlight">Responsibility 2.</span></li>
            <li><span class="highlight">Responsibility 3.</span></li>
          </ul>
        </div>
      </td>
    </tr>
  </table>
</div>
````

### CSS

- **On-screen layout:** `assets/css/style.css`
- **PDF-specific formatting:** `assets/css/print.css` (used by `htmtopdf.py`)

---

## PDF Generation & Upload

PDFs are generated automatically from `index.html` using [`htmtopdf.py`](htmtopdf.py) and uploaded to **Azure Blob Storage**.

- **Library:** [WeasyPrint](https://weasyprint.org) renders modern CSS to PDF.
- **Hosting:** Azure Blob Storage (`$web` container recommended for static website hosting).

### Local / Debug Options

**CLI options:**

| Option             | Description                                                      |
| ------------------ | ---------------------------------------------------------------- |
| `--no-upload`      | Skip uploading PDF (for local testing)                           |
| `--html <path>`    | Alternate HTML input file (default: `index.html`)                |
| `--out <file>`     | Output PDF filename (default: `Frank_Refol_Resume_YYYYMMDD.pdf`) |
| `--suffix <value>` | Filename suffix (use `ats` for ATS-friendly PDF)                 |

**Environment variables:**

- `SKIP_UPLOAD=1` → same as `--no-upload`
- `AZURE_STORAGE_CONNECTION_STRING` → required for uploads
- `AZURE_STORAGE_CONTAINER` → target container (default `$web`)

**Recommended local workflow:**

```powershell
$env:VENV=.venv
python -m venv $env:VENV
& $env:VENV\Scripts\Activate.ps1
pip install -r requirements.txt

python htmtopdf.py --no-upload
```

- Verify updated footer and timestamped PDF (e.g., `Frank_Refol_Resume_20260107.pdf`)
- To test upload, set Azure env vars and run without `--no-upload`

---

### Azure Setup

1. **Get credentials:**

   - Connection string: [Azure Portal → Storage Account → Access keys → Show keys](https://portal.azure.com/)
   - Container: `$web` for static website

2. **Set environment variables:**

**Linux/macOS:**

```bash
export AZURE_STORAGE_CONNECTION_STRING='your_connection_string_here'
export AZURE_STORAGE_CONTAINER='$web'
```

**Windows (PowerShell):**

```powershell
$env:AZURE_STORAGE_CONNECTION_STRING='your_connection_string_here'
$env:AZURE_STORAGE_CONTAINER="$web"
```

3. **Run script:**

```bash
python3 htmtopdf.py
```

- Generates timestamped PDF for version history
- Updates HTML footer with latest PDF URL
- Uploads PDFs to Azure Blob Storage

---

### Automated GitHub Actions Workflow

- Runs on push to `main` or manual trigger
- Uses **GitHub Secrets** for Azure credentials:

  - `AZURE_STORAGE_CONNECTION_STRING`
  - `AZURE_STORAGE_CONTAINER`

- Workflow:

```text
index.html --> htmtopdf.py --> Timestamped PDF + Latest PDF --> Azure Blob Storage
```

---

## Evaluating Resume Page

Use **Google Lighthouse** to audit Performance, Accessibility, Best Practices, and SEO.

**Prerequisites:** Node.js, npm, Chrome, and a local server.

```bash
# Serve files locally
python -m http.server 8000

# Run Lighthouse audit
npx -y lighthouse http://localhost:8000/index.html \
  --only-categories=performance,accessibility,best-practices,seo \
  --output html \
  --output-path lighthouse-report.html \
  --chrome-flags="--headless"
```

- Open `lighthouse-report.html` in a browser to review suggestions
- Can also run via Chrome DevTools GUI (Lighthouse panel) or in CI with GitHub Actions
