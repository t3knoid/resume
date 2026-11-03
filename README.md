# Resume Website

This repository contains the source for my résumé website, built with clean, semantic HTML/CSS and published through GitHub Pages. It also includes tooling to generate **print‑optimized PDFs**, with automated upload to Azure Blob Storage for hosting.

- **Live résumé:** https://resume.refol.us  
- **PDF version:** use the **download** link in the footer of the live résumé.

> The PDF URL is deliberately not linked here. The PDF contains contact details, and any public link to it (including this README) lets search engines find and index it. See [Keeping the PDF out of search engines](#keeping-the-pdf-out-of-search-engines).

The HTML served on the website (`index.html`) is already ATS‑friendly and designed for reliable parsing by applicant‑tracking systems.

---

## Repository Requirements

Use this section as the single source of truth for local prerequisites.

### Required

- **Git** (for clone/commit workflows and hooks)
- **Node.js** (includes `npm` and usually `npx`)
  - Used for HTML validation (`html-validate`) and Lighthouse CLI
- **Python 3** (for PDF/ATS tooling scripts)
- **Python dependencies** from `requirements.txt`

### Optional (feature-specific)

- **Google Chrome/Chromium** for Lighthouse audits (`--chrome-flags="--headless"`)
- **Azure Blob Storage credentials** for upload workflows:
  - `AZURE_STORAGE_CONNECTION_STRING`
  - `AZURE_STORAGE_CONTAINER` (default `$web`)
  - `RESUME_PDF_TOKEN` (optional; secret token added to PDF file names)

### Quick verification

```bash
git --version
node -v
npm -v
npx -v || npm exec --yes html-validate --version
python3 --version
python3 -m pip install -r requirements.txt
```

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

### Download link obfuscation

- **Why:** The footer "download" link in [index.html](index.html) is obfuscated so the direct blob URL doesn't appear in the markup, where crawlers could follow it.
- **How it works:** The link uses a `data-resume` attribute containing the base64-encoded URL and a small inline JS decoder that decodes on click and navigates to the original PDF. The code is in `index.html` near the footer and before `</body>`.
- **Updated automatically:** `htmtopdf.py` rewrites `data-resume` to point at the current "latest" PDF name (which includes `RESUME_PDF_TOKEN` when set), keeping the existing base URL. The workflow commits the change.
- **Generate/update encoded value manually:**

```bash
printf %s 'https://url/to/resume.pdf' | base64
```

- **To apply:** put the base64 string into the `data-resume` attribute (e.g. `data-resume="<base64>"`) and ensure the decoder script is present. Example link markup used here:

```html
<a href="#" id="download-resume" data-resume="<base64>">download</a>
```

- **To revert:** replace the anchor with a direct `href` to the PDF or remove the decoder script.
- **Note:** This is light obfuscation for presentation purposes only — it is not a security mechanism. For stronger concealment or analytics, consider a shortlink, server-side redirect, or signed URL workflow.

---

## PDF Generation & Upload

PDFs are generated from `index.html` using `htmtopdf.py` and uploaded to Azure Blob Storage.

- **Renderer:** WeasyPrint (modern CSS → PDF)  
- **Hosting:** Azure Blob Storage static website (`$web` container)
- **Download behavior:** PDFs are uploaded with `Content-Disposition: attachment; filename="Frank_Refol_Resume.pdf"`, so browsers save the file (with a clean name) instead of opening it inline.
- **robots.txt:** each upload also writes a `robots.txt` (`Disallow: /`) to the root of the static website so crawlers skip the PDFs.

### File names

| File | Without token | With `RESUME_PDF_TOKEN` |
| ---- | ------------- | ----------------------- |
| Dated | `Frank_Refol_Resume_YYYYMMDD.pdf` | `Frank_Refol_Resume_YYYYMMDD_<token>.pdf` |
| Latest | `Frank_Refol_Resume_latest.pdf` | `Frank_Refol_Resume_latest_<token>.pdf` |

### CLI options

| Option             | Description                                                      |
| ------------------ | ---------------------------------------------------------------- |
| `--no-upload`      | Skip Azure upload (local testing)                                |
| `--html <path>`    | Use an alternate HTML input file (default: `index.html`)         |
| `--out <file>`     | Output filename (default: see [File names](#file-names); token not applied) |
| `--suffix <value>` | Add a filename suffix (e.g., `ats`)                              |

### Environment variables

- `SKIP_UPLOAD=1` — same as `--no-upload`  
- `AZURE_STORAGE_CONNECTION_STRING` — required for uploads  
- `AZURE_STORAGE_CONTAINER` — target container (default `$web`)  
- `RESUME_PDF_TOKEN` — optional secret token added to PDF file names so their URLs can't be guessed  

### Recommended local workflow

```powershell
$env:VENV=.venv
python -m venv $env:VENV
& $env:VENV\Scripts\Activate.ps1
pip install -r requirements.txt

python scripts/htmtopdf.py --no-upload
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
python3 scripts/htmtopdf.py
```

- Produces timestamped and "latest" PDFs  
- Updates the footer "last updated" date and the download link in `index.html`  
- Uploads the PDFs and `robots.txt` to Azure Blob Storage  

4. **Make the `$web` container private** (recommended)  
   Azure Portal → Storage Account → Containers → `$web` → Change access level → **Private**.  
   The static website endpoint (`*.web.core.windows.net`) keeps serving files, but the blob endpoint (`*.blob.core.windows.net/$web/...`) stops doing so. That matters because the `robots.txt` above covers only the static website host.

---

## GitHub Actions Workflow

The automated workflow:

- Runs on push to `main` or manual dispatch  
- Generates both timestamped and “latest” PDFs  
- Uploads them, plus `robots.txt`, to Azure Blob Storage  
- Commits the updated `index.html` (last-updated date, download link)  
- Deploys the site to GitHub Pages  

Required secrets:

- `AZURE_STORAGE_CONNECTION_STRING`  
- `AZURE_STORAGE_CONTAINER`  
- `RESUME_PDF_TOKEN` (recommended; without it the PDF names are predictable)

Pipeline flow:

```
index.html → htmtopdf.py → timestamped + latest PDFs → Azure Blob Storage
                         → updated index.html → commit → GitHub Pages
```

---

## Keeping the PDF out of search engines

The PDF contains contact details that aren't shown on the web page, so it should not be indexed. Several layers keep it out:

1. **Unguessable names:** `RESUME_PDF_TOKEN` is added to the file names.
2. **No public links:** the site link is base64-obfuscated, and the URL is not linked from this README.
3. **robots.txt on the PDF host:** uploaded to the static website root on every run. (The `robots.txt` in this repo applies only to the GitHub Pages domain, not to Azure.)
4. **Private `$web` container:** closes the blob endpoint, which robots.txt can't cover (see [Azure Setup](#azure-setup)).

`Content-Disposition: attachment` only affects browsers. It does **not** stop indexing.

### Removing a PDF that is already indexed

1. Generate a token (`python -c "import secrets; print(secrets.token_hex(8))"`) and save it as the `RESUME_PDF_TOKEN` repository secret.
2. Delete the old, predictable blobs **before** pushing, because the pattern would also match the new files:

   ```bash
   az storage blob delete-batch --source '$web' --pattern 'Frank_Refol_Resume_*.pdf' \
     --connection-string "$AZURE_STORAGE_CONNECTION_STRING" --dryrun   # drop --dryrun to delete
   ```

3. Push to `main` so the workflow uploads the new PDFs and updates the link.
4. Once the old URL returns 404, submit it to Google's [Remove Outdated Content](https://search.google.com/search-console/remove-outdated-content) tool.

To rotate the token later, change the secret, delete the old tokened blobs, and push.

---

## Evaluating the Resume Page

Use **Google Lighthouse** to audit performance, accessibility, best practices, and SEO.
See [Repository Requirements](#repository-requirements) for prerequisites.

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

## Pre-Commit HTML Validation

This repository includes a native Git pre-commit hook at `.githooks/pre-commit` that validates `index.html` before each commit.
See [Repository Requirements](#repository-requirements) for prerequisites.

Setup:

```bash
git config core.hooksPath .githooks
chmod +x .githooks/pre-commit
```

Windows (PowerShell):

```powershell
git config core.hooksPath .githooks
```

If you use Git Bash on Windows, you can also run:

```bash
chmod +x .githooks/pre-commit
```

Run the same validation manually:

```bash
npx --yes html-validate index.html
```

If `npx` is unavailable in your environment, use:

```bash
npm exec --yes html-validate index.html
```

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
