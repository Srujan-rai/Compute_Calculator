import re
import csv
import json
import pandas as pd

with open('knowledge_base.json', 'r') as kb_file:
    knowledge_base = json.load(kb_file)

os_mapping = {
    r"win(dows)?": "Paid: Windows Server",
    r"rhel": "Paid: Red Hat Enterprise Linux",
    r"ubuntu": "Free: Debian, CentOS, CoreOS, Ubuntu or BYOL",
    r"debian": "Free: Debian, CentOS, CoreOS, Ubuntu or BYOL",
    r"sql": "Paid: SQL Server Standard",
    r"free": "Free: Debian, CentOS, CoreOS, Ubuntu or BYOL",
    r"sles(\s*12)?": "Paid: SLES 12 for SAP",
    r"sles(\s*15)?": "Paid: SLES 15 for SAP",
    r"ubuntu\s*pro": "Paid: Ubuntu Pro",
    r"rhel\s*7": "Paid: Red Hat Enterprise Linux 7 with Extended Life Cycle Support",
    r"rhel\s*sap": "Paid: Red Hat Enterprise Linux for SAP with HA and Update Services",
    r"sles": "Paid: SLES"
}

def map_os(value, os_mapping):
    for pattern, replacement in os_mapping.items():
        if re.search(pattern, value, re.IGNORECASE):
            return replacement
    return value  

def map_value(value, knowledge_base):
    for key in knowledge_base:
        if re.search(rf"\b{re.escape(value)}\b", key, re.IGNORECASE):
            return key
    return value 

def process_csv(input_file, output_file):
    df = pd.read_csv(input_file)

    columns_to_map = ["Machine Family", "Series", "Machine Type"]

    for column in columns_to_map:
        if column in df.columns:
            df[column] = df[column].apply(lambda x: map_value(str(x).strip(), knowledge_base) if pd.notnull(x) else x)

    if 'OS with version' in df.columns:
        df['OS with version'] = df['OS with version'].apply(lambda x: map_os(str(x).strip(), os_mapping) if pd.notnull(x) else x)

    df.to_csv(output_file, index=False)

input_file = "resourses/jane new GcpData- - ComputeEngine (1).csv"  # Replace with your input file path
output_file = "output.csv"  

# Process the file
process_csv(input_file, output_file)

print(f"Processed data saved to {output_file}")
