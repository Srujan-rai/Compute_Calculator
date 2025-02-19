# AWS SNS

#!/bin/bash

# Combined Bash and Python script to fetch AWS SNS details

# Output file
python_script="sns_fetch.py"
output_file="sns_details.xlsx"

# Ensure AWS CLI and jq are installed
if ! command -v aws &>/dev/null || ! command -v jq &>/dev/null; then
    echo "Error: AWS CLI and jq must be installed."

fi

# Check for required Python libraries
if ! python3 -c "import boto3, pandas" &>/dev/null; then
    echo "Python libraries boto3 and pandas are required. Installing..."
    pip install boto3 pandas
fi

# Fetch all SNS topics
topics=$(aws sns list-topics --output json 2>/dev/null | jq -r '.Topics[].TopicArn')
if [[ -z "$topics" ]]; then
    echo "No topics found or failed to retrieve topics."

fi

# Create the Python script dynamically
cat << 'EOF' > $python_script
import boto3
import pandas as pd
import sys

def fetch_sns_details(topic_arn):
    sns_client = boto3.client('sns')
    result = {}

    try:
        # Fetch topic attributes
        attributes = sns_client.get_topic_attributes(TopicArn=topic_arn)
        result['Attributes'] = attributes.get('Attributes', {})
    except Exception as e:
        result['Error'] = f"Error fetching attributes: {str(e)}"
        return result

    try:
        # Fetch subscriptions
        subscriptions = sns_client.list_subscriptions_by_topic(TopicArn=topic_arn)
        result['Subscriptions'] = subscriptions.get('Subscriptions', [])
    except Exception as e:
        result['Error'] = f"Error fetching subscriptions: {str(e)}"

    return result

def save_to_excel(data, filename):
    # Consolidate all data into a single DataFrame
    consolidated_data = []

    for topic_data in data:
        attributes = topic_data.get("Attributes", {})
        subscriptions = topic_data.get("Subscriptions", [])
        
        # Extract topic details
        topic_name = attributes.get("DisplayName", "N/A")
        topic_arn = attributes.get("TopicArn", "N/A")
        delivery_policy = attributes.get("DeliveryPolicy", "N/A")
        
        if subscriptions:
            for subscription in subscriptions:
                consolidated_data.append({
                    "Topic Name": topic_name,
                    "Topic ARN": topic_arn,
                    "T Display Name": topic_name,  # Same as Topic Name
                    "Delivery Policy": delivery_policy,
                    "Subscription ARN": subscription.get("SubscriptionArn", "N/A"),
                    "Subscription Protocol": subscription.get("Protocol", "N/A"),
                    "Endpoint": subscription.get("Endpoint", "N/A")
                })
        else:
            consolidated_data.append({
                "Topic Name": topic_name,
                "Topic ARN": topic_arn,
                "T Display Name": topic_name,
                "Delivery Policy": delivery_policy,
                "Subscription ARN": "N/A",
                "Subscription Protocol": "N/A",
                "Endpoint": "N/A"
            })

    # Save to Excel
    df = pd.DataFrame(consolidated_data)
    df.to_excel(filename, index=False)
    print(f"Data saved to {filename}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print({"Error": "Please provide Topic ARNs and an output file as arguments"})
        

    output_file = sys.argv[-1]
    topic_arns = sys.argv[1:-1]

    all_topic_details = []

    for topic_arn in topic_arns:
        details = fetch_sns_details(topic_arn)
        details["TopicArn"] = topic_arn
        all_topic_details.append(details)

    save_to_excel(all_topic_details, output_file)
EOF

# Execute the Python script
python3 $python_script $topics $output_file
if [[ $? -eq 0 ]]; then
    echo "Excel file $output_file created successfully!"
else
    echo "Failed to create Excel file."
fi

# Clean up temporary Python script
rm -f $python_script


#======================================================================================================================================#

#aws DMS

#!/bin/bash

# Output files
output_file="dms_info.csv"
log_file="error.log"
excel_output_file="dms-tracker-output.xlsx"

# Function to log messages with timestamps
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$log_file"
}

# Check for required dependencies
log_message "Checking dependencies..."
if ! command -v aws &>/dev/null; then
    log_message "Error: AWS CLI is not installed. Please install it."

fi

if ! command -v jq &>/dev/null; then
    log_message "Error: jq is not installed. Please install it."

