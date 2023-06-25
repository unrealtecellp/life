# LiFE
## Linguistic Field Data Management and Analysis System

This repository hosts the code and installation instructions for the LiFE, developed by the M.Sc. Computational Linguistics and M.Phil Linguistics students of Dr. Bhimrao Ambedkar Univesity, Agra - Siddharth Singh, Shyam Ratan and Sonal Sinha - under the supervision of Dr. Ritesh Kumar.


## Running the Demo Version (Alpha Test Version)

In order to run a Demo Version of the app (currently its an Alpha Test Version), use the following link -

```
http://life.unreal-tece.co.in/
```

## Installation on Local System

If you would like to set up the app on your own server / system for testing and use, follow the following instructions - these are tested to work on Ubuntu >= 18.04 but is expected to work on other Linux-based systems as well as other Operating Systems (with equivalent commands / methods of installation of required packages).

### <font color="red"> Remember that the app is still in Alpha testing phase and is made available for feature request and feedback. Do NOT use it for production purposes. </font>

### The Easy Way (for Linux-based Systems)

1. Clone the app GitHub repository
    ```
    https://github.com/unrealtecellp/life.git
    ```
2.  Change directory to the app root directory(repo name)
    ```
    cd life
    ```
3. Run the installation script
    ```
    ./install.sh
    ```
4. Run the application
    ```
    flask run -h 0.0.0.0
    ```
5. In browser address bar, type the following location
    ```
    http://localhost:5000


### The slightly involved way (if the easy way didn't work or you are not on Linux)

1. Clone the app GitHub repository
    ```
    https://github.com/unrealtecellp/life.git
    ```
2.  Change directory to the app root directory(repo name)
    ```
    cd life
    ```
3. Create a python virtual environment(venv) 
    ```
    python3 -m venv venv
    ```  
4. Activate python virtual environment(venv) 
    ```
    source venv/bin/activate
    ```
5. Install all dependencies from requirements.txt
    ```
    pip3 install -r requirements.txt
    ```
6. Setup mongodb
    ```
    sudo apt-get install mongodb
    ```
    Check the MongoDB Version and its status -
    ```
    mongod --version

    sudo systemctl status mongodb
    ```
7. Run the application
    ```
    flask run -h 0.0.0.0
    ```
8. In browser address bar, type the following location
    ```
    http://localhost:5000
    ```

    In order to access it from within the same network or make it available publicly, one could login using the system's IP address.

9. View mongodb in GUI: install mongodb compass
    - https://www.digitalocean.com/community/tutorials/how-to-use-mongodb-compass
    - mongodb from terminal
    https://docs.mongodb.com/manual/tutorial/getting-started/       

## Video Demo
A Short Video Demo for using the app is available at the following link -

<b><a href="https://youtu.be/HJWCjeiv3mU">LiFE Demo</a></b>


## Contact

For all queries / suggestions / feedback as well as updates related to the app, please join our Google Group -

<b><a href=https://groups.google.com/g/lifeapp>LiFE Web App Google Group</a></b>

## Citation

We do not have a publication yet. However you may cite our demo at ICON-2021 (the paper is at ArXiV but will be soon published in the ICON-2021 Proceedings). You may also directly cite this repository.

    @misc{https://doi.org/10.48550/arxiv.2203.11443,
       doi = {10.48550/ARXIV.2203.11443},
       url = {https://arxiv.org/abs/2203.11443},
       author = {Singh, Siddharth and Kumar, Ritesh and Ratan, Shyam and Sinha, Sonal},
       keywords = {Computation and Language (cs.CL), FOS: Computer and information sciences, FOS: Computer and information sciences},
       title = {Demo of the Linguistic Field Data Management and Analysis System -- LiFE},
       publisher = {arXiv},
       year = {2022},
       copyright = {arXiv.org perpetual, non-exclusive license}
     }
    
    @inproceedings{singh-etal-2022-towards,
        title = "Towards a Unified Tool for the Management of Data and Technologies in Field Linguistics and Computational Linguistics - {L}i{FE}",
        author = "Singh, Siddharth  and
          Kumar, Ritesh  and
          Ratan, Shyam  and
          Sinha, Sonal",
        booktitle = "Proceedings of the Workshop on Resources and Technologies for Indigenous, Endangered and Lesser-resourced Languages in Eurasia within the 13th Language Resources and Evaluation Conference",
        month = jun,
        year = "2022",
        address = "Marseille, France",
        publisher = "European Language Resources Association",
        url = "https://aclanthology.org/2022.eurali-1.16",
        pages = "90--94",
        abstract = "",
    }


    @inproceedings{singh-etal-2021-demo,
        title = "Demo of the Linguistic Field Data Management and Analysis System - {L}i{FE}",
        author = "Singh, Siddharth  and
          Kumar, Ritesh  and
          Ratan, Shyam  and
          Sinha, Sonal",
        booktitle = "Proceedings of the 18th International Conference on Natural Language Processing (ICON)",
        month = dec,
        year = "2021",
        address = "National Institute of Technology Silchar, Silchar, India",
        publisher = "NLP Association of India (NLPAI)",
        url = "https://aclanthology.org/2021.icon-main.82",
        pages = "660--662",
        abstract = "",
    }