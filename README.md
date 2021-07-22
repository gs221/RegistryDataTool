# Registry Data Tool

## Description
Tool created for Academic Registry to aid in the management of their data. 

The tool includes the following options: 

- Detect duplicates across two delimited files. 
- Detect duplicate across a single delimited file. 
- Automatically test links in a file. 
- Detect differences across two delimited files.

## Documentation

Documentation for the data tool can be found here:
- [Source 1 - OneDrive](https://universityofstandrews907-my.sharepoint.com/:w:/g/personal/gs221_st-andrews_ac_uk/EYQC-RKj859Ao_rQ0yDG_okB5LFdglXZnp4erHbyUucanw?e=DbG8CD)
- [Source 2 - Personal Server](https://os5.mycloud.com/action/share/ff5c3679-3366-4964-83e2-eff3dec61974)

## Prerequisites and Installation
Clone repository:
```
git clone https://github.com/gs221/RegistryDataTool.git
```
If using windows you must install the following build tools:
- MSVC v142 -VS 2019 C++ x64/x86 build tools (Latest)
- Windows 10 SDK (10.0.19041.0)

Navigate to the `RegistryDataTool` folder and install required packages: 
```
pip install -r program_files/requirements.txt
```

## Licensing 
[Csvdedupe](https://github.com/dedupeio/csvdedupe#copyright-and-attribution) - Copyright © 2016 DataMade. Released under MIT License.