fi

if ! command -v python3 &>/dev/null; then
    log_message "Error: Python3 is not installed. Please install it."

fi

# Ensure necessary Python libraries are installed
for package in pandas xlsxwriter; do
    if ! python3 -c "import $package" &>/dev/null; then
        log_message "Installing Python package: $package..."
        pip install $package
    fi
done

# Create an empty CSV file with headers
echo "Endpoint Type,Endpoint ARN,Source Database Type,Target Database Type,Migration Type" > "$output_file"

log_message "Starting to gather DMS information..."

# Get a list of all DMS endpoints
endpoints=$(aws dms describe-endpoints --output json 2>> "$log_file")
if [[ $? -ne 0 ]]; then
    log_message "Error retrieving DMS endpoints. Exiting."

fi

# Get replication task info to find migration types
replication_tasks=$(aws dms describe-replication-tasks --output json 2>> "$log_file")
if [[ $? -ne 0 ]]; then
    log_message "Error retrieving replication tasks. Exiting."

fi

# Loop through each endpoint and extract required information
echo "$endpoints" | jq -r '.Endpoints[] | 
    "\(.EndpointType),\(.EndpointArn),\(.EngineName),\(.EngineName)"' > temp_dms.csv

# Add migration types for each replication task
while IFS=, read -r endpoint_type endpoint_arn source_db_type target_db_type; do
    migration_type=$(echo "$replication_tasks" | jq -r --arg arn "$endpoint_arn" '
        .ReplicationTasks[] | 
        select(.SourceEndpointArn==$arn or .TargetEndpointArn==$arn) | .MigrationType')

    # Check if migration_type is "full-load", "cdc", or "full-load-and-cdc"
    if [[ -z "$migration_type" ]]; then
        migration_type="No Task"
    elif [[ "$migration_type" == "full-load" ]]; then
        migration_type="Full Load"
    elif [[ "$migration_type" == "cdc" ]]; then
        migration_type="CDC"
    elif [[ "$migration_type" == "full-load-and-cdc" ]]; then
        migration_type="Full Load and CDC"
    else
        migration_type="Unknown Type"
    fi

    log_message "Processing Endpoint ARN: $endpoint_arn | Migration Type: $migration_type"
    echo "$endpoint_type,$endpoint_arn,$source_db_type,$target_db_type,$migration_type" >> "$output_file"
done < temp_dms.csv

rm temp_dms.csv
log_message "DMS information gathered successfully and saved to $output_file."

# Python code for CSV to Excel conversion
temp_python_script="dms_to_excel.py"
cat << 'EOF' > $temp_python_script
import pandas as pd
import sys

input_csv = sys.argv[1]
output_excel = sys.argv[2]

df = pd.read_csv(input_csv)
writer = pd.ExcelWriter(output_excel, engine='xlsxwriter')
df.to_excel(writer, sheet_name='DMS Data', index=False)
writer.close()
print(f"Completed: Data saved to {output_excel}")
EOF

# Run the Python script
python3 $temp_python_script "$output_file" "$excel_output_file" 2>> "$log_file"
if [[ $? -eq 0 ]]; then
    log_message "Excel file created successfully: $excel_output_file."
else
    log_message "Error converting CSV to Excel."
fi

# Cleanup temporary Python script
rm -f $temp_python_script

log_message "Script execution completed."


#===========================================================================================================================================#

#AWS KINESIS STREAM

#!/bin/bash

# Output files
output_file="kinesis_info.csv"
log_file="error.log"
excel_output_file="kinesis_info.xlsx"
json_output_file="kinesis_info.json"

# Function to log messages with timestamps
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$log_file"
}

# Create an empty CSV file with headers
echo "Stream Name,Stream ARN,Retention Period (hours),Data Producers,Consumers" > "$output_file"

# Initialize an empty JSON structure
echo '{"KinesisStreams": []}' > "$json_output_file"

log_message "Starting to gather Kinesis stream information..."

# Get a list of all Kinesis streams with pagination support
streams=$(aws kinesis list-streams --output json 2>> "$log_file")
if [[ $? -ne 0 ]]; then
    log_message "Error retrieving Kinesis streams. Exiting."

fi

