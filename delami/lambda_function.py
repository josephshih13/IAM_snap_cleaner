import boto3
from dateutil.parser import parse
import datetime

def del_ami():
    age = -1
    aws_profile_name = 'prod'
    def days_old(date):
        get_date_obj = parse(date)
        date_obj = get_date_obj.replace(tzinfo=None)
        diff = datetime.datetime.now() - date_obj
        return diff.days
        
    def days_old2(date):
        # get_date_obj = parse(date)
        date_obj = date.replace(tzinfo=None)
        diff = datetime.datetime.now() - date_obj
        return diff.days
    
    #boto3.setup_default_session(profile_name = aws_profile_name)
    client = boto3.client('ec2')
    amis = client.describe_images(Owners=[
            'self'
        ])
    # print(amis)
    
    client2 = boto3.client('autoscaling')
    # amis = client.describe_images(Owners=[
                # 'self'
            # ])
        # print(amis)
        
    launch_id = []
    launch_snap = []
        
    paginator = client2.get_paginator('describe_launch_configurations')
    
        # Create a PageIterator from the Paginator
    page_iterator = paginator.paginate()
        
    for page in page_iterator:
        for lc in page['LaunchConfigurations']:
            launch_id.append(lc['ImageId'])
    
    
    for ami in amis['Images']:
        create_date = ami['CreationDate']
        ami_id = ami['ImageId']
        # print ami['ImageId'], ami['CreationDate']
        if ami_id in launch_id:
            blockmapping = ami['BlockDeviceMappings']
            for bm in blockmapping:
                launch_snap.append(bm['Ebs']['SnapshotId'])
            continue
        day_old = days_old(create_date)
        if day_old > age:
            print("deleting -> " + ami_id + " - create_date = " + create_date)
            # deregister the AMI
            client.deregister_image(ImageId=ami_id)
    print(launch_snap)
    
    
    account_id = boto3.client('sts').get_caller_identity().get('Account')
    # print(account_id)
    snapshots = client.describe_snapshots(OwnerIds=[account_id])
    # print(snapshots['Snapshots'])
    
    for snapshot in snapshots['Snapshots']:
        create_date = snapshot['StartTime']
        snap_id = snapshot['SnapshotId']
        if snap_id in launch_snap:
            continue
        # print ami['ImageId'], ami['CreationDate']
        # print(snap_id)
        day_old = days_old2(create_date)
        if day_old > age:
            print("deleting -> " + snap_id)
            # deregister the AMI
            client.delete_snapshot(SnapshotId=snap_id)





def lambda_handler(event, context):
    del_ami()
    return ''