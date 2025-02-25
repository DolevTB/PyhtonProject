import re
import uuid
import boto3
from botocore.exceptions import ClientError
from modules.General_func import who_am_i, clear_terminal


# Checks if the hosted zone already exists
def check_existing_hosted_zone(client, domain_name):
    response = client.list_hosted_zones()
    for zone in response['HostedZones']:
        if zone['Name'] == domain_name + '.':
            return True
    return False


# Lists all hosted zones created by  the user and by the CLI
def list_all_hosted_zone_created_by_cli(client):
    username = who_am_i()
    response = client.list_hosted_zones()
    hosted_zones = response['HostedZones']
    filtered_zones = []
    for zone in hosted_zones:
        zone_id = zone['Id'].split("/")[-1]
        tag_response = client.list_tags_for_resource(
            ResourceType='hostedzone',
            ResourceId=zone_id
        )
        tags = {tag['Key']: tag['Value'] for tag in tag_response['ResourceTagSet']['Tags']}
        if tags.get("Owner") == username and tags.get("CreatedBy") == f"CLI {username}":
            filtered_zones.append(zone['Name'][:-1])
    if not filtered_zones:
        print("No hosted zones were created by you by the CLI")
    return filtered_zones


# Retrieves the hosted zone ID for a given domain
def get_hosted_zone_id(client, domain_name):
    response = client.list_hosted_zones()
    for zone in response['HostedZones']:
        if zone['Name'] == domain_name + '.':
            return zone['Id'].split("/")[-1]
    return None


# Lets you choose only valid host zone
def valid_host_zone(client):
    clear_terminal()
    filtered_host_zones = list_all_hosted_zone_created_by_cli(client)
    chosen_hosted_zone = ""
    if filtered_host_zones:
        filtered_host_zones_string = "This is all the available hosted zones for you:"
        for zone in filtered_host_zones:
            filtered_host_zones_string += f"\n{zone}"
        print(filtered_host_zones_string)
        chosen_hosted_zone = input("Enter your choice, press Enter to exit: ")
        while chosen_hosted_zone and chosen_hosted_zone not in filtered_host_zones:
            print(filtered_host_zones_string)
            chosen_hosted_zone = input("Enter your choice, press Enter to exit: ")
    return chosen_hosted_zone


# Generates base record name
def generate_record_name(record_type, base_domain):
    if record_type in ["A", "AAAA", "MX", "TXT", "NS"]:
        return base_domain
    elif record_type == "CNAME":
        return f"www.{base_domain}"
    elif record_type == "PTR":
        return f"reverse.{base_domain}"
    else:
        raise ValueError(f"Unsupported record type: {record_type}")


# Checks if record exist
def record_exists(client, hosted_zone_id, record_name, record_type):
    response = client.list_resource_record_sets(HostedZoneId=hosted_zone_id)
    for record in response['ResourceRecordSets']:
        if record['Name'] == record_name and record['Type'] == record_type:
            return True
    return False


# Lets you choose only valid record type
def valid_record_type():
    record_types = ["A", "AAAA", "CNAME", "MX", "TXT", "NS", "SOA", "PTR", "SRV", "SPF"]
    records_type_string = "This is all the available record type for you:"
    for record in record_types:
        records_type_string += f"\n{record}"
    print(records_type_string)
    chosen_record_type = input("Enter your choice, press Enter to exit: ")
    while chosen_record_type and chosen_record_type.upper() not in record_types:
        print(records_type_string)
        chosen_record_type = input("Enter your choice, press Enter to exit: ")
    return chosen_record_type.upper()


# Validates that record value based on the record type
def valid_record_value(record_type, record_value):
    if record_type == "A":
        return bool(re.match(
            r"^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){2}(25[0-5]|2[0-4]["
            r"0-9]|[01]?[0-9][0-9]?)$",
            record_value))
    elif record_type == "AAAA":
        return bool(re.match(
            r"^(([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,"
            r"6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,"
            r"4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,"
            r"2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,"
            r"7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]+|::(ffff(:0{1,4})?:)?((25[0-5]|(1[0-9]{2}|[1-9]?[0-9]){"
            r"1,2})(\.(25[0-5]|(1[0-9]{2}|[1-9]?[0-9]){1,2})){3}|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(1[0-9]{2}|["
            r"1-9]?[0-9]){1,2})(\.(25[0-5]|(1[0-9]{2}|[1-9]?[0-9]){1,2})){3}|[0-9a-fA-F]{1,4})))$",
            record_value))
    elif record_type == "CNAME":
        return bool(re.match(r"^[a-zA-Z0-9.-]+$", record_value))
    elif record_type == "MX":
        return bool(re.match(r"^[a-zA-Z0-9.-]+$", record_value))
    elif record_type == "TXT":
        return isinstance(record_value, str)
    elif record_type == "NS":
        return bool(re.match(r"^[a-zA-Z0-9.-]+$", record_value))
    elif record_type == "PTR":
        return bool(re.match(r"^[a-zA-Z0-9.-]+$", record_value))
    else:
        raise ValueError(f"Unsupported record type: {record_type}")


