import argparse
import base64
import datetime
import html
import json
import pathlib
import re
import struct
import zipfile
from xml.sax.saxutils import escape


ROOT = pathlib.Path(__file__).resolve().parents[1]
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
XML_HEADER = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'


def clean(value):
    return re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", str(value))


def paragraph(text, style="Normal", keep_next=False):
    properties = '<w:pStyle w:val="' + style + '"/>'
    if keep_next:
        properties += "<w:keepNext/>"
    runs = []
    for index, line in enumerate(clean(text).split("\n")):
        if index:
            runs.append("<w:r><w:br/></w:r>")
        runs.append('<w:r><w:t xml:space="preserve">' + escape(line) + "</w:t></w:r>")
    return "<w:p><w:pPr>" + properties + "</w:pPr>" + "".join(runs) + "</w:p>"


def image_info(item, base):
    path = (base / item["path"]).resolve()
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("Report images must be PNG files: " + str(path))
    width, height = struct.unpack(">II", data[16:24])
    if width == 0 or height == 0:
        raise ValueError("Image has invalid dimensions: " + str(path))
    return data, width, height


def image_paragraph(index, width, height, caption):
    scale = min(6.65 / width, 7.4 / height)
    cx = round(width * scale * 914400)
    cy = round(height * scale * 914400)
    description = escape(clean(caption), {'"': "&quot;"})
    return f'''<w:p><w:pPr><w:jc w:val="center"/><w:keepNext/><w:spacing w:before="120" w:after="60"/></w:pPr><w:r><w:drawing>
<wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="{cx}" cy="{cy}"/><wp:docPr id="{index}" name="Screenshot {index}" descr="{description}"/><wp:cNvGraphicFramePr><a:graphicFrameLocks noChangeAspect="1"/></wp:cNvGraphicFramePr>
<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:pic><pic:nvPicPr><pic:cNvPr id="{index}" name="image{index}.png"/><pic:cNvPicPr/></pic:nvPicPr><pic:blipFill><a:blip r:embed="rIdImage{index}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill><pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic></a:graphicData></a:graphic>
</wp:inline></w:drawing></w:r></w:p>'''


def styles_xml():
    return XML_HEADER + f'''<w:styles xmlns:w="{W}">
<w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:sz w:val="21"/><w:color w:val="233044"/><w:lang w:val="en-GB"/></w:rPr></w:rPrDefault><w:pPrDefault><w:pPr><w:spacing w:after="140" w:line="276" w:lineRule="auto"/><w:widowControl/></w:pPr></w:pPrDefault></w:docDefaults>
<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/></w:style>
<w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:basedOn w:val="Normal"/><w:pPr><w:spacing w:before="500" w:after="240"/><w:keepNext/></w:pPr><w:rPr><w:b/><w:sz w:val="54"/><w:color w:val="123B55"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Subtitle"><w:name w:val="Subtitle"/><w:basedOn w:val="Normal"/><w:pPr><w:spacing w:after="260"/><w:keepNext/></w:pPr><w:rPr><w:sz w:val="28"/><w:color w:val="526678"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:pPr><w:keepNext/><w:keepLines/><w:spacing w:before="260" w:after="200"/><w:outlineLvl w:val="0"/></w:pPr><w:rPr><w:b/><w:sz w:val="32"/><w:color w:val="123B55"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:pPr><w:keepNext/><w:spacing w:before="220" w:after="120"/><w:outlineLvl w:val="1"/></w:pPr><w:rPr><w:b/><w:sz w:val="24"/><w:color w:val="1B6576"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Caption"><w:name w:val="Caption"/><w:basedOn w:val="Normal"/><w:pPr><w:jc w:val="center"/><w:keepLines/><w:spacing w:after="180"/></w:pPr><w:rPr><w:i/><w:sz w:val="18"/><w:color w:val="526678"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Metadata"><w:name w:val="Metadata"/><w:basedOn w:val="Normal"/><w:pPr><w:spacing w:after="100"/></w:pPr><w:rPr><w:sz w:val="20"/><w:color w:val="526678"/></w:rPr></w:style>
</w:styles>'''


