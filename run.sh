#!/bin/bash

# IFTTT Webhooks URL
IFTTT_WEBHOOKS_URL="https://maker.ifttt.com/trigger/<ifttt-server>/json/with/key/<ifttt-key>" #modify according to your needs (not mandatory)

# Function to execute a command and check its exit status
execute_command() {
    local cmd="$1"
    echo "Starting: '$cmd' ." >> run.log
    notify_ifttt "Starting: '$cmd' ."
    $cmd
    if [ $? -eq 0 ]; then
        echo "Command '$cmd' executed successfully." >> run.log
        notify_ifttt "Command '$cmd' executed successfully."
    else
        echo "Command '$cmd' failed." >> run.log
        notify_ifttt "Command '$cmd' failed."
        exit 1
    fi
}


# Function to send a notification to IFTTT
notify_ifttt() {
    sanitized_string=$(echo "$1" | sed -e 's/[^a-zA-Z0-9_:]/_/g' -e "s/['\"]//g") 
    local message="{\"message\":\"$sanitized_string\"}"
    
curl --silent -o /dev/null -X POST -H "Content-Type: application/json" -d $message $IFTTT_WEBHOOKS_URL
}


#move problink file outside folder
if [ ! -s file_list_problink.txt ]; then
    ls ProbLink/ > file_list_problink.txt
    execute_command "mv ProbLink/* ./"
fi

#Change the data and the name files

#ASRANK

# execute ASRANK
execute_command "perl asrank.pl rib.txt " > asrank_result_native.txt

#execute Upload asrank
execute_command "python3 DataUpload.py -f asrank_result_native.txt -a asrank -d 2023-10-01 " &> upload_asrank.log



# PROBLINK

# parser for problink
execute_command "python3 bgp_path_parser.py peeringdb_2_dump_2023_10_01.json"  &> parser_problink.log

# execute ASRANK for problink
execute_command "perl asrank.pl sanitized_rib.txt " > asrank_result.txt

# execute PROBLINK
execute_command "python3 problink.py -p peeringdb_2_dump_2023_10_01.json -a 20231001.as-org2info.txt " &> problink.log

#execute Upload problink
execute_command "python3 DataUpload.py -f problink_result.txt -a problink -d 2023-10-01 " &> upload_problink.log


#move problink file inside folder
while IFS= read -r file; do mv "./$file" ProbLink/; done < file_list_problink.txt
rm file_list_problink.txt

#move TopoScope file outside folder
#move problink file outside folder
if [ ! -s file_list_toposcope.txt ]; then
    ls TopoScope/ > file_list_toposcope.txt
    execute_command "mv TopoScope/* ./"
fi



# TOPOSCOPE

#execute parser for toposcope
execute_command "python uniquePath.py -i rib.txt -p peeringdb_2_dump_2023_10_01.json "  &> parser_toposcope.log

#execute ASRANK for toposcope
execute_command "perl asrank.pl aspaths.txt " > asrel.txt

#execute TOPOSCOPE
execute_command "python toposcope.py -o 20231001.as-org2info.txt -p peeringdb_2_dump_2023_10_01.json -d tmp/"

#move TopoScope file inside folder
while IFS= read -r file; do mv "./$file" TopoScope/; done < file_list_toposcope.txt
rm file_list_toposcope.txt

#execute Upload toposcope
execute_command "python3 DataUpload.py -f asrel_toposcope.txt -a toposcope -d 2023-10-01 " &> upload_toposcope.log

# All commands have executed successfully
echo "All commands have completed successfully."

# Exit the script with a success status
exit 0
