import hashlib
import json
import pathlib
import re
import subprocess
import sys


sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
CLOUD = pathlib.Path("C:/Users/Xxthe/OneDrive/Desktop/Cloud_Lab")
WORK = CLOUD / "Lab3/work"
OUT = CLOUD / "Lab3/output"
WORK.mkdir(exist_ok=True)
OUT.mkdir(exist_ok=True)

draft = json.loads((HERE / "report_data_draft.json").read_text(encoding="utf-8"))
data = {
    "student_name": draft["student_name"],
    "student_id": draft["student_id"],
    "submission_date": "September 25, 2026 (working draft)",
    "complete": False,
    "metadata_sources": draft["metadata_sources"],
    "observations": {
        "local_timestamp": "2026-09-25T12:44:18.1189433+04:00",
        "local_file": "Hamdan.txt",
        "aws_execution": "Pending sign-in and execution",
    },
    "blocks": [],
}
blocks = data["blocks"]
blocks.append({"kind": "heading", "text": "Exercise Objective"})
blocks.append({"kind": "paragraph", "text": "Create Windows EC2 images with preloaded applications, attach an EBS data disk, and check whether the applications and saved file are preserved when new instances are launched."})
blocks.append({"kind": "pending", "text": "WORKING DRAFT: only the local timestamp command (Deliverable 10) has been completed. AWS execution, screenshots, observed results, and cleanup verification remain pending."})

task_titles = {
    1: "Task 1 - Create an AMI",
    2: "Task 2 - Attach an EBS and Upload Files",
    3: "Task 3 - Create an AMI with EBS",
    4: "Task 4 - Resource Cleanup",
}
previous_task = None
for section in draft["sections"]:
    task = section["task"]
    if task != previous_task:
        if previous_task is not None:
            blocks.append({"kind": "pagebreak"})
        blocks.append({"kind": "heading", "text": task_titles[task]})
        previous_task = task
    number = section.get("deliverable")
    if section["kind"] == "screenshot":
        title = section["title"].split(": ", 1)[1]
        file = "evidence/10_local_date.png" if number == 10 else section["evidence_file"]
        caption = "PowerShell in Downloads created Hamdan.txt with timestamp 2026-09-25T12:44:18.1189433+04:00." if number == 10 else "Evidence pending."
        blocks.append({"kind": "figure", "deliverable": number, "title": title, "file": file, "caption": caption})
    elif number == 7:
        blocks.append({"kind": "question", "deliverable": number, "text": "How are instances, AMIs, volumes, and snapshots related?"})
        blocks.append({"kind": "paragraph", "text": "An instance is the virtual computer, and EBS volumes store its operating system, applications, and files. Creating an EBS-backed AMI takes snapshots of the included volumes and records their storage layout. The AMI refers to those snapshots; launching from it creates new volumes from the saved data. Image-A is intended to preserve the installed applications, while Image-B should also preserve the additional disk and its text file. These outcomes still need to be verified in this run. [1-3]"})
    elif number == 17:
        blocks.append({"kind": "question", "deliverable": number, "text": section["question"]})
        blocks.append({"kind": "paragraph", "text": "Expected behavior: Storage-A begins as an empty disk on Instance-B, so it may need to be brought online, initialized, partitioned, formatted, and assigned a drive letter. On Instance-C, the data volume restored through Image-B should retain its partition, file system, and saved file; it should not need formatting again. Windows might still need an online or drive-letter step. The actual configuration steps and file persistence on both instances have not yet been tested. [3, 4]"})
    else:
        blocks.append({"kind": "pending", "text": "Pending: after the AWS tasks, verify termination of the lab instances, deregistration of the lab AMIs, and deletion of their remaining EBS volumes and snapshots. Record cleanup of any key pair or security group created for this lab."})

blocks.append({"kind": "heading", "text": "References"})
for title, url in [
    ("[1] AWS, Create an Amazon EBS-backed AMI.", "https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/creating-an-ami-ebs.html"),
    ("[2] AWS, Block device mappings.", "https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/block-device-mapping-concepts.html"),
    ("[3] AWS, Restore a volume from a snapshot.", "https://docs.aws.amazon.com/ebs/latest/userguide/ebs-restoring-volume.html"),
    ("[4] AWS, Make an Amazon EBS volume available for use.", "https://docs.aws.amazon.com/ebs/latest/userguide/ebs-using-volumes.html"),
]:
    blocks.append({"kind": "reference", "text": title, "url": url})