def write_docx(data, base, destination):
    blocks = [paragraph(data["title"], "Title")]
    if data.get("subtitle"):
        blocks.append(paragraph(data["subtitle"], "Subtitle"))
    if data.get("date"):
        blocks.append(paragraph(data["date"], "Metadata"))
    if data.get("environment"):
        blocks.append(paragraph("Execution environment", "Heading2"))
        blocks.extend(paragraph(item, "Metadata") for item in data["environment"])
    if data.get("introduction"):
        blocks.append(paragraph("Introduction", "Heading2"))
        blocks.extend(paragraph(item) for item in data["introduction"])
    media = []
    relationships = [
        '<Relationship Id="rIdStyles" Type="' + R + '/styles" Target="styles.xml"/>',
        '<Relationship Id="rIdFooter" Type="' + R + '/footer" Target="footer1.xml"/>',
        '<Relationship Id="rIdSettings" Type="' + R + '/settings" Target="settings.xml"/>',
    ]
    for section in data.get("sections", []):
        blocks.append('<w:p><w:r><w:br w:type="page"/></w:r></w:p>')
        blocks.append(paragraph(section["title"], "Heading1"))
        blocks.extend(paragraph(item) for item in section.get("paragraphs", []))
        for item in section.get("images", []):
            content, width, height = image_info(item, base)
            media.append(content)
            index = len(media)
            caption = item.get("caption", "")
            blocks.append(image_paragraph(index, width, height, caption))
            blocks.append(paragraph(caption, "Caption"))
            relationships.append(f'<Relationship Id="rIdImage{index}" Type="{R}/image" Target="media/image{index}.png"/>')
    if data.get("conclusion"):
        blocks.append('<w:p><w:r><w:br w:type="page"/></w:r></w:p>')
        blocks.append(paragraph("Conclusion", "Heading1"))
        blocks.extend(paragraph(item) for item in data["conclusion"])
    blocks.append('<w:sectPr><w:footerReference w:type="default" r:id="rIdFooter"/><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1152" w:right="1152" w:bottom="1152" w:left="1152" w:header="576" w:footer="576" w:gutter="0"/></w:sectPr>')
    document = XML_HEADER + f'''<w:document xmlns:w="{W}" xmlns:r="{R}" xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"><w:body>{''.join(blocks)}</w:body></w:document>'''
    content_types = XML_HEADER + '''<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Default Extension="png" ContentType="image/png"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/><Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/><Override PartName="/word/footer1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/><Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/><Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/></Types>'''
    package_rels = XML_HEADER + f'''<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="{R}/officeDocument" Target="word/document.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/><Relationship Id="rId3" Type="{R}/extended-properties" Target="docProps/app.xml"/></Relationships>'''
    doc_rels = XML_HEADER + '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">' + "".join(relationships) + "</Relationships>"
    footer = XML_HEADER + f'''<w:ftr xmlns:w="{W}"><w:p><w:pPr><w:jc w:val="center"/></w:pPr><w:r><w:rPr><w:sz w:val="18"/><w:color w:val="526678"/></w:rPr><w:t xml:space="preserve">Page </w:t></w:r><w:fldSimple w:instr="PAGE"><w:r><w:rPr><w:sz w:val="18"/><w:color w:val="526678"/></w:rPr><w:t>1</w:t></w:r></w:fldSimple></w:p></w:ftr>'''
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    core = XML_HEADER + f'''<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><dc:title>{escape(clean(data['title']))}</dc:title><dcterms:created xsi:type="dcterms:W3CDTF">{timestamp}</dcterms:created><dcterms:modified xsi:type="dcterms:W3CDTF">{timestamp}</dcterms:modified></cp:coreProperties>'''
    app = XML_HEADER + '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"><Application>Lab report generator</Application></Properties>'
    settings = XML_HEADER + f'<w:settings xmlns:w="{W}"><w:updateFields w:val="true"/><w:defaultTabStop w:val="720"/></w:settings>'
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as report:
        for name, content in {
            "[Content_Types].xml": content_types,
            "_rels/.rels": package_rels,
            "word/document.xml": document,
            "word/_rels/document.xml.rels": doc_rels,
            "word/styles.xml": styles_xml(),
            "word/settings.xml": settings,
            "word/footer1.xml": footer,
            "docProps/core.xml": core,
            "docProps/app.xml": app,
        }.items():
            report.writestr(name, content.encode("utf-8"))
        for index, content in enumerate(media, start=1):
            report.writestr(f"word/media/image{index}.png", content)


def html_text(value):
    return html.escape(clean(value)).replace("\n", "<br>")


