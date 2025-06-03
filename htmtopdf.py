import os
from weasyprint import HTML

# Convert HTML to PDF
HTML('https://t3knoid.github.io/resume/index.html').write_pdf('Frank_Refol_Resume.pdf') 