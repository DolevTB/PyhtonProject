import boto3
import uuid


# Renames the instances to USERNAME<index>-<uuid
def rename_instances(ec2, instances):
    iam = boto3.client('iam')
    response = iam.get_user()
    unique_id = uuid.uuid4().hex[:6]
    for i in range(len(instances)):
        ec2.create_tags(Resources=[instances[i].id], Tags=[
            {
                "Key": "Name",
                "Value": f"{response['User']['UserName']}-{i + 1}-{unique_id}",
            },
            {
                "Key": "Owner",
                "Value": response['User']['UserName'],
            },
            {
                "Key": "CreatedBy",
                "Value": "CLI " + response['User']['UserName'],
            },
        ])


# Checks weather the key is in available key pairs.
def valid_key_name():
    ec2 = boto3.client('ec2')
    key_pairs = ec2.describe_key_pairs()['KeyPairs']
    available_keys = [kp['KeyName'] for kp in key_pairs]
    chosen_key = ""
    while chosen_key not in available_keys:
        index = 1
        for key in available_keys:
            print(f"{index}. {key}")
            index += 1
        chosen_key = input("Make sure to choose a key (by its name) from the list above!\nDesired Key: ")
    return chosen_key


# Sets a dictionary for configurations
def setting_config_dict():
    config_dict = {}
    flag_instance = False
    flag_image_id = False
    while not flag_instance:
        instance_type = input(
            "Which instance type do you need to set?(Choose 1 or 2)\n1. t3.nano\n2. t4g.nano\nYour choice: ")
        if instance_type == "1":
            config_dict['instance-type'] = "t3.nano"
            print("you chose t3.nano")
            flag_instance = True
        elif instance_type == "2":
            config_dict['instance-type'] = "t4g.nano"
            print("you chose t4g.nano")
            flag_instance = True
        else:
            print("Make sure to type 1 or 2")
    config_dict['key-name'] = valid_key_name()
    while not flag_image_id:
        instance_type = input("Which AMI do you need to set?(Choose 1 or 2)\n1. Ubuntu\n2. Amazon Linux\nYour choice: ")
        if instance_type == "1":
            if config_dict['instance-type'] == "t3.nano":
                config_dict['image-id'] = "ami-04b4f1a9cf54c11d0"
            else:
                config_dict['image-id'] = "ami-0a7a4e87939439934"
            print("you chose Ubuntu")
            flag_image_id = True
        elif instance_type == "2":
            if config_dict['instance-type'] == "t3.nano":
                config_dict['image-id'] = "ami-085ad6ae776d8f09c"
            else:
                config_dict['image-id'] = "ami-0e532fbed6ef00604"
            print("you chose Amazon Linux")
            flag_image_id = True
        else:
            print("Make sure to type 1 or 2")
    config_dict['security-group'] = "sg-0c8e5ab29dfd29316"
    config_dict['SubnetId'] = "subnet-0f7b7bdb55981e7de"
    return config_dict


# Creates number of instances according to the user,
# sets it to enable connection port 80 22 and 3000 and give it with a public  IP
def create_ec2_instance(ec2, number_of_instances):
    config_dict = setting_config_dict()
    instances = ec2.create_instances(
        ImageId=config_dict["image-id"],
        InstanceType=config_dict["instance-type"],
        KeyName=config_dict["key-name"],
        MaxCount=number_of_instances,
        MinCount=1,
        NetworkInterfaces=[
            {
                "SubnetId": config_dict["SubnetId"],
                "DeviceIndex": 0,
                "Groups": [config_dict["security-group"]],
                "AssociatePublicIpAddress": True,
                "DeleteOnTermination": True
            }
        ]
    )
    rename_instances(ec2, instances)
    instance_id = []
    for i in instances:
        i.wait_until_running()
        print(f"This is your private IP {i.private_ip_address}")
        instance_id.append(i.id)


# Creates instances under limitations
def create_instances_limited(ec2):
    flag = False
    number_of_instances = 0
    number = input("Enter the number of instances you would like to set: ")
    while not flag:
        try:
            number_of_instances = int(number)
            assert 0 <= number_of_instances <= 2
        except:
            print("Only 1 or 2 instances can be set or 0 to quit!")
            number = input(
                "Enter the number of instances you would like to set: ")
        else:
            if number_of_instances == 1:
                print("1 instance is being set for you!")
            else:
                print(
                    f"{number_of_instances} instances are being set for you!")
            flag = True
    if number_of_instances > 0:
        create_ec2_instance(ec2, number_of_instances)
        if number_of_instances == 1:
            print("1 instance was set for you!\nGoodbye.")
        else:
            print(
                "2 instances were set for you!\nGoodbye.")
    else:
        print("no instance was set for you!\nGoodbye.")
    input("Enter anything to go back to EC2 menu: ")
