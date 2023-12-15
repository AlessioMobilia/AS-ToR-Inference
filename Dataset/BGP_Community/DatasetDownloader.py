import pybgpstream
import re
import json
import datetime
import argparse

def downloader(start_date, duration, files):

    # Start of UNIX time
    base = int(datetime.datetime.strptime(start_date, '%m/%d/%Y').strftime('%s'))
    # Create a BGPStream instance with record type "ribs"
    stream = pybgpstream.BGPStream(
        collectors=["route-views2","rrc00","route-views.sg", "route-views.eqix"],
        record_type="ribs",
        filter="community *:*"
    )
    stream.add_interval_filter(base, base + int(duration))
    print(base)




    #------------------
    '''
    FORMAT
    (ASN,[community regex pattern,...], position, relationship, [community regex pattern to exclude]),

    if all the community regex pattern are found the relation is added
    but if all the comunity regex pattern to exclud are found the reletion is not added
    position can be 1 or -1. 1 if it is relative to the next AS in the list, -1 if it is relative to te previous element
    relation can be -1, 0, 1 or 2:

    AS|<customer-as>|-1
    AS|<peer-as>|0
    AS|<sibling-as>|1
    AS|<provider-as>|2

    '''
    #load json from file
    print(f"Start Date: {start_date}")
    print(f"Duration: {duration} minutes")

    BGPFilter = []  # Initialize an empty list to store all JSON data

    for file_path in files:
        try:
            with open(file_path, 'r') as file:
                json_data = json.load(file)
                # Append the JSON data to the list
                BGPFilter.extend(json_data)
                print(f"Processing file: {file_path}")
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            return
        except json.JSONDecodeError:
            print(f"Error decoding JSON in file: {file_path}")
            return

    #--------------

    unique_lines_set = set()
    line_number = 0
    output_file = "dataset.txt"

    print("Starting download...")

    with open(output_file, "w") as f:
        # Iterate through BGP records and elements
        for elem in stream:
            line_number += 1
            
            if (':' not in  elem.fields['prefix']): #check if it is an IPv4 path
                as_path_with_duplicate =elem.fields['as-path'].split()

                # Using a loop to remove consecutive duplicate occurrences in as_path
                # AS can prepend multiple times the same asn to make a path longer
                as_path = [as_path_with_duplicate[0]] 
                for i in range(1, len(as_path_with_duplicate)):
                    if as_path_with_duplicate[i] != as_path_with_duplicate[i - 1]:
                        as_path.append(as_path_with_duplicate[i])

                # Check if the route has any BGP community attribute
                if "communities" in elem.fields:
                    for filter in BGPFilter:
                        if str(filter[0]) in as_path:
                            

                            #check for pattern to exclude line
                            match=True
                            check=False
                            for bad_pattern in filter[4]:  
                                check = True
                                m=False
                                for com in elem.fields['communities']:
                                    m = re.match(bad_pattern, com) or m
                                    if(m):
                                        break
                                match = match and m
                            if(match and check):
                                break #exit if all bad pattern are found
                            
                            #check for pattern
                            match=True
                            for pattern in filter[1]:  
                                m=False
                                for com in elem.fields['communities']:
                                    m = re.match(pattern, com) or m
                                    if(m):
                                        break
                                match = match and m
                                if(not match):
                                    break
                            if(match):
                                #find the as target
                                as_target =''
                                for i in range(1, len(as_path)):
                                    if (as_path[i] == str(filter[0])):
                                        if(filter[2]==-1 and i>0):
                                            as_target = as_path[i - 1]
                                        elif(filter[2]==1 and i<len(as_path)-1):
                                            as_target = as_path[i + 1]
                                        else:   
                                            break

                                if(as_target ==''):
                                    break
                                if(filter[3]==2):
                                    line = f"{as_target}|{filter[0]}|-1"
                                else:
                                    line = f"{filter[0]}|{as_target}|{filter[3]}"
                                if line not in unique_lines_set:
                                    #print relationship
                                    f.write(line+'\n')
                                    unique_lines_set.add(line)
                                    if(filter[3]==0):
                                        unique_lines_set.add(f"{as_target}|{filter[0]}|0")
                                    f.flush()

            if line_number % 100000000 == 0:
                print(f"Paths checked: {line_number}")

    print(f"Output saved to {output_file}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download BGP path from a start date for a duration and generate relation from pattern in json file')
    parser.add_argument('-s', '--start',
                        help='The start date in MM/DD/YYYY',
                        required=True)
    parser.add_argument('-d', '--duration',
                        help='Duration in minutes',
                        required=True)
    parser.add_argument('-f', '--files',
                        help='pattern file/files',
                        nargs='+',
                        required=True)
    args = parser.parse_args()
    downloader(args.start, args.duration, args.files)
