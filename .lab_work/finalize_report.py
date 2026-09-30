from pathlib import Path
import json

work=Path('C:/Users/Xxthe/OneDrive/Desktop/Cloud_Lab/Lab3/work')
state=json.loads((work/'state.json').read_text(encoding='utf-8-sig'))
local=json.loads((work/'local_cleanup.json').read_text(encoding='utf-8-sig'))
assert state['cleanup']['aws_verified'] and local['local_verified']
assert state['file']['verified_on_B'] and state['file']['verified_on_C']
path=work/'report_data.json'
data=json.loads(path.read_text(encoding='utf-8-sig'))
data['complete']=True
data['submission_date']='September 25, 2026'
obs=data['observations']
obs['aws_execution']='All three tasks were completed and all 15 required screenshots were captured. Both applications were preserved through Image-A and Image-B. Instance-C restored the data volume automatically and the timestamp file matched the local original. All recorded lab resources were removed after verification.'
obs['image_b']={'name':state['images']['B']['name'],'image_id':state['images']['B']['id'],'state_at_capture':'Available','snapshots':state['images']['B']['snapshots'],'evidence':'evidence/aws/13_image_b_available.png'}
obs['instance_c']={**state['instances']['C'],'state_at_capture':'Running','application_icons':['Everything','WizTree'],'source_image':state['images']['B']['id'],'evidence':['evidence/aws/14_instance_c_running.png','evidence/remote/15_instance_c_software.png','evidence/remote/16_instance_c_restored_file.png']}
obs['file_on_c']={'path':'E:\\Hamdan.txt','size_bytes':72,'timestamp':state['file']['timestamp'],'sha256':state['file']['sha256'],'matches_local_file':True,'manual_disk_configuration':False,'evidence':'evidence/remote/instance_c_file_contents.png'}
obs['cleanup']={**state['cleanup'],'local_verified':True,'evidence':['evidence/aws/cleanup_'+name+'.png' for name in ['instances','amis','volumes','snapshots','key_pair','security_group']]}
captions={13:'Image-B-Hamdan available with snapshots of the Windows disk and the 1 GiB data disk.',14:'Instance-C-Hamdan running from Image-B-Hamdan.',15:'Everything and WizTree icons preserved on Instance-C.',16:'Hamdan.txt preserved on the restored Storage-A-Hamdan (E:) volume on Instance-C.'}
answer7='An instance is the virtual computer, and its EBS volumes store Windows, applications, and files. When an EBS-backed AMI is created, AWS takes snapshots of the included volumes and records their device mappings in the image. Launching an instance from that AMI creates new EBS volumes from the snapshots. Image-A preserved Everything and WizTree on Instance-B. Image-B included both the Windows and data disks, so Instance-C also restored Hamdan.txt. Its data volume had a new volume ID; the original Storage-A was not reattached. [1-3]'
answer17='On Instance-B, Storage-A was online but had no partition or file system. I initialized it as GPT, formatted it as NTFS, and assigned E: with the label Storage-A-Hamdan. On Instance-C, the restored disk was already online and available as E: without manual configuration. Image-B preserved the partition, file system, and file. Hamdan.txt contained the same timestamp, and its SHA-256 hash matched the local original. [3, 4]'
cleanup='I terminated Instance-A, Instance-B, and Instance-C, deregistered both AMIs, and deleted their three snapshots. The three root volumes were removed automatically on termination. I deleted the original data volume and the restored data volume, then verified that no volumes or snapshots remained in the lab region. I also deleted the lab key pair and security group and removed the temporary local credentials and connection files. Cleanup was verified on September 25, 2026.'
blocks=[]
answer=None
for block in data['blocks']:
    if block['kind']=='pending':
        if block['text'].startswith('Pending:'):
            blocks.append({'kind':'paragraph','text':cleanup})
        continue
    if block['kind']=='figure' and block['deliverable'] in captions:
        block['caption']=captions[block['deliverable']]
    if block['kind']=='question':
        answer=block['deliverable']
    elif block['kind']=='paragraph' and answer in [7,17]:
        block['text']=answer7 if answer==7 else answer17
        answer=None
    for key in ['text','caption']:
        if key in block: block[key]=block[key].replace('E:\\\\Hamdan.txt','E:\\Hamdan.txt')
    blocks.append(block)
data['blocks']=blocks
assert set(b['deliverable'] for b in blocks if 'deliverable' in b)==set(range(1,18))
assert all((work/b['file']).is_file() for b in blocks if b['kind']=='figure')
assert not any('pending' in b.get('text','').lower() or 'pending' in b.get('caption','').lower() for b in blocks)
path.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
state['cleanup']['local_verified']=True
(work/'state.json').write_text(json.dumps(state,indent=2)+'\n',encoding='utf-8')
print('Final report data ready: all 17 deliverables and verified cleanup.')
