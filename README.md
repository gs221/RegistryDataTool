# Registry Data Tool

## Description
Tool created for the University of St Andrews Academic Registry to aid in the importation of external ucas data into internal school table. The tool includes the following options: 

- Detect duplicates across two delimited files. 
- Detect duplicate across a single delimited file. 
- Automatically test links in a file. 
- Detect differences across two delimited files.

## Prerequisites and Installation
Clone repository:
```
git clone https://github.com/gs221/RegistryDataTool.git
```
If using windows you must install the following build tools:
- MSVC v142 -VS 2019 C++ x64/x86 build tools (Latest)
- Windows 10 SDK (10.0.19041.0)

Navigate to the SCL-Tool folder and install required packages: 
```
pip install -r program_files/requirements.txt
```

## Licensing 
[Csvdedupe](https://github.com/dedupeio/csvdedupe#copyright-and-attribution) - Copyright © 2016 DataMade. Released under MIT License.

## Contact 
- Gregor: gregor@gscs.uk
