
# Resume
This is a very simple resume format using HTML and CSS. You can view [my resume](https://t3knoid.github.io/resume/) in HTML using this technique in Github Pages.

My resume is also available as a PDF generated automatically when it is committed to GitHub as described [below](#automated-resume-pdf-generation--upload).

[![Resume PDF](https://img.shields.io/badge/View%20Resume-PDF-blue?style=flat&logo=adobe)](https://homelabstore1.blob.core.windows.net/$web/Frank_Refol_Resume_latest.pdf)

---

## Formatting

Each work experience is encapsulated in using the following div item.

```
<!-- Company name -->
<div class="resume-item">
	<table>
		<tr>
			<td>
				<div class="resume-position">
					Job position
				</div>
				<div class="resume-company">
					<a href="https://www.companyurl.com/" target="_blank">Some Company Name</a> | Anytown, USA
				</div>
				<div class="resume-company-description">
					Short description of the company.
				</div> 
			</td>
			<td class="resume-dateworked">
				MMM YYYY-MMM YYYY<br/>
			</td>
		</tr>
		<tr>
			<td colspan="2">
				<ul>
					<li>Responsibility 1.</li>
					<li>Responsibility 2.</li>
					<li>Responsibility 3.</li>
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

---

### **1. Get Azure Storage Credentials**

To upload the PDF, you need:

1. **Azure Storage account connection string**

   * Go to the [Azure Portal](https://portal.azure.com/) → your **Storage Account** → **Security + networking → Access keys**
   * Click **Show keys** and copy the **Connection string**

2. **Container name**

   * For static website hosting, use `$web`
   * Otherwise, specify the container where you want the PDF uploaded

---

### **2. Manual Execution**

1. **Install dependencies**:

```bash
pip install -r requirements.txt
```

2. **Set Azure credentials as environment variables**:

**Linux / macOS:**

```bash
export AZURE_STORAGE_CONNECTION_STRING="your_connection_string_here"
export AZURE_STORAGE_CONTAINER="$web"
```

**Windows (PowerShell):**

```powershell
$env:AZURE_STORAGE_CONNECTION_STRING="your_connection_string_here"
$env:AZURE_STORAGE_CONTAINER="$web"
```

3. **Run the script**:

```bash
python3 htmtopdf.py
```

* The script performs:

  * Converts `index.html` to a **timestamped PDF** (e.g., `Frank_Refol_Resume_20251209.pdf`)
  * Uploads the PDF to Azure Blob Storage
  * Uploads a  `Frank_Refol_Resume_Latest.pdf` as well

> Using timestamped PDF filenames ensures that every generated version is unique and provides clear versioning history in Azure.

---

### **3. Automated Execution via GitHub Actions**

* A GitHub Actions workflow can automate the process on every push to the `main` branch or via manual trigger.
* Store the Azure credentials as **GitHub Secrets**:

  * `AZURE_STORAGE_CONNECTION_STRING` → your connection string
  * `AZURE_STORAGE_CONTAINER` → your container name (`$web`)

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

* The **timestamped naming convention** ensures each resume PDF uploaded to Azure has a unique URL while preserving historical versions.
* The footer URL in the HTML is automatically updated to point to the latest version.
