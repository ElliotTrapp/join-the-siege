# File Classifier

This is my solution to [Heron Data's join-the-siege technical challenge.](https://github.com/heron-data/join-the-siege)

## Overview

## Improvements

[] Logging
[] Exception handling 
[] Add logic for processing empty files, empty files with no extension, empty files with no name
[] Add support for new industries
[] Classify other things about the file, industry, users, suggestions, etc.
[] Allow different upload strategies, single file, zipped file, S3 path, Google Drive, etc.
[] Comments/docstrings
[] Actual documentation
[] Host documentation somewhere
[] Better use of standard library
[] Type hints
[] More endpoints
[] Deploying to cloud
[] Training a classifier, include content of file
[] Support many more file formats (pdf, docx, etc.) and file types (invoice, taxes, iteneratory, etc.)
[] Setup CI/CD pipeline for automatic testing and deployment
[] Refactor to make more maintainable and scalable
[] Generating synthetic data
[] Learn through data ingestion
[] ElasticSearch?
[] Adding a database
[] Better validation, guard statements
[] More tests
[] Adding a GUI
[] Adding an endpoint to define new data/train
[] No downtime on app for new training
[] Add docker
[] Users can generate new embeddings by asking an LLM

## Supported File Formats

- pdf
- jpg
- png
- tiff
- txt
- docx
- xlsx
- rtf

## Support Document Types

## Setup

1. Clone the repository:

    ```shell
    git clone <repository_url>
    cd heron_classifier
    ```

2. Install dependencies:

    ```shell
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

3. Run the Flask app:

    ```shell
    python -m src.app
    ```

4. Test the classifier using a tool like curl:

    ```shell
    curl -X POST -F 'file=@path_to_pdf.pdf' http://localhost:5000/classify_file
    ```

# More than one

    ```shell
    curl -X POST -F 'files[]=@drivers_licence_2.jpg' -F 'files[]=@invoice_1.pdf' http://localhost:5000/classify_files
    ```

5. Run tests:

   ```shell
    pytest
    ```

## Usage

### With Docker

docker build -t doc-classifier . # builds image
docker images # check if image is there
docker run -d -p 5000:5000 doc-classifier # spins up container from image
docker ps # ensure the container is running

### Without Docker


### Adding a new label without embedding

```shell
curl -X POST http://localhost:5000/add_file_label \
  -H "Content-Type: application/json" \
  -d '{"label": "invoice"}'
```

### Adding a new label with embedding

```shell
curl -X POST http://localhost:5000/add_file_label \
  -H "Content-Type: application/json" \
  -d '{"label": "transcript", "embedding": "grade school class semester quarter"}'
```


## Architecture
