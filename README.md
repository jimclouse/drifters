Drifter Processing and Analysis
===============================

Intent
------
This repo is specifically for storing code used in my Master's thesis, titled: Identification and retrieval of derelict fishing gear in the North Atlantic Ocean.

Overview
--------
For my Master's thesis, I needed to obtain coordinate data for drifters (satellite tracked buoys), pull them into a database, and then extract sets of them for various experiments. 
This code does all of the loading, processing, and much of the analysis of these drifters.

Raw drifter data was obtained from Fisheries and Ocean's Canada website (http://www.meds-sdmm.dfo-mpo.gc.ca/isdm-gdsi/drib-bder/svp-vcs/index-eng.asp)

Installation
------------
After cloning the project, run sudo Make to install the required software.

There are various make targets that run different parts of the analysis.

The project includes a Vagrant file, which can be used to spin up a new VM.