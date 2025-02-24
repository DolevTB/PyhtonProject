import boto3
from tabulate import tabulate
from modules.General_func import who_am_i


# Lists all instances created by this user via CLI
def list_instances_created_by_me_and_by_cli(action):
    ec2 = boto3.client("ec2")
    state_map = {
        "restart": ['stopped'],
        "stop": ['running'],
        "terminate": ['running', 'stopped'],
        "list all": ['pending', 'running', 'stopping', 'stopped', 'shutting-down', 'terminated']
    }
    states = state_map.get(action)
    username = who_am_i()
    custom_filter = [
        {'Name': 'tag:CreatedBy', 'Values': [f"CLI {username}"]},
        {'Name': 'tag:Owner', 'Values': [username]},
        {'Name': 'instance-state-name', 'Values': states}
    ]
    try:
        response = ec2.describe_instances(Filters=custom_filter)
    except Exception as e:
        print(f"Error describing instances: {e}")
        return []
    if 'Reservations' not in response or not response['Reservations']:
        return []
    instances = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            state = instance['State']['Name']
            name_tag = next(
                (tag['Value'] for tag in instance.get('Tags', []) if tag['Key'] == 'Name'),
                "Unknown"
            )
            instances.append([instance_id, name_tag, state])
    return instances


# Prints nicely
def print_instances_by_action(action):
    print(tabulate(list_instances_created_by_me_and_by_cli(action),
                   headers=["Instance ID", "Name", "State"], tablefmt="grid"))


# Validates the chosen instance:
def valid_instance(action):
    instance_list = []
    try:
        for instance in list_instances_created_by_me_and_by_cli(action):
            instance_list.append(instance[0])
    except:
        pass
    if not instance_list:
        return ""
    instance_string = "This is all the available instances for you:\n"
    instance_string += f"{tabulate(list_instances_created_by_me_and_by_cli(action),
                                   headers=["Instance ID", "Name", "State"], tablefmt="grid")}"
    print(instance_string)
    chosen_instance = input("Enter your choice, press Enter to exit: ")
    while chosen_instance and chosen_instance not in instance_list:
        print(instance_string)
        chosen_instance = input("Enter your choice, press Enter to exit: ")
    return chosen_instance


# terminates all instances under my the name Dolev that were created over a week
def action_ec2_instance(ec2, action):
    if action == "list all":
        print_instances_by_action(action)
    else:
        instance_to_action = valid_instance(action)
        if instance_to_action:
            print(f"This is the instance you are going to {action}:")
            assure = input(f"Are sure you want to {action} {instance_to_action}?\nType yes if you want to proceed: ")
            if assure.lower() in ["yes", "y"]:
                instances = ec2.Instance(instance_to_action)
                if action == "terminate":
                    instances.terminate()
                    print("Terminated instances: ", instance_to_action)
                elif action == "stop":
                    instances.stop()
                    print("Stopped instances: ", instance_to_action)
                elif action == "restart":
                    instances.start()
                    print("Started instances: ", instance_to_action)
        else:
            print(f"No instances were created by you via CLI in the right state for you to {action}")
    input("Enter anything to go back to EC2 menu: ")
