# Resume Website

This repository contains the source for my résumé website, built with clean, semantic HTML/CSS and published through GitHub Pages. It also includes tooling to generate **print‑optimized PDFs**, with automated upload to Azure Blob Storage for hosting.

- **Live résumé:** https://resume.refol.us  
- Download the latest PDF version:  
[![Resume PDF](https://img.shields.io/badge/View%20Resume-PDF-blue?style=flat&logo=adobe)](https://homelabstore1.blob.core.windows.net/$web/Frank_Refol_Resume_latest.pdf)  

The HTML served on the website (`index.html`) is already ATS‑friendly and designed for reliable parsing by applicant‑tracking systems.

---

## Resume HTML Structure

The résumé is written using semantic HTML to ensure clarity, accessibility, and ATS compatibility. Each work experience entry follows a consistent structure that includes:

- A role title  
- Company, location, and dates  
- A short company description  
- A list of responsibilities  

Example:

```html
<article class="resume-item" id="tcdi">
  <header>
    <h4 class="resume-position">Technical Applications Engineer</h4>
    <div class="resume-meta">
      <div>
        <span class="resume-company"><a href="https://tcdi.example/" target="_blank" rel="noopener">Technology Concepts &amp; Design, Inc.</a></span>
        | <span class="resume-company-location">Purchase, NY</span>
        | <time class="resume-date-worked" datetime="2022-07">Jul 2022</time> – <time class="resume-date-worked" datetime="2024-08">Aug 2024</time>
      </div>
      <div class="resume-company-description">TCDI is a legal services and cybersecurity solutions company.</div>
    </div>
  </header>
  <div class="resume-responsibilities">
    <ul>
      <li><strong>Developed Ansible scripts</strong> to automate management of network inventories and deployments.</li>
      <li><strong>Maintained monitoring tools</strong> across hybrid environments (Windows, Linux).</li>
      <li><strong>Collaborated with cross-functional teams</strong> to deliver secure infrastructure.</li>
    </ul>
  </div>
</article>
```

### Stylesheets

- **Screen layout:** `assets/css/style.css`  
- **Print/PDF layout:** `assets/css/print.css` (used by `htmtopdf.py`)

---

## PDF Generation & Upload

PDFs are generated from `index.html` using `htmtopdf.py` and uploaded to Azure Blob Storage.

- **Renderer:** WeasyPrint (modern CSS → PDF)  
- **Hosting:** Azure Blob Storage (`$web` container recommended)

### CLI options

| Option             | Description                                                      |
| ------------------ | ---------------------------------------------------------------- |
| `--no-upload`      | Skip Azure upload (local testing)                                |
| `--html <path>`    | Use an alternate HTML input file (default: `index.html`)         |
| `--out <file>`     | Output filename (default: `Frank_Refol_Resume_YYYYMMDD.pdf`)     |
| `--suffix <value>` | Add a filename suffix (e.g., `ats`)                              |

### Environment variables

- `SKIP_UPLOAD=1` — same as `--no-upload`  
- `AZURE_STORAGE_CONNECTION_STRING` — required for uploads  
- `AZURE_STORAGE_CONTAINER` — target container (default `$web`)  

### Recommended local workflow

```powershell
$env:VENV=.venv
python -m venv $env:VENV
& $env:VENV\Scripts\Activate.ps1
pip install -r requirements.txt

python htmtopdf.py --no-upload
```

- Confirm the timestamped PDF output  
- Remove `--no-upload` to test Azure upload  

---

## Azure Setup

1. **Retrieve credentials**  
   Azure Portal → Storage Account → Access Keys → Show Keys  
   Container: `$web`

2. **Set environment variables**

**Linux/macOS:**

```bash
export AZURE_STORAGE_CONNECTION_STRING='your_connection_string_here'
export AZURE_STORAGE_CONTAINER='$web'
```

**Windows PowerShell:**

```powershell
$env:AZURE_STORAGE_CONNECTION_STRING='your_connection_string_here'
$env:AZURE_STORAGE_CONTAINER="$web"
```

3. **Generate and upload**

```bash
python3 htmtopdf.py
```

- Produces timestamped PDFs  
- Updates the HTML footer with the latest PDF URL  
- Uploads PDFs to Azure Blob Storage  

---

## GitHub Actions Workflow

The automated workflow:

- Runs on push to `main` or manual dispatch  
- Generates both timestamped and “latest” PDFs  
- Uploads them to Azure Blob Storage  

Required secrets:

- `AZURE_STORAGE_CONNECTION_STRING`  
- `AZURE_STORAGE_CONTAINER`  

Pipeline flow:

```
index.html → htmtopdf.py → timestamped + latest PDFs → Azure Blob Storage
```

---

## Evaluating the Resume Page

Use **Google Lighthouse** to audit performance, accessibility, best practices, and SEO. This requires installation of Chromium and Node.js.

**`npx` is bundled with Node.js**.  

```bash
brew update
brew install node
```

**Chromium**
```bash
rew install --cask google-chrome
```

### Running a Local audit

Execute the following in a terminal to start a web server serving up the Resume website.

```bash
python -m http.server 8000
```

In a separate terminal, execute lighthouse.

```bash
npx -y lighthouse http://localhost:8000/index.html \
  --only-categories=performance,accessibility,best-practices,seo \
  --output html \
  --output-path lighthouse-report.html \
  --chrome-flags="--headless"
```

Open `lighthouse-report.html` to review results.

---

## ATS‑Friendly Resume (Optional)

The main HTML résumé is already ATS‑friendly.  
However, some systems prefer extremely plain formatting. For those cases, the repository includes an **optional ATS‑friendly HTML and PDF generator**.

### What the ATS generator does

The script `scripts/html_to_ats_resume.py` can generate a simplified HTML version by:

- Extracting contact info, summary, work experience, skills, and education  
- Converting tables and nested layout elements into plain headings, paragraphs, and lists  
- Producing a minimal HTML file suitable for conversion into a plain PDF

This step is **optional** and not used by the live website.

### Manual usage

```bash
python scripts/html_to_ats_resume.py -i index.html -o resume_ats.html
```

- `-i` input HTML (default: `index.html`)  
- `-o` output HTML (default: `resume_ats.html`)  
