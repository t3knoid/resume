# Resume
This is a very simple resume format using HTML and CSS. You can view [my resume](https://t3knoid.github.io/resume/) using this technique in Github Pages. 

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

## Azure Blob

The HTML contains a static link to a PDF format of the resume. The download link is located at the footer of the document. It links to a URL in an Azure blob storage containing the PDF.

## Automated Deploy

In order to automate the changes and upload the PDF to Azure, I've written this [Python script](https://github.com/t3knoid/resume/blob/main/htmtopdf.py) that modifies the HTML with the updated URL to the PDF file in Azure, generate the PDF, and uploads the PDF to Azure. 

Run the script using the following commands:

```bash
pip install requirements.txt
python3 htmtopdf.py
```