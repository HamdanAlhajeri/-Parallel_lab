## COMPLETED September 25, 2026
Lab3 AWS work, all17deliverables,15required real screenshots,2written answers complete. C automatically restored E: and Hamdan.txt hash matched original. AWS cleanup verified all3instances terminated,2AMIs deregistered,3snapshots deleted,5volumes gone,keypair+dedicatedSG removed; defaultSGpreserved. Tempsecrets and5WinCred entriesremoved. FinalPDF17pages+DOCX+ScreenshotsZIP(24originalPNGs)andREADME in C:/Users/Xxthe/OneDrive/Desktop/Cloud_Lab/Lab3/output. verify_final_report.py passed nofailures/warnings; contact sheetreviewed. Older drafts archived Lab3/work/previous_drafts. No Blackboard submission or gitpush performed. Authoritativestate Lab3/work/state.json. Historical notes below are stale.

## Latest progress at 2026-09-25 16:20 Asia/Dubai
A terminated; Image-A available. B apps verified, Storage-A initialized GPT/NTFS E:, original Hamdan.txt copied and hash verified. Evidence1-6,8-12 complete. B STOPPED; Image-B ami-0362f89f3d644e210 PENDING, created16:16. Root snapshot snap-0d03d900cbeb49761(30GiB), data snapshot snap-05775df7b13597df6(1GiB). Await available; then terminate_b.py, start_c.py, configure_c.py, launch_c.py, record_c.py, verify_rdp.py C, connect_saved_rdp.py C. Scripts under .lab_work and browser wrapper require escalation. Authoritative AWS manifest Cloud_Lab/Lab3/work/state.json. Do not duplicate launches. Browser9223 recovered from hung process using scoped psutil termination; one active AWS tab now Snapshots. check_image_b.py navigates back and captures13 when available. Agent lab3_report_check updating report_data; report_tooling completed final checker .lab_work/verify_final_report.py. Final report and AWS cleanup still required. Historical notes below may be stale.

# Lab 3 state

## ACTIVE RUN - supersedes older setup notes below

User replied ready; AWS signed in as HamdanAlhajeri2003 (731776047103).
LIVE resources have now been created and MUST be cleaned up after evidence:
Instance-A-Hamdan i-0060fb425d7ebcbad (stopped after graceful shutdown),
root vol-0a87781f82bbc250a, security group sg-0b3f9891500dc7ecc
(launch-wizard-1, RDP only from 31.215.195.115/32), key Hamdan-Lab3-20260925.
Image-A-Hamdan ami-08c8483cf822da554 is currently PENDING; its root snapshot
is snap-0e0928588f20ad22d. Created around 13:50 local Sept25.
Do not terminate A until Image-A is Available and screenshot 03 saved.
Then terminate A, save screenshot04, launch B from image A using same key/SG.

Authoritative run state: Cloud_Lab/Lab3/work/state.json.
A public DNS was ec2-100-54-14-202.compute-1.amazonaws.com (IP100.54.14.202),
private172.31.8.156, subnet-06d969874bc72855f, us-east-1a. RDP certificate SHA1
4F738966110A47DE621E1D8EF9D171054DEC4BDA matched AWS system log. Password is
DPAPI encrypted at %TEMP%/Codex_CloudLab_AWS_Secrets/Lab3_password.dpapi;
PEM and Hamdan-Lab3-A.rdp are there. Windows Credential Manager entry recorded
in state.json. Do NOT print passwords/private key. B/C should retain password.

Completed screenshots: evidence/aws/01_instance_a_running.png,
evidence/remote/02_instance_a_apps_running.png, evidence/10_local_date.png.
Everything1.4.1.1032 x64 and WizTree4.33 installed, signatures verified, both
running in actual screenshot02. report_data.json was updated by agent for 1/2.
Install transcript/script reside C:\\Lab3 inside remote A; inherited in AMIs.

Browser wrapper: python .lab_work/aws_lab3.py <step.py> requires escalation.
Browser tabs currently Image-A AMI inventory (first), Snapshots (second), old
LaunchInstances success page (third). Target exact page by URL as appropriate.
For reload/goto, wait page.locator('#compute-react-frame').wait_for(attached)
before accessing frame. EC2 inventory, details, AMIs, create image use
compute-react-frame. EBS Snapshots and Volumes use storage-react-frame.
check_image_a.py refreshes AMI, records snapshots, screenshots when Available.
check_snapshot.py reads snapshot panel; refresh button named Refresh snapshots.