#producer info
get_data_producers() {
    local stream_name=$1
    local producers=""

    # Query CloudTrail for both PutRecord and PutRecords events for this stream
    local start_time=$(date -u -d "-1 hour" '+%Y-%m-%dT%H:%M:%SZ')  # Adjust time range as needed
    local end_time=$(date -u '+%Y-%m-%dT%H:%M:%SZ')

    cloudtrail_events=$(aws cloudtrail lookup-events \
                        --lookup-attributes AttributeKey=EventName,AttributeValue=PutRecord \
                        --lookup-attributes AttributeKey=EventName,AttributeValue=PutRecords \
                        --lookup-attributes AttributeKey=ResourceName,AttributeValue="$stream_name" \
                        --start-time "$start_time" --end-time "$end_time" \
                        --max-results 50 --output json 2>> "$log_file")

    if [[ $? -eq 0 ]]; then
        # Process paginated results
        local next_token=$(echo "$cloudtrail_events" | jq -r '.NextToken // empty')
        while [[ -n "$next_token" ]]; do
            local additional_events=$(aws cloudtrail lookup-events \
                                      --lookup-attributes AttributeKey=EventName,AttributeValue=PutRecord \
                                      --lookup-attributes AttributeKey=EventName,AttributeValue=PutRecords \
                                      --lookup-attributes AttributeKey=ResourceName,AttributeValue="$stream_name" \
                                      --start-time "$start_time" --end-time "$end_time" \
                                      --max-results 50 --next-token "$next_token" \
                                      --output json 2>> "$log_file")
            cloudtrail_events=$(jq -s '.[0].Events + .[1].Events' <(echo "$cloudtrail_events") <(echo "$additional_events"))
            next_token=$(echo "$additional_events" | jq -r '.NextToken // empty')
        done

        # Filter out internal AWS services and get unique user identities
        producers=$(echo "$cloudtrail_events" | \
                    jq -r '.Events[] | select(.Username | startswith("AWS:") | not) | .Username' | \
                    sort -u | \
                    paste -sd "," -)

        if [[ -z "$producers" ]]; then
            producers="None"
        fi
    else
        log_message "Error retrieving data producers for stream $stream_name from CloudTrail."
        producers="Unknown"
    fi

    echo "$producers"
}



# Function to fetch consumers for a given stream (both enhanced fan-out and Firehose)
get_consumers() {
    local stream_arn=$1
    local stream_name=$2
    consumers=$(aws kinesis list-stream-consumers --stream-arn "$stream_arn" --output json 2>> "$log_file")
    
    if [[ $? -ne 0 ]]; then
        log_message "Error retrieving consumers for stream $stream_arn. Skipping."
        echo "None"
        return
    fi

    # Extract consumer names from the response using jq for enhanced fan-out consumers.
    consumer_names=$(echo "$consumers" | jq -r '.Consumers[] | .ConsumerName, .ConsumerStatus, .ConsumerCreationTimestamp' | paste -sd "," -)
    
    if [[ -z "$consumer_names" ]]; then
        consumer_names="None"
    fi

    # Check if Firehose is consuming from this stream by listing delivery streams and checking the source.
    firehose_streams=$(aws firehose list-delivery-streams --output json 2>> "$log_file")
    
    firehose_consumer=""
    
    for delivery_stream in $(echo "$firehose_streams" | jq -r '.DeliveryStreamNames[]'); do
        firehose_info=$(aws firehose describe-delivery-stream --delivery-stream-name "$delivery_stream" --output json 2>> "$log_file")
        
        # Check if the source of the Firehose delivery stream is the current Kinesis stream.
        firehose_source_stream=$(echo "$firehose_info" | jq -r '.DeliveryStreamDescription.Source.KinesisStreamSourceDescription.KinesisStreamARN // empty')
        
        if [[ "$firehose_source_stream" == "$stream_arn" ]]; then
            # Check if Firehose is actively consuming data from this stream
            delivery_stream_status=$(echo "$firehose_info" | jq -r '.DeliveryStreamDescription.DeliveryStreamStatus')
            if [[ "$delivery_stream_status" == "ACTIVE" ]]; then
                firehose_consumer="$delivery_stream (Firehose)"
                break
            fi
        fi
    done

    # If Firehose is consuming, append it to the list of consumers.
    if [[ -n "$firehose_consumer" ]]; then
        if [[ "$consumer_names" == "None" ]]; then
            consumer_names="$firehose_consumer"
        else
            consumer_names="$consumer_names, $firehose_consumer"
        fi
    fi

    echo "$consumer_names"
}

