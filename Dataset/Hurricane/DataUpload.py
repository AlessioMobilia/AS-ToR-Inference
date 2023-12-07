from email.policy import strict
import re
from datetime import datetime
import requests
from urllib.request import Request, urlopen
import json
import argparse
from tqdm import tqdm
import mmap
import os
from time import sleep
from neo4j import GraphDatabase

# Define your Neo4j database credentials and connection URL
uri = "neo4j:// 192.168.10.4"  # Replace with your database URL
username = "neo4j"  # Replace with your Aura database username
password = "FrafJWurDR9gX@"  # Replace with your Aura database password

# Define a function to perform some operation within a transaction
def create_dataset_node(tx, date, name):
    id = dataset_check(tx, name, date)
    if( id == -1):
        query = "CREATE (t:Dataset {inference_date: $date, name:$name}) RETURN t"
        result = tx.run(query, date=date, name=name)
        record = result.single(strict=True)
        id = record[0].id
        return id
    return id


#create the node as and connect it to the Dataset node
def create_as(tx, asn, datasetid):
    if(node_check(tx, asn, datasetid)<1):
        name = get_as_name(asn)
        query = "CREATE (p:AutonomousSystem {name: $name, asn: $asn}) RETURN p"
        result = tx.run(query, name=name, asn=asn)
        record = result.single(strict=True)
        asid = record[0].id

        #create relationship with Dataset node
        query = "MATCH (t:Dataset) WHERE ID(t)= $datasetid MATCH (p:AutonomousSystem) WHERE ID(p)= $asid CREATE (p)-[r:INFERRED_ON]->(t)"
        tx.run(query, datasetid=datasetid, asn=asn, asid=asid)
        


def create_peer_relationship(tx, asn1, asn2, datasetid):
    if(relationship_check(tx,asn1,asn2,datasetid)<1):
        query = "MATCH (aa:AutonomousSystem {asn:$asn1})-[]-(t:Dataset) WHERE ID(t)=$datasetid MATCH (ab:AutonomousSystem {asn:$asn2})-[]-(t:Dataset) WHERE ID(t)=$datasetid CREATE (aa)-[r:PEER_OF]->(ab)"
        tx.run(query, asn1=asn1, asn2=asn2,datasetid=datasetid)

def create_transit_relationship(tx, asn1, asn2, datasetid):
    if(relationship_check(tx,asn1,asn2,datasetid)<1):
        query = "MATCH (a1:AutonomousSystem {asn:$asn1})-[]-(t:Dataset) WHERE ID(t)=$datasetid MATCH (a2:AutonomousSystem {asn:$asn2})-[]-(t:Dataset) WHERE ID(t)=$datasetid CREATE (a1)-[r:GIVE_TRANSIT_TO]->(a2)"
        tx.run(query, asn1=asn1, asn2=asn2, datasetid=datasetid)

def create_sibling_relationship(tx, asn1, asn2, datasetid):
    if(relationship_check(tx,asn1,asn2,datasetid)<1):
        query = "MATCH (a1:AutonomousSystem {asn:$asn1})-[]-(t:Dataset) WHERE ID(t)=$datasetid MATCH (a2:AutonomousSystem {asn:$asn2})-[]-(t:Dataset) WHERE ID(t)=$datasetid CREATE (a1)-[r:SIBLING_OF]->(a2)"
        tx.run(query, asn1=asn1, asn2=asn2, datasetid=datasetid)


# return the count of a relationship with the same algo
def relationship_check(tx, asn1, asn2, datasetid):
    query = ("""
        MATCH (t:Dataset)-[]-(n:AutonomousSystem {asn: $asn1})-[r]-(a:AutonomousSystem {asn: $asn2})-[]-(t:datasetid) WHERE ID(t)=$datasetid
        RETURN COUNT(n) as count
    """)
    result = tx.run(query, asn1=asn1, asn2=asn2, datasetid=datasetid)
    record = result.single(strict=True)
    return record['count']


