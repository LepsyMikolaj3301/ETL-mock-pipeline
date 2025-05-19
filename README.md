# ETL-mock-pipeline
This project is aiming to simulate a **full end-to-end ETL pipeline** with **synthetic source data**.
## Description
As real world data is partially already processed, that is why to emulate Big Data processing purposes, data will be created on our own. This way, we can ensure the data is raw and generated with different schemas. The data will be generated in different formats. The synthetic is going to be created by generative AI and SDV models.  

The generated data will be stored internally for (optionally CRON scheduled) calls to access the data. After calling and access the data (through different mediums, such as: FTP, HTTP, maybe through email), the raw data will be stored in a HDFS file system.  

After importing data to the HDFS file system, we will conduct the MapReduce procedure for transforming, cleaning and preparing the data for ingestion into the final form - a data warehouse or data lake




## ETL
1. **Extract**  

    The extraction process involves retrieving synthetic data from the generative AI and SDV models. The different sources will involve different mediums such as FTP servers, HTTP requests and others. The generated data will be in a lot of different formats sa: XML, CSV, HTML, JSON, PNG, ...  
    The data consists of (TODO)

2. **Transform**  

    The transform process will involve cleaning, normalizing, and enriching the extracted synthetic data. This stage will involve the MapReduce methodology to transform the data for storing 

3. **Load**  

    The load process involves transferring the transformed data into the target system, such as a database (data warehouse) or a data lake. This step ensures the data is stored in a structured and accessible manner for further analysis or reporting or in a more loose fashion.

## Tech Stack
1. **ollama**, **Hugging Face**, **Python SDV** for running GenAI and SDK
2. **Hadoop** (Java?)
    - HDFS (Hadoop Distributed File System) for distributed storage.
    - MapReduce for distributed data processing. ??
    - YARN (Yet Another Resource Negotiator) for resource management.
    - Hive for querying and managing large datasets.
3. **Spark** (Python)
    - Spark Core for distributed task scheduling and execution.
    - Spark SQL for structured data processing and querying.
    - Spark Streaming for real-time data processing.
    - MLlib for machine learning and data analysis. ??
    - GraphX for graph processing and computation. ??
4. **Kafka** for distributed messaging and real-time data streaming. ??
5. **PostgreSQL** for data storing (data warehouse)  
6. Other Libraries for Python and Java (Pandas, ...)

### **FOR DEPLOYMENT**  
**Docker** and Terraform? for deploying contenerized scripts for generating data and the ETL process

## UML model
Below a proposition of the 
[UML model](https://app.diagrams.net/#G1InUlv0mn3igTeRsMwb_epqKdp3Ltcxnz#%7B%22pageId%22%3A%22QgZOktwWCn2C65YlBKYE%22%7D) of the project