# Loop through each stream and extract required information
echo "$streams" | jq -r '.StreamNames[]' | while read -r stream_name; do
    log_message "Processing stream: $stream_name"

    stream_info=$(aws kinesis describe-stream --stream-name "$stream_name" --output json 2>> "$log_file")
    
    if [[ $? -ne 0 ]]; then
        log_message "Error retrieving details for stream $stream_name. Skipping."
        continue
    fi

    stream_arn=$(echo "$stream_info" | jq -r '.StreamDescription.StreamARN')
    retention_period=$(echo "$stream_info" | jq -r '.StreamDescription.RetentionPeriodHours')

    # Fetch data producers using the actual logic
    data_producers=$(get_data_producers "$stream_name")

    # Fetch consumers for the current stream using the ARN of the stream (including Firehose check)
    consumers=$(get_consumers "$stream_arn" "$stream_name")

    # Remove trailing comma and space from data_producers if necessary
    data_producers=$(echo "$data_producers" | sed 's/, $//')
    
    if [[ -z "$data_producers" ]]; then
        data_producers="Unknown"
    fi

    echo "Data Producers for stream '$stream_name': $data_producers"  # Debug log
    log_message "Data Producers for stream '$stream_name': $data_producers"

    # Remove trailing comma and space from consumers if necessary.
    consumers=$(echo "$consumers" | sed 's/, $//')
    
    if [[ -z "$consumers" ]]; then
        consumers="None"
    fi

    # Append data to CSV file for Excel conversion later on, ensure proper commas between fields.
    echo "\"$stream_name\",\"$stream_arn\",\"$retention_period\",\"$data_producers\",\"$consumers\"" >> "$output_file"

    # Append information to the JSON output file using jq (make sure to insert properly formatted JSON)
    jq --arg name "$stream_name" \
       --arg arn "$stream_arn" \
       --argjson retention_period "$retention_period" \
       --arg producers "$data_producers" \
       --arg consumers "$consumers" \
       '.KinesisStreams += [{"StreamName": $name, "StreamARN": $arn, "RetentionPeriodHours": $retention_period, "DataProducers": $producers, "Consumers": $consumers}]' \
       "$json_output_file" > tmp.json && mv tmp.json "$json_output_file"

done

log_message "Kinesis stream information gathered successfully and saved to $output_file and $json_output_file"

# Call Python script to create Excel file from CSV file 
python3 <<EOF
import pandas as pd

# Load the CSV file with proper handling of quotes and commas.
csv_file = "$output_file"
excel_file = "$excel_output_file"

try:
    # Read the CSV file into a DataFrame and save as Excel.
    df = pd.read_csv(csv_file)
    
    # Ensure that all columns are correctly mapped.
    df.columns = ["Stream Name", "Stream ARN", "Retention Period (hours)", "Data Producers", "Consumers"]
    
    # Save DataFrame as Excel file.
    df.to_excel(excel_file, index=False)
    
    print("Excel file created successfully:", excel_file)
except Exception as e:
    print("Failed to create Excel file:", e)
EOF

if [[ $? -eq 0 ]]; then
    log_message "Excel file created: $excel_output_file"
else
    log_message "Error creating Excel file"
fi


#========================================================================================================================================#

#AWS KINESIS FIREHOSE
#!/bin/bash

# List of standard AWS regions to search in
regions=(
    "us-east-1" "us-east-2" "us-west-1" "us-west-2"
    "eu-west-1" "eu-west-2" "eu-west-3" "eu-central-1"
    "ap-southeast-1" "ap-southeast-2" "ap-northeast-1"
    "ap-northeast-2" "ap-south-1" "sa-east-1"
)

# Initialize an array to store found streams
found_streams=()

# Iterate over each region to find delivery streams
for region in "${regions[@]}"; do
    echo "Searching in region: $region"

    # List delivery streams in the current region
    streams=$(aws firehose list-delivery-streams --region "$region" --query "DeliveryStreamNames[]" --output json | jq -r '.[]')

    # Check if there are any streams and add them to the list
    if [ -n "$streams" ]; then
        for stream in $streams; do
            found_streams+=("$region:$stream")
        done
    fi
