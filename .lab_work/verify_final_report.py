import argparse
import collections
import datetime
import hashlib
import io
import json
import pathlib
import re
import sys


sys.dont_write_bytecode = True
REQUIRED_DELIVERABLES = list(range(1, 18))
REQUIRED_SCREENSHOTS = list(range(1, 7)) + list(range(8, 17))
REQUIRED_ANSWERS = [7, 17]
MARKERS = [
    r"\bdraft\b",
    r"\bpending\b",
    r"not ready for submission",
    r"has not yet been captured",
    r"have not yet been tested",
    r"still need to be verified",
    r"observations still required",
    r"answer pending",
]


def digest_bytes(content):
    return hashlib.sha256(content).hexdigest()


def pixel_digest(image):
    image = image.convert("RGB")
    return digest_bytes(str(image.size).encode("ascii") + image.tobytes())


def labels(text):
    return sorted(map(int, re.findall(r"Deliverable\s+(\d+)\s*:", text)))


def main():
    parser = argparse.ArgumentParser(description="Check completed Lab 3 report and render pages for visual review.")
    parser.add_argument("--lab-root", type=pathlib.Path, default=pathlib.Path("C:/Users/Xxthe/OneDrive/Desktop/Cloud_Lab/Lab3"))
    parser.add_argument("--data", type=pathlib.Path)
    parser.add_argument("--pdf", type=pathlib.Path)
    parser.add_argument("--review-dir", type=pathlib.Path)
    parser.add_argument("--dpi", type=int, default=110)
    args = parser.parse_args()
    lab = args.lab_root.resolve()
    work = lab / "work"
    source = args.data.resolve() if args.data else work / "report_data.json"
    basename = "CCEN448_Lab3_Hamdan_AlHajeri_100060861"
    pdf_path = args.pdf.resolve() if args.pdf else lab / "output" / (basename + ".pdf")
    review = args.review_dir.resolve() if args.review_dir else work / "final_review"
    if args.dpi < 72 or args.dpi > 200:
        parser.error("--dpi must be between 72 and 200.")

    sys.path.insert(0, str(lab.parent / ".lab_tools"))
    try:
        import pymupdf
        from PIL import Image, ImageDraw
        from docx import Document
        if not callable(getattr(pymupdf, "open", None)):
            raise ImportError("pymupdf resolved as an inaccessible namespace package")
    except ImportError as error:
        print("Report libraries could not be loaded. Run this command with approved require_escalated execution.", file=sys.stderr)
        print(str(error), file=sys.stderr)
        return 2

    failures = []
    warnings = []
    checks = {}

    def check(name, condition, explanation):
        checks[name] = bool(condition)
        if not condition:
            failures.append(explanation)

    if not source.is_file():
        print("Report data does not exist: " + str(source), file=sys.stderr)
        return 2
    data = json.loads(source.read_text(encoding="utf-8-sig"))
    blocks = data.get("blocks", [])
    figures = [block for block in blocks if block.get("kind") == "figure"]
    questions = [block for block in blocks if block.get("kind") == "question"]
    check("source_complete", data.get("complete") is True, "report_data.json does not have complete=true.")
    check("source_deliverables", sorted(block["deliverable"] for block in blocks if "deliverable" in block) == REQUIRED_DELIVERABLES, "Source must contain each numbered deliverable 1-17 exactly once.")
    check("source_screenshots", sorted(block.get("deliverable", -1) for block in figures) == REQUIRED_SCREENSHOTS, "Source screenshot deliverables must be 1-6 and 8-16 exactly once.")
    check("source_answers", sorted(block.get("deliverable", -1) for block in questions) == REQUIRED_ANSWERS, "Source answer deliverables must be 7 and 17.")
    check("no_pending_blocks", not any(block.get("kind") == "pending" for block in blocks), "Source still contains pending blocks.")
    check("final_filename", not re.search(r"draft", pdf_path.stem, flags=re.I), "The PDF filename still identifies it as a draft.")

    screenshot_records = []
    screenshot_pixels = {}
    for block in figures:
        number = block.get("deliverable")
        file = work / block.get("file", "")
        item = {"deliverable": number, "path": str(file), "exists": file.is_file(), "caption": block.get("caption", "")}
        if not item["exists"]:
            failures.append(f"Deliverable {number}: screenshot file is missing: {file}")
        else:
            try:
                with Image.open(file) as screenshot:
                    screenshot.load()
                    item["dimensions"] = list(screenshot.size)
                    item["pixel_sha256"] = pixel_digest(screenshot)
                    screenshot_pixels[number] = item["pixel_sha256"]
                item["sha256"] = digest_bytes(file.read_bytes())
                item["bytes"] = file.stat().st_size
            except Exception as error:
                failures.append(f"Deliverable {number}: screenshot cannot be decoded: {error}")
        screenshot_records.append(item)
    checks["all_screenshot_files_readable"] = len(screenshot_pixels) == len(REQUIRED_SCREENSHOTS)
    repeated = collections.defaultdict(list)
    for number, checksum in screenshot_pixels.items():
        repeated[checksum].append(number)
    for numbers in repeated.values():
        if len(numbers) > 1:
            warnings.append("The same image pixels are used by deliverables " + ", ".join(map(str, numbers)) + "; verify that the shared screenshot supports each requirement.")

    review.mkdir(parents=True, exist_ok=True)
    pages = []
    pdf_text = ""
    embedded_pixels = set()
    artifacts = []
    if not pdf_path.is_file():
        failures.append("Final PDF does not exist: " + str(pdf_path))
    else:
        report = pymupdf.open(pdf_path)
        check("pdf_nonempty", len(report) > 0, "PDF has no pages.")
        pdf_text = "\n".join(page.get_text() for page in report)
        check("pdf_deliverables", labels(pdf_text) == REQUIRED_DELIVERABLES, "PDF must display each Deliverable 1-17 exactly once.")
        check("pdf_figures", sorted(map(int, re.findall(r"Figure\s+(\d+)\s", pdf_text))) == list(range(1, 16)), "PDF must display Figure 1-15 exactly once.")
        check("pdf_identity", data.get("student_name", "") in pdf_text and str(data.get("student_id", "")) in pdf_text, "PDF is missing the expected student identity.")
        check("pdf_staff", "Mr. Mohammad Madine" in pdf_text, "PDF does not show the Lab 3 teaching assistant.")
        normalized = " ".join(pdf_text.split())
        found = [pattern for pattern in MARKERS if re.search(pattern, normalized, flags=re.I)]
        check("pdf_no_unfinished_markers", not found, "PDF still contains unfinished markers: " + ", ".join(found))
        check("pdf_no_em_dashes", "\u2014" not in pdf_text, "PDF contains em dashes, which the prior report avoided.")
        image_xrefs = set()
        out_of_bounds = []
        thumbnail_width = 306
        thumbnail_height = 422
        columns = 3
        sheet = Image.new("RGB", (columns * thumbnail_width, ((len(report) + columns - 1) // columns) * thumbnail_height), "#e4e8ec")
        drawing = ImageDraw.Draw(sheet)
        for index, page in enumerate(report):
            rect = page.rect
            image_info = page.get_image_info()
            for x0, y0, x1, y1, word, *_ in page.get_text("words"):
                if not (-0.5 <= x0 < x1 <= rect.width + 0.5 and -0.5 <= y0 < y1 <= rect.height + 0.5):
                    out_of_bounds.append({"page": index + 1, "type": "text", "text": word, "bounds": [x0, y0, x1, y1]})
            for info in image_info:
                x0, y0, x1, y1 = info["bbox"]
                if not (-0.5 <= x0 < x1 <= rect.width + 0.5 and -0.5 <= y0 < y1 <= rect.height + 0.5):
                    out_of_bounds.append({"page": index + 1, "type": "image", "bounds": [x0, y0, x1, y1]})
            image_xrefs.update(image[0] for image in page.get_images(full=True))
            image_path = review / f"page_{index + 1:02}.png"
            page.get_pixmap(matrix=pymupdf.Matrix(args.dpi / 72, args.dpi / 72), alpha=False).save(image_path)
            with Image.open(image_path) as page_image:
                page_image.thumbnail((thumbnail_width - 10, thumbnail_height - 24), Image.Resampling.LANCZOS)
                x = index % columns * thumbnail_width
                y = index // columns * thumbnail_height
                sheet.paste(page_image, (x + (thumbnail_width - page_image.width) // 2, y + 4))
                drawing.text((x + 8, y + thumbnail_height - 18), f"Page {index + 1}", fill="#233044")
            pages.append({"page": index + 1, "size_points": [rect.width, rect.height], "image_draws": len(image_info), "deliverables": labels(page.get_text()), "render": str(image_path)})
        for xref in image_xrefs:
            try:
                with Image.open(io.BytesIO(report.extract_image(xref)["image"])) as embedded:
                    embedded_pixels.add(pixel_digest(embedded))
            except Exception as error:
                warnings.append(f"Could not compare PDF image xref {xref}: {error}")
        for number, checksum in screenshot_pixels.items():
            if checksum not in embedded_pixels:
                failures.append(f"Deliverable {number}: original screenshot pixels were not found among the embedded PDF images.")
        checks["all_screenshots_embedded"] = len(screenshot_pixels) == 15 and all(value in embedded_pixels for value in screenshot_pixels.values())
        check("all_content_within_page_bounds", not out_of_bounds, "Some PDF text or images extend beyond the page; inspect content_bounds_issues.json.")
        (review / "content_bounds_issues.json").write_text(json.dumps(out_of_bounds, indent=2), encoding="utf-8")
        contact = review / "contact_sheet.png"
        sheet.save(contact)
        artifacts.extend([str(pdf_path), str(contact)])
        report.close()

    docx_path = pdf_path.with_suffix(".docx")
    if docx_path.is_file():
        document = Document(docx_path)
        word_text = "\n".join(paragraph.text for paragraph in document.paragraphs)
        check("docx_deliverables", labels(word_text) == REQUIRED_DELIVERABLES, "DOCX must display each Deliverable 1-17 exactly once.")
        check("docx_images", len(document.inline_shapes) == 16, "DOCX must have 15 evidence images plus the university logo.")
        word_found = [pattern for pattern in MARKERS if re.search(pattern, " ".join(word_text.split()), flags=re.I)]
        check("docx_no_unfinished_markers", not word_found, "DOCX still contains unfinished markers: " + ", ".join(word_found))
        artifacts.append(str(docx_path))
    else:
        warnings.append("Matching DOCX was not found; PDF validation is still performed.")

    output = {
        "passed": not failures,
        "checked_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "source": str(source),
        "pdf": str(pdf_path),
        "pdf_sha256": digest_bytes(pdf_path.read_bytes()) if pdf_path.is_file() else None,
        "required_deliverables": REQUIRED_DELIVERABLES,
        "required_screenshot_deliverables": REQUIRED_SCREENSHOTS,
        "checks": checks,
        "failures": failures,
        "warnings": warnings,
        "screenshots": screenshot_records,
        "pages": pages,
        "artifacts": artifacts,
        "manual_review": ["Inspect contact_sheet.png and page PNGs for layout and legibility.", "Confirm every AWS console screenshot visibly includes the username at the top right.", "Confirm captions, written observations, and cleanup statements agree with the actual evidence."],
    }
    result_path = review / "validation.json"
    result_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    (review / "pdf_text.txt").write_text(pdf_text, encoding="utf-8")
    print(json.dumps({"passed": output["passed"], "pdf_pages": len(pages), "screenshot_files": len(screenshot_pixels), "failures": failures, "warnings": warnings, "validation": str(result_path), "review_directory": str(review)}, indent=2))
    return 0 if output["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