# return the count of as with a defined asn
def node_check(tx, asn, datasetid):
    query = ("""
        MATCH (n:AutonomousSystem {asn: $asn})-[]-(t:Dataset) WHERE ID(t)=$datasetid
        RETURN COUNT(n) as count
    """)
    result = tx.run(query, asn=asn, datasetid=datasetid)
    record = result.single(strict=True)
    return record['count']

def dataset_check(tx, name, date):
    query = ("""
        MATCH (t:Dataset {inference_date: $date,name:$name})
        RETURN count(t) as count
    """)
    result = tx.run(query, date=date,name=name)
    record = result.single(strict=True)
    if(record['count']>0):
        query = ("""
            MATCH (t:Dataset {inference_date: $date,name:$name})
            RETURN t
        """)
        result = tx.run(query, date=date,name=name)
        record = result.single(strict=True)
        return record[0].id
    return -1


# Main function to connect to the database and call multiple functions in a transaction
def main(filepath,datasetname,time):
    try:
        driver = GraphDatabase.driver(uri, auth=(username, password), max_connection_lifetime=200)
        driver.verify_connectivity()

        with driver.session() as session:
            # Start a transaction
            with session.begin_transaction() as tx:

                datasetid = create_dataset_node(tx, time, datasetname)
            
            gen_graph(filepath,session,datasetid)
                
            print("Transaction completed successfully.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

    finally:
        driver.close()

#return num of lines of a file
def get_num_lines(file_path):
    fp = open(file_path, "r+")
    buf = mmap.mmap(fp.fileno(), 0)
    lines = 0
    while buf.readline():
        lines += 1
    return lines



#read the file and generate the graph
def gen_graph(filepath, session,datasetid):
    
        #analyze lines
        with open(filepath,'r') as f:
            for line in tqdm(f, total=get_num_lines(filepath)):
                with session.begin_transaction() as tx:
                    line.strip()
                    if not line:
                        break
                    elif '#' in line:
                        continue
                    else:
                        ases = line.split("|")
                        create_as(tx,ases[0],datasetid)
                        create_as(tx,ases[1],datasetid)
                        if '-1' in ases[2]:
                            create_transit_relationship(tx,ases[0],ases[1],datasetid)
                        elif '0' in ases[2]:
                            create_peer_relationship(tx,ases[0],ases[1],datasetid)
                        elif '1' in ases[2]:
                            create_sibling_relationship(tx,ases[0],ases[1],datasetid)
                        ases={}

            f.close()


#retrive the name od the as by the asn
def get_as_name(asnumber, retry=0):
    sleep(1)
    try:
        response = requests.get('https://api.bgpview.io/asn/'+asnumber, headers={'User-agent': 'Mozilla/5.0', 'Accept': 'application/json'})
        response.raise_for_status()  # Raise an exception for HTTP errors (e.g., 404 Not Found)
        data = response.json()  # Try to parse the response as JSON

        # Check if the response contains valid data
        if 'data' in data and 'name' in data['data']:
            return data['data']['name']
        else:
            # Handle the case where the response doesn't contain the expected data
            return "Unknown"  # or any other default value you prefer

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while making the HTTP request: {str(e)}")
        # Handle the error by retry the request max 3 times
        retry=retry+1
        if(retry<3):
            sleep(3)
            return get_as_name(asnumber, retry)
        else:
            return "Unknown"  

    except json.JSONDecodeError as e:
        print(f"An error occurred while parsing JSON data: {str(e)}")
        return "Unknown"  # Handle the error by returning a default value


def valid_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        msg = "not a valid date: {0!r}".format(s)
        raise argparse.ArgumentTypeError(msg)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Upload the data inferred to neo4j graph db')
    parser.add_argument('-n', '--name',
                        help='The dataset name',
                        required=True)
    parser.add_argument('-f', '--file',
                        help='file path of the infered results',
                        required=True)
    parser.add_argument('-d', '--date',
                        type=valid_date,
                        help='date of the input data for the inference algo',
                        required=True)
    args = parser.parse_args()

    main(args.file,args.name,args.date)