assert sorted(block["deliverable"] for block in blocks if "deliverable" in block) == list(range(1, 18))
actual_file = (WORK / "Hamdan.txt").read_text(encoding="utf-16").strip()
assert actual_file == data["observations"]["local_timestamp"]
assert (WORK / "evidence/10_local_date.png").is_file()
(WORK / "report_data.json").write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
(WORK / "report_answers.md").write_bytes((HERE / "report_answers.md").read_bytes())
(WORK / "university_logo.jpeg").write_bytes((CLOUD / "Lab2/work/university_logo.jpeg").read_bytes())

builder = (CLOUD / "Lab2/work/build_report.py").read_text(encoding="utf-8")
for old, new in [
    ("import sys\n", "import sys\nsys.dont_write_bytecode = True\n"),
    ("'Lab2'", "'Lab3'"),
    ("Lab Exercise #2 Report", "Lab Exercise #3 Report"),
    ("Launching and Managing an EC2 Windows Instance", "Creating AMIs with Software and EBS Storage"),
    ("Mr. Abduraouf Hassan", "Mr. Mohammad Madine"),
    ("Submission Date:", "Report Date:"),
    ("CCEN 448 Lab 2:", "CCEN 448 Lab 3:"),
    ("CCEN448_Lab2_", "CCEN448_Lab3_"),
]:
    assert old in builder, old
    builder = builder.replace(old, new)
(WORK / "build_report.py").write_text(builder, encoding="utf-8")
subprocess.run([sys.executable, "-B", str(WORK / "build_report.py")], check=True)

sys.path.insert(0, str(CLOUD / ".lab_tools"))
import pymupdf
from docx import Document
from PIL import Image, ImageDraw

stem = "CCEN448_Lab3_Hamdan_AlHajeri_100060861_DRAFT"
pdf_path = OUT / (stem + ".pdf")
docx_path = OUT / (stem + ".docx")
report = pymupdf.open(pdf_path)
pdf_text = "\n".join(page.get_text() for page in report)
assert sorted(map(int, re.findall(r"Deliverable (\d+):", pdf_text))) == list(range(1, 18))
assert "Hamdan AlHajeri" in pdf_text and "100060861" in pdf_text
assert "Mr. Mohammad Madine" in pdf_text
assert "WORKING DRAFT" in pdf_text
assert pdf_text.count("Evidence pending: this screenshot has not yet been captured.") == 14
assert data["observations"]["local_timestamp"] in pdf_text
for page in report:
    for x0, y0, x1, y1, word, *_ in page.get_text("words"):
        assert 0 <= x0 < x1 <= 612.5 and 0 <= y0 < y1 <= 792.5, word
word_report = Document(docx_path)
word_text = "\n".join(paragraph.text for paragraph in word_report.paragraphs)
assert sorted(map(int, re.findall(r"Deliverable (\d+):", word_text))) == list(range(1, 18))
assert len(word_report.inline_shapes) == 2
assert "WORKING DRAFT" in word_text
columns = 3
width, height = 306, 412
sheet = Image.new("RGB", (columns * width, ((len(report) + columns - 1) // columns) * height), "#dddddd")
draw = ImageDraw.Draw(sheet)
for index, page in enumerate(report):
    pixmap = page.get_pixmap(matrix=pymupdf.Matrix(0.5, 0.5), alpha=False)
    page_image = Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)
    x = index % columns * width
    y = index // columns * height
    sheet.paste(page_image, (x, y))
    draw.text((x + 8, y + 397), "Page " + str(index + 1), fill="black")
sheet.save(WORK / "draft_report_contact.png")
validation = {
    "status": "working draft",
    "pdf_pages": len(report),
    "numbered_deliverables": 17,
    "actual_experimental_screenshots": 1,
    "pending_experimental_screenshots": 14,
    "docx_images_including_logo": len(word_report.inline_shapes),
    "all_pdf_text_within_page_bounds": True,
    "artifacts": {path.name: {"bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()} for path in [pdf_path, docx_path]},
}
(WORK / "draft_validation.json").write_text(json.dumps(validation, indent=2), encoding="utf-8")
(OUT / "README_DRAFT.txt").write_text("CCEN 448 - Lab Exercise 3\nHamdan AlHajeri | 100060861\n\nWORKING DRAFT - NOT READY FOR SUBMISSION\n\nThe PDF and DOCX include all 17 required deliverable labels. Only Deliverable 10 has an actual execution screenshot: the local PowerShell timestamp command. AWS screenshots, resource work, file-persistence observations, and cleanup remain pending. Written answers describe source-based expected behavior where observations are still needed.\n\nThe editable source is ../work/report_data.json. The reproducible report builder is ../work/build_report.py. Original local evidence is ../work/evidence/10_local_date.png and ../work/Hamdan.txt.\n", encoding="utf-8")
print(json.dumps(validation, indent=2))