def html_paragraphs(items):
    return "".join("<p>" + html_text(item) + "</p>" for item in items)


def write_html(data, base, destination):
    parts = ['<section class="cover"><h1>' + html_text(data["title"]) + "</h1>"]
    if data.get("subtitle"):
        parts.append('<p class="subtitle">' + html_text(data["subtitle"]) + "</p>")
    if data.get("date"):
        parts.append('<p class="date">' + html_text(data["date"]) + "</p>")
    if data.get("environment"):
        parts.append('<h2>Execution environment</h2><div class="environment">' + html_paragraphs(data["environment"]) + "</div>")
    if data.get("introduction"):
        parts.append("<h2>Introduction</h2>" + html_paragraphs(data["introduction"]))
    parts.append("</section>")
    for section in data.get("sections", []):
        parts.append('<section class="report-section" id="' + html.escape(str(section.get("id", "")), quote=True) + '"><h2>' + html_text(section["title"]) + "</h2>")
        parts.append(html_paragraphs(section.get("paragraphs", [])))
        for item in section.get("images", []):
            content, width, height = image_info(item, base)
            encoded = base64.b64encode(content).decode("ascii")
            caption = html_text(item.get("caption", ""))
            alternative = html.escape(clean(item.get("caption", "Screenshot")), quote=True)
            parts.append(f'<figure><img src="data:image/png;base64,{encoded}" width="{width}" height="{height}" alt="{alternative}"><figcaption>{caption}</figcaption></figure>')
        parts.append("</section>")
    if data.get("conclusion"):
        parts.append('<section class="report-section"><h2>Conclusion</h2>' + html_paragraphs(data["conclusion"]) + "</section>")
    css = '''
@page { size: A4; margin: 19mm 20mm; }
* { box-sizing: border-box; }
body { color: #233044; font: 11pt/1.5 Calibri, Arial, sans-serif; margin: 0; background: #eef2f5; }
main { max-width: 210mm; margin: 24px auto; padding: 20mm; background: white; box-shadow: 0 2px 18px #b7c3ce; }
h1 { font-size: 29pt; line-height: 1.15; color: #123b55; margin: 12mm 0 6mm; }
h2 { color: #123b55; font-size: 18pt; line-height: 1.2; margin: 0 0 6mm; break-after: avoid; }
.cover h2 { font-size: 14pt; margin-top: 9mm; color: #1b6576; }
.subtitle { font-size: 15pt; color: #526678; margin-bottom: 5mm; }
.date, .environment { color: #526678; font-size: 10pt; }
.environment p { margin: 0 0 2mm; }
p { margin: 0 0 4mm; orphans: 3; widows: 3; }
.report-section { border-top: 1px solid #cbd9e2; margin-top: 12mm; padding-top: 10mm; }
figure { margin: 6mm 0; break-inside: avoid; page-break-inside: avoid; }
img { display: block; width: auto; height: auto; max-width: 100%; max-height: 190mm; margin: auto; object-fit: contain; border: 1px solid #dde5eb; }
figcaption { font-size: 9pt; line-height: 1.35; font-style: italic; text-align: center; color: #526678; margin-top: 3mm; }
@media print {
body { background: white; font-size: 10.5pt; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
main { margin: 0; padding: 0; max-width: none; box-shadow: none; }
.report-section { break-before: page; page-break-before: always; border: 0; margin: 0; padding: 0; }
}
'''
    document = '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>' + html_text(data["title"]) + "</title><style>" + css + "</style></head><body><main>" + "".join(parts) + "</main></body></html>"
    destination.write_text(document, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Build an editable DOCX and printable HTML lab report from JSON.")
    parser.add_argument("data", nargs="?", type=pathlib.Path, default=ROOT / "report_data.json")
    parser.add_argument("--output-name", default="Lab3_Report")
    parser.add_argument("--output-dir", type=pathlib.Path)
    args = parser.parse_args()
    source = args.data.resolve()
    data = json.loads(source.read_text(encoding="utf-8-sig"))
    destination = args.output_dir.resolve() if args.output_dir else source.parent
    destination.mkdir(parents=True, exist_ok=True)
    docx = destination / (args.output_name + ".docx")
    page = destination / (args.output_name + ".html")
    write_docx(data, source.parent, docx)
    write_html(data, source.parent, page)
    print(docx)
    print(page)


if __name__ == "__main__":
    main()
