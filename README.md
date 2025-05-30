# File Classifier

This is my solution to [Heron Data's join-the-siege technical challenge.](https://github.com/heron-data/join-the-siege)

## Overview

## Improvements

- Logging
- Comments
- Type hints
[] Setup CI/CD pipeline for automatic testing and deployment
[] Add docker
- Tests for list_file_labels, list_file_embeddings remove_file_label, add_file_label, classify_files
- Overhaul README with examples, explanations, add possible future improvements like GUI, other ways to upload
[] Exception handling, include note about getting embedding from OpenAI could be problem
[x] Support many more file formats (pdf, docx, etc.) and file types (invoice, taxes, iteneratory, etc.)
[x] Refactor to make more maintainable and scalable
[x] Better validation with guard statements
[x] Adding an endpoint to define new data/train
[x] No downtime on app for adding or removing industries
[x] Users can generate new embeddings by asking an LLM

## Supported File Formats

There are several supported file formats. Neither file name nor extension is required to be anything specific.

- pdf
- jpg
- png
- tiff
- txt
- docx
- rtf

## Built-in Document Types

There are several document types built-in but more can be added at anytime via the `/add_file_label` endpoint.

- advertisement
- bank statement
- drivers license
- email
- invoice
- news article
- presentation
- resume

## Prerequisites

## Setup With Docker

1. Clone the repository:

    ```shell
    git clone <repository_url>
    cd join-the-siege
    ```

2. Build image

    ```shell
    docker build -t doc-classifier .
    ```

3. Confirm image is built

    ```shell
    docker images 
    ```

4. Bring up container

    ```shell
    docker run -d -p 5000:5000 doc-classifier
    ```

5. Ensure container is running

    ```shell
    docker ps
    ```

## Setup Without Docker

1. Clone the repository:

    ```shell
    git clone <repository_url>
    cd join-the-siege
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

## Usage

### Classify Single File

```shell
    curl -X POST -F 'file=@path_to_pdf.pdf' http://localhost:5000/classify_file
```

### Classify Multiple Files

```shell
    curl -X POST -F 'files[]=@drivers_licence_2.jpg' -F 'files[]=@invoice_1.pdf' http://localhost:5000/classify_files
```

### Adding a New Label Only

```shell
    curl -X POST http://localhost:5000/add_file_label \
    -H "Content-Type: application/json" \
    -d '{"label": "invoice"}'
```

### Adding a New Label and Embedding

```shell
curl -X POST http://localhost:5000/add_file_label \
  -H "Content-Type: application/json" \
  -d '{"label": "transcript", "embedding": "grade school class semester quarter"}'
```

### Removing a Label and Embedding

### Listing Labels

### Listing Labels with Embeddings

## Running Tests

```shell
    pytest
```