from modules.creator import *
from modules.terminator import *
import boto3
from modules.General_func import clear_terminal


# Main CLI for ec2
def cli_ec2():
    ec2 = boto3.resource("ec2", region_name="us-east-1")
    flag_done = False
    options = ["1", "2", "3", "4", "5", "6"]
    CREATE = "1"
    LIST = "2"
    STOP = "3"
    DELETE = "4"
    RESTART = "5"
    menu = (r"""What do you want to do:
1. Create 1 or 2 ec2 instances.
2. List all ec2 that were created by this user via CLI.
3. Stop an existing instance.
4. Delete an existing instance.
5. Restart a stopped instance.
6. Go back to main menu.
Enter your choice:
-------------------------------
""")
    while not flag_done:
        clear_terminal()
        what_to_do = input(menu)
        while what_to_do not in options:
            clear_terminal()
            what_to_do = input(menu)
        if what_to_do == CREATE:
            create_instances_limited(ec2)
        elif what_to_do == LIST:
            action_ec2_instance(ec2, "list all")
        elif what_to_do == STOP:
            print("***You are going to ***STOP*** the chosen ec2!!!***")
            action_ec2_instance(ec2, "stop")
        elif what_to_do == DELETE:
            print("***You are going to ***TERMINATE*** the chosen ec2!!!***")
            action_ec2_instance(ec2, "terminate")
        elif what_to_do == RESTART:
            action_ec2_instance(ec2, "restart")
        else:
            flag_done = True
