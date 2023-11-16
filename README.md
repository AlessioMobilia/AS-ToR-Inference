# AS-ToR-Inference
This repository showcases the results of different inference algorithms: ASRank, TopoScope, and ProbLink. Each algorithm's results are organized into separate folders.

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
The "Data" folder contains input files such as rib.txt and sanitized_rib.txt.
The "Results" folder includes the output files from the inference algorithms.

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

Feel free to explore each algorithm's folder and use the provided scripts for further analysis and visualization. If you have any questions or feedback, please don't hesitate to reach out.

