from pathlib import Path
import json
import zipfile
import hashlib

root=Path('C:/Users/Xxthe/OneDrive/Desktop/Cloud_Lab/Lab3').resolve()
work=root/'work'
out=root/'output'
data=json.loads((work/'report_data.json').read_text())
validation=json.loads((work/'final_review/validation.json').read_text())
assert data['complete']
assert json.loads((work/'state.json').read_text())['cleanup']['aws_verified']
readme='''CCEN 448 - Lab Exercise 3
Hamdan AlHajeri | 100060861
Completed September 25, 2026

Files
CCEN448_Lab3_Hamdan_AlHajeri_100060861.pdf: final report for submission.
CCEN448_Lab3_Hamdan_AlHajeri_100060861.docx: editable report.
Lab3_Screenshots_and_Evidence.zip: all 15 required screenshots, 9 additional
verification/cleanup screenshots, the original Hamdan.txt, and an evidence index.

The report covers all 17 deliverables. Instance-C restored the applications and
E:\\Hamdan.txt without manual disk setup. Its file contents and SHA-256 matched
the original local file. All lab instances, AMIs, volumes, snapshots, the lab key
pair, and the lab security group were removed after evidence was saved.

The screenshots are original captures from AWS and Remote Desktop.
Supporting source and validation files are retained in ../work.
'''
(out/'README.txt').write_text(readme,encoding='utf-8')
index=['Lab 3 screenshot index','']
for b in data['blocks']:
 if b['kind']=='figure': index.append(str(b['deliverable'])+': '+b['file']+' - '+b['caption'])
index.extend(['','Other screenshots provide disk initialization, Instance-B termination,','Instance-C file contents/hash, and final resource cleanup evidence.','','Original file SHA-256: '+hashlib.sha256((work/'Hamdan.txt').read_bytes()).hexdigest().upper()])
files=sorted((work/'evidence').rglob('*.png'))
assert len(files)==24
archive=out/'Lab3_Screenshots_and_Evidence.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for file in files: z.write(file,file.relative_to(work).as_posix())
 z.write(work/'Hamdan.txt','Hamdan.txt')
 z.writestr('Evidence_Index.txt','\n'.join(index)+'\n')
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None and len(z.namelist())==26
drafts=work/'previous_drafts'
drafts.mkdir(exist_ok=True)
for name in ['CCEN448_Lab3_Hamdan_AlHajeri_100060861_DRAFT.pdf','CCEN448_Lab3_Hamdan_AlHajeri_100060861_DRAFT.docx','README_DRAFT.txt']:
 source=(out/name).resolve()
 destination=(drafts/name).resolve()
 assert source.parent==out and destination.parent==drafts
 assert source.is_relative_to(root) and destination.is_relative_to(root)
 if source.exists(): source.replace(destination)
print('Final package prepared; 24 original screenshots, file, and index verified in ZIP.')
for file in sorted(out.iterdir()):
 if file.is_file(): print(file.name, file.stat().st_size)