Local RDP control can invoke prior Lab2/work/desktop_control.py with new scripts
in .lab_work; never run historical mutation scripts directly. remote_run.py
opens Run in focused RDP and executes a command text file. remote_paste.py pastes
one command into current focused remote app. rdp_capture.py captures to
.lab_work/rdp.png. accept_connection.py accepts Connect/Yes only after verified
target/certificate. GUI window is 1458x947 at20,30, remote desktop1440x900.
RDP state may currently be disconnect notice after A stop. Windows PowerShell
on remote A contains LabWindow user32 type for arranging apps (persistent only
in its console process). Taskbar positions can shift; inspect before clicking.
Remote app install used .lab_work/install_apps.ps1 via clipboard/base64.
remote_copy_file.py prepares CF_HDROP for actual local Downloads/Hamdan.txt
and pastes into the currently focused remote Explorer; run only after B data
disk Explorer is open. Preserve original timestamp file and verify on C.

## Earlier setup context

User confirmed on 2026-09-25 that the task is the AWS Cloud Infrastructure lab in
`C:/Users/Xxthe/OneDrive/Desktop/Cloud_Lab/Lab3/Exercise03_Fall2026 - Tagged.pdf`.
User authorized continuing the prior AWS lab workflow, including the real AWS
tasks, screenshots, report, and handout-required cleanup of resources created
for this lab. Do not remove unrelated resources. No AWS resources have been
created for Lab 3 yet.

Student metadata from the prior completed Lab 2 report: Hamdan AlHajeri,
student ID 100060861. Previous account was 731776047103, username
HamdanAlhajeri2003, region us-east-1. Verify the current signed-in account before
creating resources; do not assume historical account data is current.

The prior dedicated Edge profile at `%TEMP%/Codex_CloudLab_AWS` was reopened
with CDP on localhost:9223. AWS redirected to its sign-in page. An asynchronous
user question requests login/MFA and confirmation. The AWS login window was
brought forward. No credentials were read or disclosed. The user must renew
the expired login before AWS work can continue.

Local deliverable 10 is complete: the specified Get-Date command ran in
C:/Users/Xxthe/Downloads and created Hamdan.txt containing
2026-09-25T12:44:18.1189433+04:00. The real PowerShell screenshot is at
Cloud_Lab/Lab3/work/evidence/10_local_date.png; a copy of the text file is at
Cloud_Lab/Lab3/work/Hamdan.txt. Screenshot was visually verified. Do not rerun
the initial prepare_local.py blindly because it refuses to overwrite the file.

Automation helpers and source text are currently staged in this workspace's
.lab_work directory. aws_lab3.py attaches using installed Playwright from
Cloud_Lab/.lab_browser. Invoke with a step script to operate that lab browser.
Require escalated execution for browser control, external Lab3 writes, and
libraries in Cloud_Lab/.lab_tools; normal sandbox imports see empty namespace
packages. Prior successful report tools use pymupdf, docx, reportlab there.

Required AWS sequence: Windows t3.micro Instance-A-Hamdan; install Everything
and WizTree; stop A; create Image-A-Hamdan; wait Available; terminate A; launch
Instance-B-Hamdan from Image-A; verify apps. Create a 1 GiB gp3 volume named
Storage-A-Hamdan in B's AZ; stop B, attach, start, initialize/format as needed;
copy the existing local Hamdan.txt to it and capture file/contents. Stop B;
create Image-B-Hamdan including both volumes; wait Available; terminate B;
launch Instance-C-Hamdan from Image-B; verify apps and restored data volume/file.
Capture all 15 required screenshots with the AWS username visible on every
AWS screenshot. Answer deliverables 7 and 17 based on actual observations.
Finally terminate only Lab3 instances and remove Lab3 images, volumes,
snapshots and any dedicated lab key/security group after saving evidence.

Report answer source: report_answers.md. Report skeleton: report_data_draft.json.
Any draft report must clearly mark AWS work pending; do not claim completion
or fabricate screenshots. Final report must be PDF with cover, identity,
concise descriptions, actual screenshots, written answers, and cleanup record.
