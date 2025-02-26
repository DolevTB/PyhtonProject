from modules.ec2 import cli_ec2
from modules.Route53 import cli_route_53
from modules.S3 import cli_bucket
from modules.General_func import clear_terminal


# Make sure to download AWSCLI and set aws configure.
# Main menu of the project
def cli():
    flag_done = False
    options = ["1", "2", "3", "4"]
    EC2 = "1"
    S3 = "2"
    ROUTE53 = "3"
    menu = (r"""What do you want to do:
1. EC2 service.
2. S3 service.
3. Route53 Service.
4. Exit the code.
Enter your choice:
-------------------------------
""")
    while not flag_done:
        clear_terminal()
        what_to_do = input(menu)
        while what_to_do not in options:
            clear_terminal()
            what_to_do = input(menu)
        if what_to_do == EC2:
            print("***Entering EC2 menu!!!***")
            cli_ec2()
        elif what_to_do == S3:
            print("***Entering S3 menu!!!***")
            cli_bucket()
        elif what_to_do == ROUTE53:
            print("***Entering Route53 menu!!!***")
            cli_route_53()
        else:
            flag_done = True

try:
    cli()
except KeyboardInterrupt:
    exit()
