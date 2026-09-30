from pathlib import Path
import json

path=Path('C:/Users/Xxthe/OneDrive/Desktop/Cloud_Lab/Lab3/work/report_data.json')
data=json.loads(path.read_text(encoding='utf-8'))
answers={
    7: "AWS creates an EBS-backed AMI by taking snapshots of an instance's included volumes and recording their device mappings. Launching a new instance from the AMI creates new volumes from those snapshots, preserving the saved operating system, applications, and files. [1-3]",
    17: "Storage-A required manual initialization, NTFS formatting, and a drive letter on Instance-B. On Instance-C, it was ready as E: automatically because Image-B preserved its partition, file system, and saved file. [3, 4]",
}
cleanup='I terminated all three lab instances and removed both AMIs, all volumes and snapshots, and the lab key pair and security group. I verified cleanup and removed the temporary local credentials and connection files.'
answer=None
heading=None
for block in data['blocks']:
    if block['kind']=='heading':
        heading=block['text']
    elif block['kind']=='question':
        answer=block['deliverable']
    elif block['kind']=='paragraph':
        if answer in answers:
            block['text']=answers[answer]
            answer=None
        elif heading=='Task 4 - Resource Cleanup':
            block['text']=cleanup
    if block['kind']=='figure' and block['deliverable']==10:
        block['caption']='PowerShell created Hamdan.txt with the current timestamp in Downloads.'
path.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('Report explanations shortened to one or two sentences each.')
