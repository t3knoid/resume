import argparse
from bs4 import BeautifulSoup
import re

DEFAULT_INPUT = "index.html"
DEFAULT_OUTPUT = "resume_ats.html"


def clean_text(text):
    return re.sub(r"\s+", " ", text.strip())


def extract_list_items(section):
    items = []
    for li in section.find_all("li"):
        items.append(clean_text(li.get_text()))
    return items


def parse_args():
    parser = argparse.ArgumentParser(description="Generate ATS-friendly resume HTML.", add_help=True)
    parser.add_argument(
        "-i",
        "--input",
        default=DEFAULT_INPUT,
        help=f"Input HTML file (default: {DEFAULT_INPUT})",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=DEFAULT_OUTPUT,
        help=f"Output HTML file (default: {DEFAULT_OUTPUT})",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    INPUT_FILE = args.input
    OUTPUT_FILE = args.output

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    ats = BeautifulSoup("<!DOCTYPE html><html><head></head><body></body></html>", "html.parser")

    # ----- HEAD -----
    head = ats.head
    head.append(ats.new_tag("meta", charset="utf-8"))
    title = ats.new_tag("title")
    title.string = "Francis Refol – IT Automation Engineer / DevOps"
    head.append(title)

    # ----- BODY -----
    body = ats.body

    # ----- HEADER / CONTACT -----
    header = ats.new_tag("header")
    name = soup.select_one(".name")
    title_role = soup.select_one(".title")
    email = soup.select_one(".email")
    phone = soup.select_one(".phone")
    url = soup.select_one(".url a")

    h1 = ats.new_tag("h1")
    h1.string = clean_text(name.get_text())
    header.append(h1)

    p = ats.new_tag("p")
    p.string = (
        f"{clean_text(title_role.get_text())}\n"
        f"Email: {clean_text(email.get_text())} | "
        f"Phone: {clean_text(phone.get_text())}\n"
        f"Portfolio: {url['href']}"
    )
    header.append(p)
    body.append(header)

    # ----- PROFESSIONAL SUMMARY -----
    summary_section = soup.select_one("#resume-summary .summary")
    if summary_section:
        sec = ats.new_tag("section")
        h2 = ats.new_tag("h2")
        h2.string = "Professional Summary"
        sec.append(h2)

        p = ats.new_tag("p")
        p.string = clean_text(summary_section.get_text())
        sec.append(p)
        body.append(sec)

    # ----- WORK EXPERIENCE -----
    work_section = ats.new_tag("section")
    h2 = ats.new_tag("h2")
    h2.string = "Work Experience"
    work_section.append(h2)

    for item in soup.select(".resume-item"):
        position = item.select_one(".resume-position")
        date = item.select_one(".resume-date-worked")
        company = item.select_one(".resume-company")
        desc = item.select_one(".resume-company-description")
        responsibilities = item.select_one(".resume-responsibilities")

        if not position:
            continue

        h3 = ats.new_tag("h3")
        h3.string = clean_text(position.get_text())
        work_section.append(h3)

        p = ats.new_tag("p")
        meta = []
        if company:
            meta.append(clean_text(company.get_text()))
        if date:
            meta.append(clean_text(date.get_text()))
        p.string = " – ".join(meta)
        work_section.append(p)

        if desc:
            d = ats.new_tag("p")
            d.string = clean_text(desc.get_text())
            work_section.append(d)

        if responsibilities:
            ul = ats.new_tag("ul")
            for li in extract_list_items(responsibilities):
                li_tag = ats.new_tag("li")
                li_tag.string = li
                ul.append(li_tag)
            work_section.append(ul)

    body.append(work_section)

    # ----- CORE SKILLS -----
    skills_section = soup.select_one("#core-skills")
    if skills_section:
        sec = ats.new_tag("section")
        h2 = ats.new_tag("h2")
        h2.string = "Core Skills"
        sec.append(h2)

        ul = ats.new_tag("ul")
        for li in extract_list_items(skills_section):
            li_tag = ats.new_tag("li")
            li_tag.string = li
            ul.append(li_tag)
        sec.append(ul)
        body.append(sec)

    # ----- EDUCATION -----
    education_section = soup.select_one("#education")
    if education_section:
        sec = ats.new_tag("section")
        h2 = ats.new_tag("h2")
        h2.string = "Education"
        sec.append(h2)

        p = ats.new_tag("p")
        p.string = clean_text(education_section.get_text())
        sec.append(p)
        body.append(sec)

    # ----- WRITE OUTPUT -----
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(ats.prettify())

    print(f"ATS-friendly resume generated: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
