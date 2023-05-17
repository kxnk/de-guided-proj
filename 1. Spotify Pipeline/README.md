## Project Objective
Develop an ETL pipeline using Python and AWS services to obtain the artist, album, and song information from the "Discover Weekly" playlist on Spotify. This playlist is updated every Monday and consists of 30 personalized songs tailored for each user. The pipeline involves extracting data from the Spotify API, transforming the data to prepare it for analysis, loading the transformed data into Amazon S3, and querying the transformed data using Amazon Athena, utilizing AWS Glue for cataloging and metadata management.

Tools used: Python, AWS services (CloudWatch, Lambda, S3, Glue and Athena)

## Files

* Spotify Data Pipeline Project-My Version.ipynb: Jupyter notebook to develop the initial Python code for data extraction and transformation
* extract_data.py: This code will be used in the Lambda function to extract data from the Spotipy API
* transform_spotipy_data.py: This code will be used in the Lambda function to perform data transformation and prepare 3 files for the album, artist, and songs. The data will be stored in the respective subfolders in transformed_data. Files in the to_process folder will be copied to the processed folder and files in to_process will be deleted.
* spotipy_layer.zip: Upload this zip file in a layer in Lambda
* Architecture Diagram.jpg: Diagram provided in the course

* References: 
  * [Darshil Parmar's Python for Data Engineering course](https://learn.datawithdarshil.com/courses/Python-for-Data-Engineering-63dbd4e2e4b04e40a25e4445)
  * [Main Repository](https://github.com/darshilparmar/python-for-data-engineering/tree/main/6.%20End-To-End%20Data%20Pipeline%20Project)
