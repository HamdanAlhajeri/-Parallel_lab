# Lab 3 report answers

Prepared from official AWS documentation on 25 September 2026. The explanations below are source-based. Replace the observation notes with the actual results and screenshot numbers before submitting the report.

## Deliverable 7: How AWS creates AMIs and how the resources relate

An EC2 instance is the virtual computer that runs the operating system and applications. Its EBS volumes hold the operating system, installed software, and other saved files. When an EBS-backed AMI is created from an instance, EC2 takes snapshots of its root volume and the included attached EBS volumes. EC2 registers an AMI that references those snapshots and records the storage layout. This allows the installed software and saved data to be reproduced when a new instance is launched. [AWS: Create an Amazon EBS-backed AMI](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/creating-an-ami-ebs.html)

The AMI's block device mapping specifies which disks should be attached at launch. A snapshot stores a volume's state at a particular time. Launching another instance from the AMI creates new EBS volumes from the referenced snapshots, so the new instance receives a separate copy of the saved disks. For this lab, Image-A is intended to preserve the installed applications, while Image-B is intended to preserve both the applications and the additional data disk containing the text file. [AWS: Block device mappings](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/block-device-mapping-concepts.html), [AWS: Restore a volume from a snapshot](https://docs.aws.amazon.com/ebs/latest/userguide/ebs-restoring-volume.html)

Observation to add after verification: identify the screenshots showing applications on Instance-B and both applications and the saved file on Instance-C. Do not describe these outcomes as observed until those checks succeed.

## Deliverable 17: Was Storage-A ready to use on Instance-B and Instance-C?

On Instance-B, Storage-A starts as an empty EBS disk. Attaching a disk in AWS does not by itself create a usable Windows file system. If Windows does not configure it automatically, it must be brought online, initialized, given a partition and drive letter, and formatted before files can be stored on it. [AWS: Make an Amazon EBS volume available for use](https://docs.aws.amazon.com/ebs/latest/userguide/ebs-using-volumes.html)

On Instance-C, the data disk is a new volume restored from the snapshot recorded in Image-B. Its existing partition, file system, and saved text file are retained, so it should not need formatting again. Whether the disk appears immediately in File Explorer depends on Windows bringing it online and assigning a drive letter. Any required online or drive-letter step should be reported; a restored disk should not be reformatted because that would erase its saved data. [AWS: Restore a volume from a snapshot](https://docs.aws.amazon.com/ebs/latest/userguide/ebs-restoring-volume.html), [AWS: Make an Amazon EBS volume available for use](https://docs.aws.amazon.com/ebs/latest/userguide/ebs-using-volumes.html)

Observations still required: record whether Instance-B needed manual initialization, its chosen drive letter and volume label, whether Instance-C mounted its restored disk automatically, and whether the timestamp file contents matched. The explanation above gives the expected behavior, not a claim that those observations have already been made.