# Gets input from user about record value
def get_record_value(record_type):
    record_value = input("Please enter valid value according to chosen record type, press Enter to exit: ")
    while record_value and not valid_record_value(record_type, record_value):
        record_value = input("Please enter valid value according to chosen record type, press Enter to exit: ")
    return record_value


# Changes dns record by action
def change_dns_record(domain_name, record_name, record_type, record_value, action):
    client = boto3.client('route53')
    hosted_zone_id = get_hosted_zone_id(client, domain_name)
    if action == "DELETE" and not record_exists(client, hosted_zone_id, record_name, record_type):
        print(f"Record {record_name} of type {record_type} does not exist. Cannot delete.")
        return
    if action == "CREATE" and record_exists(client, hosted_zone_id, record_name, record_type):
        print(f"Record {record_name} of type {record_type} already exists. Consider updating instead.")
        return
    change_batch = {
        "Changes": [
            {
                "Action": action,
                "ResourceRecordSet": {
                    "Name": record_name,
                    "Type": record_type,
                    "TTL": 300,
                    "ResourceRecords": [{"Value": record_value}]
                }
            }
        ]
    }
    try:
        response = client.change_resource_record_sets(
            HostedZoneId=hosted_zone_id,
            ChangeBatch=change_batch
        )
        print(
            f"{action} request submitted for {record_name} ({record_type}). Change ID: {response['ChangeInfo']['Id']}")
    except ClientError as e:
        print(f"Error: {e}")
        pass


# Creates a hosted zone based on user input
def create_hosted_zone(client):
    domain_name = ""
    flag_not_used_domain = False
    while not flag_not_used_domain:
        while not domain_name or domain_name[0] == ".":
            clear_terminal()
            domain_name = input("Enter domain name(must not start on \".\"): ").strip()
            domain_name = re.sub(r'\.{2,}', '.', domain_name)
        if "." not in domain_name:
            domain_name += ".com"
        elif domain_name[-1] == ".":
            domain_name += "com"
        if check_existing_hosted_zone(client, domain_name):
            print(f"Domain '{domain_name}' already exists in Route 53. Try another name.")
        else:
            flag_not_used_domain = True
    response = client.create_hosted_zone(
        Name=domain_name + ".",
        CallerReference=str(uuid.uuid4()) + domain_name,
        HostedZoneConfig={
            'Comment': 'Zone created by CLI',
            'PrivateZone': False
        }
    )
    hosted_zone_id = response['HostedZone']['Id'].split("/")[-1]
    print(f"Hosted Zone created successfully! ID: {hosted_zone_id}")
    username = who_am_i()
    client.change_tags_for_resource(
        ResourceType="hostedzone",
        ResourceId=hosted_zone_id,
        AddTags=[
            {"Key": "Owner", "Value": username},
            {"Key": "CreatedBy", "Value": f"CLI {username}"}
        ]
    )


# Lists all records in a hosted zone
def list_records(client, hosted_zone_id):
    response = client.list_resource_record_sets(HostedZoneId=hosted_zone_id)
    records = []
    for record in response['ResourceRecordSets']:
        records.append({
            'Name': record['Name'][:-1],
            'Type': record['Type'],
            "TTL": 300,
            'Value': [value['Value'] for value in record['ResourceRecords']]
        })
    return records