done

# Check if any streams were found
if [ ${#found_streams[@]} -eq 0 ]; then
    echo "No Firehose delivery streams found in any region."

fi

# Prepare JSON data for Excel conversion
json_data="["

for stream_info in "${found_streams[@]}"; do
    IFS=":" read -r region stream_name <<< "$stream_info"
    
    # Fetch the delivery stream information for each found stream
    firehose_info=$(aws firehose describe-delivery-stream --region "$region" --delivery-stream-name "$stream_name" --query "DeliveryStreamDescription" --output json)

    # Identify destination type and extract details accordingly
    destination_type=$(echo "$firehose_info" | jq -r '.Destinations[0] | if .S3DestinationDescription then "S3" elif .RedshiftDestinationDescription then "Redshift" elif .ElasticsearchDestinationDescription then "Elasticsearch" elif .HttpEndpointDestinationDescription then "HTTP Endpoint" else "Unknown" end')

    # Extract destination name based on type
    if [ "$destination_type" == "S3" ]; then
        destination_name=$(echo "$firehose_info" | jq -r '.Destinations[0].S3DestinationDescription.BucketARN | split(":")[5]')
    elif [ "$destination_type" == "Redshift" ]; then
        destination_name=$(echo "$firehose_info" | jq -r '.Destinations[0].RedshiftDestinationDescription.ClusterJDBCURL')
    elif [ "$destination_type" == "Elasticsearch" ]; then
        destination_name=$(echo "$firehose_info" | jq -r '.Destinations[0].ElasticsearchDestinationDescription.DomainARN')
    elif [ "$destination_type" == "HTTP Endpoint" ]; then
        destination_name=$(echo "$firehose_info" | jq -r '.Destinations[0].HttpEndpointDestinationDescription.EndpointConfiguration.Url')
    else
        destination_name="Unknown"
    fi

    # Extract specific source name (e.g., Kinesis Data Stream ARN or Direct PUT)
    source_name=$(echo "$firehose_info" | jq -r '.Source.KinesisStreamSourceDescription.KinesisStreamARN // "Direct PUT or Other Source Type"')

    # Extract full Lambda function ARN for data transformation, handle missing values safely
    lambda_arn=$(echo "$firehose_info" | jq -r '.Destinations[0].ExtendedS3DestinationDescription.ProcessingConfiguration.Processors[].Parameters[]? | select(.ParameterName=="LambdaArn").ParameterValue // "N/A"' | head -n 1)

    # Extract data format conversion details
    data_format_conversion=$(echo "$firehose_info" | jq -c '.Destinations[0].ExtendedS3DestinationDescription.DataFormatConversionConfiguration // {"Enabled": false}')

    # Extract additional details for headers
    s3_backup_configuration=$(echo "$firehose_info" | jq -r '.Destinations[0].S3BackupMode // "N/A"')
    buffer_size=$(echo "$firehose_info" | jq -r '.Destinations[0].ExtendedS3DestinationDescription.BufferingHints.SizeInMBs // "N/A"')
    buffer_interval=$(echo "$firehose_info" | jq -r '.Destinations[0].ExtendedS3DestinationDescription.BufferingHints.IntervalInSeconds // "N/A"')
    compression_format=$(echo "$firehose_info" | jq -r '.Destinations[0].ExtendedS3DestinationDescription.CompressionFormat // "N/A"')

    output_json=$(jq -n \
        --arg arn "$(echo "$firehose_info" | jq -r '.DeliveryStreamARN')" \
        --arg source_name "$source_name" \
        --arg destination_type "$destination_type ($destination_name)" \
        --arg s3_backup_configuration "$s3_backup_configuration" \
        --arg buffer_size "$buffer_size" \
        --arg buffer_interval "$buffer_interval" \
        --arg compression_format "$compression_format" \
        --arg lambda_arn "$lambda_arn" \
        --argjson data_format_conversion "$data_format_conversion" \
        '{
            "DeliveryStreamARN": $arn,
            "Source": $source_name,
            "DestinationType": $destination_type,
            "S3BackupConfiguration": $s3_backup_configuration,
            "BufferSizeMB": $buffer_size,
            "BufferIntervalSeconds": $buffer_interval,
            "CompressionFormat": $compression_format,
            "DataTransformationLambda": $lambda_arn,
            "DataFormatConversion": $data_format_conversion
        }')

    json_data+="$output_json,"
done

# Remove trailing comma and close JSON array
json_data="${json_data%,}]"

# Save JSON to a temporary file
json_file="firehose_info.json"
echo "$json_data" > "$json_file"

# Convert JSON to Excel using Python with XlsxWriter
python3 <<EOF
import json
import xlsxwriter

# Load JSON data from the file
json_file_path = '$json_file'
with open(json_file_path, 'r') as file:
    data = json.load(file)

# Create a new Excel file and add a worksheet
workbook = xlsxwriter.Workbook('firehose_info.xlsx')
worksheet = workbook.add_worksheet('FirehoseInfo')

# Define the headers
headers = [
    'Delivery Stream ARN',
    'Source',
    'Destination',
    'S3 Backup Configuration',
    'Buffer Size (MB)',
    'Buffer Interval (Seconds)',
    'Compression Format',
    'Data Transformation (AWS Lambda Function)',
    'Data Format Conversion'
]

# Write the headers
for col_num, header in enumerate(headers):
    worksheet.write(0, col_num, header)

# Write the data rows for each stream found
for row_num, stream_data in enumerate(data, start=1):
    data_row = [
        stream_data.get('DeliveryStreamARN'),
        stream_data.get('Source', 'N/A'),
        stream_data.get('DestinationType'),
        stream_data.get('S3BackupConfiguration', 'N/A'),
        stream_data.get('BufferSizeMB'),
        stream_data.get('BufferIntervalSeconds'),
        stream_data.get('CompressionFormat'),
        stream_data.get('DataTransformationLambda', 'N/A'),
        json.dumps(stream_data.get('DataFormatConversion', {}))
    ]
    
    for col_num, value in enumerate(data_row):
        worksheet.write(row_num, col_num, value)

# Close the workbook after all entries are written
workbook.close()

print("Excel file 'firehose_info.xlsx' created successfully.")
EOF


#===============================================================================================================================================#

#AWS LAMDA

#!/bin/bash

# Output file
#!/bin/bash

# Log file to track errors and progress
log_file="error.log"
> "$log_file"  # Clear log file

# Temporary CSV file
output_file="temp_lambda.csv"
> "$output_file"  # Clear output file

# CSV Header
echo "Account ID, Function Name, Region, Runtime, Timeout, Memory Size, Architecture, Ephemeral Storage, Layers, Handler" >> "$output_file"

# AWS Account ID (replace this with actual value or retrieve dynamically)
account_id="your-account-id"

# List of AWS regions to iterate over
regions=$(aws ec2 describe-regions --query "Regions[].RegionName" --output text)

for region in $regions; do
  echo "Processing region: $region" >> "$log_file"

  # Get the list of Lambda functions in the region
  functions=$(aws lambda list-functions --region "$region" --output json 2>> "$log_file")

  # Check if the output is empty or no functions are found
  if [[ -z "$functions" || "$functions" == "[]" ]]; then
    echo "No functions found in region $region" >> "$log_file"
    continue
  fi

  # Process JSON with jq
  jq_output=$(echo "$functions" | jq -r --arg region "$region" --arg account_id "$account_id" '
    .Functions[] |
    "\($account_id), \(.FunctionName), \($region), \(.Runtime), \(.Timeout), \(.MemorySize), \(.Architectures[0]), \(.EphemeralStorage.Size // \"None\"), \((.Layers // []) | map(.Arn) | join(\"|\")), \(.Handler)"' 2>> "$log_file")

  # Check if jq encountered an error
  if [[ $? -ne 0 ]]; then
    echo "Error processing JSON with jq in region $region" >> "$log_file"
    continue
  fi

  # Append processed data to the CSV file
  echo "$jq_output" >> "$output_file"
done

# Final message
echo "Script completed. Output saved to $output_file and logs saved to $log_file."


# Python code for converting CSV to Excel
# Python code for converting CSV to Excel
python3 - <<EOF
import pandas as pd
import warnings

# Input and output file
csv_file = "temp_lambda.csv"
excel_file = "lambda_output.xlsx"  # Ensure this has .xlsx extension

# Create Excel writer using xlsxwriter engine
writer = pd.ExcelWriter(excel_file, engine="xlsxwriter")

try:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        df = pd.read_csv(csv_file)
        if 'Trigger Information' in df.columns:
            print(f"Trigger Information column found in {csv_file}.")
        else:
            print(f"Warning: Trigger Information column NOT found in {csv_file}.")
        
        df.to_excel(writer, sheet_name="LambdaData", index=False)
except Exception as e:
    print(f"Error processing file '{csv_file}': {e}")

writer.close()
print(f"Completed: Combined CSV file saved to '{excel_file}'.")
EOF

# Clean up
rm temp_lambda.csv

echo "Task completed. Consolidated data saved to output.xlsx."


echo "Task completed. Consolidated data saved to $output_file."


#==============================================================================================================================================#


#MERGE ALL THE EXELSHEETS

python3 - <<EOF
import pandas as pd

output_file = "data-AWS-inv-output.xlsx" 

file1 = "athena_information.xlsx" 
file2 = "emr_cluster_info.xlsx" 
file3 = "amazon_glue.xlsx" 
file4= "msk_clusters.xlsx"
file5= "redshift_data.xlsx"
file6= "sagemaker_data.xlsx"

file7 = "sns_details.xlsx" 
file8 = "dms-tracker-output.xlsx" 
file9 = "kinesis_info.xlsx" 
file10= "firehose_info.xlsx"
file11= "lambda_output.xlsx"






# Load all Excel files
excel1 = pd.ExcelFile(file1)
excel2 = pd.ExcelFile(file2)
excel3 = pd.ExcelFile(file3)
excel4 = pd.ExcelFile(file4)
excel5 = pd.ExcelFile(file5)
excel6 = pd.ExcelFile(file6)

excel7 = pd.ExcelFile(file7)
excel8 = pd.ExcelFile(file8)
excel9 = pd.ExcelFile(file9)
excel10 = pd.ExcelFile(file10)
excel11= pd.ExcelFile(file11)



# Open the writer to save to the same file
with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
    # Write sheets from the first file
    
    for sheet_name in excel1.sheet_names:
        df = excel1.parse(sheet_name)
        df.to_excel(writer, sheet_name=f"Athena_{sheet_name}", index=False)
    
    # Write sheets from the second file
    for sheet_name in excel2.sheet_names:
        df = excel2.parse(sheet_name)
        df.to_excel(writer, sheet_name=f"EMR_{sheet_name}", index=False)
    
    # Write sheets from the third file
    for sheet_name in excel3.sheet_names:
        df = excel3.parse(sheet_name)
        df.to_excel(writer, sheet_name=f"Glue_{sheet_name}", index=False)
        
    for sheet_name in excel4.sheet_names:
        df = excel4.parse(sheet_name)
        df.to_excel(writer, sheet_name=f"Kafka_{sheet_name}", index=False)
   
    for sheet_name in excel5.sheet_names:
        df = excel5.parse(sheet_name)
        df.to_excel(writer, sheet_name=f"Redshift_{sheet_name}", index=False)
        
    for sheet_name in excel6.sheet_names:
        df = excel6.parse(sheet_name)
        df.to_excel(writer, sheet_name=f"Sagemaker_{sheet_name}", index=False)
        
        
        
        
        
        
    for sheet_name in excel7.sheet_names:
        df = excel7.parse(sheet_name)
        df.to_excel(writer, sheet_name=f"AWS_SNS{sheet_name}", index=False)
    
    # Write sheets from the second file
    for sheet_name in excel8.sheet_names:
        df = excel8.parse(sheet_name)
        df.to_excel(writer, sheet_name=f"AWS_DMS{sheet_name}", index=False)
    
    # Write sheets from the third file
    for sheet_name in excel9.sheet_names:
        df = excel9.parse(sheet_name)
        df.to_excel(writer, sheet_name=f"Kinesis_streams{sheet_name}", index=False)
        
    for sheet_name in excel10.sheet_names:
        df = excel10.parse(sheet_name)
        df.to_excel(writer, sheet_name=f"Kinesis_firehose{sheet_name}", index=False)
   
    for sheet_name in excel11.sheet_names:
        df = excel11.parse(sheet_name)
        df.to_excel(writer, sheet_name=f"Lambda_functions{sheet_name}", index=False)
        
   

print(f"Successfully saved combined information to {output_file}")
EOF




