# AS-ToR-Inference
This repository presents the outcomes of various inference algorithms: ASRank, TopoScope, and ProbLink.
The results for each algorithm are organized into separate folders.

## Folder Structure
```
.
├── Data
│   ├── 20230701.as-org2info.jsonl
│   ├── 20230701.as-org2info.txt
│   ├── asrel.txt
│   ├── peeringdb_2_dump_2023_01_01.json
│   ├── rib.txt
│   └── sanitized_rib.txt
│
└── Results
    ├── asrank_result.txt
    ├── asrel.txt
    ├── asrel_toposcope.txt
    └── problink_result.txt

```
Each folder corresponds to a day of routing tables. 
he "Data" folder contains input files such as rib.txt and sanitized_rib.txt. 
The "Results" folder includes the output files from the inference algorithms. 
Unfortunately, the input ribs are not uploaded due to their size.

## Data Format
The data results follow this format:
```
<provider-as>|<customer-as>|-1
<peer-as>|<peer-as>|0
<sibling-as>|<sibling-as>|1

```
## Usage
  - 'DataUpload.py': Allows you to upload the data to a Neo4J database.
  - 'GraphDraw': Contains Python scripts for visualizing and comparing inference results of ASN.
  - 'run.sh': A bash script designed to run the algorithm that produced the results in the repo. It should be placed in the folder containing all necessary files and separate folders for TopoScope and ProbLink.


## Related Repositories

- [ProbLink](https://github.com/AlessioMobilia/ProbLink)
- [TopoScope](https://github.com/AlessioMobilia/TopoScope)

Feel free to explore each algorithm's folder and use the provided scripts for further analysis and visualization.
If you have any questions or feedback, please don't hesitate to reach out.

# Dataset

There are two main datasets. You can find the dump of the neo4j db in the dataset folder. It contains all inference results and all the datasets.

## Hurricane

This dataset is generated by crawling the hurricane looking glass on 25 Nov 2023.
The dataset may not be 100% accurate.
Inside the folder, you can find the spider code. If you want to use it, place it in a scrapy project, paying attention to adding delays to the requests.

## BGP_Community

This dataset is created by inspecting the BGP communities. You can find the code to generate the dataset.
The Python code is extensible using JSON files.
BGP communities are codes used by ASes to filter paths. I use these codes to identify relationships between ASes.

### Usage
You can call the script by passing the starting date, duration (86400 is a full day), and the JSON file/files with the pattern to match.

```bash
python3 DatasetDownloader.py -s 08/01/2023 -d 86400 -f pattern.json &> out.txt &

```

### Files Json

The files JSON contain an array of arrays with this structure:

```json
 [1273, ["1273:1\\d{4}"], 1, -1, []],
```

- The first element is the AS number.
- The second element is an array of regex patterns to be matched.
- The third element represents the relative position in the AS_path of the AS with which it has a relationship (-1 is left, 1 is right).
- The fourth element represents the relationship to assign when the pattern matches following this:
  ```
    AS|<customer-as>|-1
    AS|<peer-as>|0
    AS|<sibling-as>|1
    AS|<provider-as>|2
  ```
- The fifth element is an array of regex patterns to exclude. If all patterns match, the relationship is ignored.