# Chooses a records in a hosted zone
def choose_records_available(client, hosted_zone_id, action):
    records = list_records(client, hosted_zone_id)
    list_choice_by_index = []
    all_records_string = f"Available records to {action}:\n"
    for i, record in enumerate(records):
        all_records_string += (f"{i + 1}. Name: {record['Name']}, Type: {record['Type']}, Values: "
                               f" {', '.join(record['Value'])}\n")
        list_choice_by_index.append(str(i + 1))
    print(all_records_string)
    record_chosen = input(f"Enter the record you want to {action} (choose by index), press Enter to exit: ")
    while record_chosen and record_chosen not in list_choice_by_index:
        print(all_records_string)
        record_chosen = input(f"Enter the record you want to {action} (choose by index), press Enter to exit: ")
    if not record_chosen:
        return record_chosen
    print(records[int(record_chosen) - 1]['Value'])
    return (records[int(record_chosen) - 1]['Name'] + ".",
            records[int(record_chosen) - 1]['Type'], records[int(record_chosen) - 1]['Value'][0])


# CLI for existing hosted zone
def manage_hosted_zone(client, domain_name):
    flag_done = False
    options = ["1", "2", "3", "4"]
    menu = (fr"""How do you want to manage:
1. Create dns record in {domain_name}.
2. Update dns record in {domain_name}.
3. Delete dns records in {domain_name}.
4. Go back to Route53 menu.
Enter your choice:
-------------------------------
""")
    actions = ["", "CREATE", "UPSERT", "DELETE"]
    CREATE = "1"
    UPSERT = "2"
    EXIT = "4"
    while not flag_done:
        clear_terminal()
        what_to_do = input(menu)
        while what_to_do not in options:
            clear_terminal()
            what_to_do = input(menu)
        if what_to_do != EXIT:
            action = actions[int(what_to_do)]
            if what_to_do == CREATE:
                record_type = valid_record_type()
                record_name = generate_record_name(record_type, domain_name)
                record_value = get_record_value(record_type)
            else:
                host_zone_id = get_hosted_zone_id(client, domain_name)
                record_name, record_type, record_value = choose_records_available(client, host_zone_id, action)
                if what_to_do == UPSERT:
                    record_value = get_record_value(record_type)
            change_dns_record(domain_name, record_name, record_type, record_value, action)
            input(f"Enter anything to go back to managing {domain_name} : ")
        else:
            flag_done = True


# Deletes all the records
def delete_all_records(client, hosted_zone_id):
    try:
        response = client.list_resource_record_sets(HostedZoneId=hosted_zone_id)
        record_sets = response['ResourceRecordSets']
        for record in record_sets:
            try:
                client.change_resource_record_sets(
                    HostedZoneId=hosted_zone_id,
                    ChangeBatch={
                        'Changes': [{
                            'Action': 'DELETE',
                            'ResourceRecordSet': record
                        }]
                    }
                )
                print(f"Deleted record: {record['Name']} of type {record['Type']}")
            except ClientError:
                continue
    except ClientError:
        pass


# Deletes hosted zone
def delete_hosted_zone(client, hosted_zone_id):
    delete_all_records(client, hosted_zone_id)
    try:
        client.delete_hosted_zone(Id=hosted_zone_id)
        print(f"Hosted zone {hosted_zone_id} deleted successfully.")
    except ClientError:
        print(f"Can't delete")


# Main CLI for route 53 part
def cli_route_53():
    client = boto3.client('route53')
    flag_done = False
    options = ["1", "2", "3", "4"]
    domain_name = ""
    menu = (r"""What do you want to do:
1. Create a hosted zone.
2. Manage an existing hosted zone.
3. Delete an existing hosted zone.
4. Go back to main menu.
Enter your choice:
-------------------------------
""")
    while not flag_done:
        clear_terminal()
        what_to_do = input(menu)
        while what_to_do not in options:
            clear_terminal()
            what_to_do = input(menu)
        if what_to_do == "1":
            create_hosted_zone(client)
            input("Enter anything to go back to Route53 menu: ")
        elif what_to_do == "2":
            try:
                domain_name = valid_host_zone(client)
                if domain_name:
                    manage_hosted_zone(client, domain_name)
            except:
                continue
            input(f"Enter anything to go back to managing {domain_name} : ")
        elif what_to_do == "3":
            try:
                id_to_delete = get_hosted_zone_id(client, valid_host_zone(client))
                delete_hosted_zone(client, id_to_delete)
                input("Enter anything to go back to Route53 menu: ")
            except:
                print(f"Can't delete")
                input("Enter anything to go back to Route53 menu: ")
        else:
            flag_done = True
