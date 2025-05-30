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

- python 3.12
- (Optional) docker, if you want to deploy with docker
- (Optional) OpenAI API key loaded with funds, if you want to automatically add new labels (by generating new embeddings)

## Setup With Docker

1. Clone the repository:

    ```shell
    git clone <repository_url>
    cd join-the-siege
    ```

2. (Optional) Setup OpenAI API key:

    ```shell
    cp env.example .env
    ```

    Update .env with your [OpenAI API key from here.](https://platform.openai.com/api-keys)

3. Build image

    ```shell
    docker build -t doc-classifier .
    ```

4. Confirm image is built

    ```shell
    docker images 
    ```

5. Bring up container

    ```shell
    docker run -d -p 5000:5000 doc-classifier
    ```

6. Ensure container is running

    ```shell
    docker ps
    ```

## Setup Without Docker

1. Clone the repository:

    ```shell
    git clone <repository_url>
    cd join-the-siege
    ```

2. (Optional) Setup OpenAI API key:

    ```shell
    cp env.example .env
    ```

    Update .env with your [OpenAI API key from here.](https://platform.openai.com/api-keys)

3. Install dependencies:

    ```shell
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

4. Run the Flask app:

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

### Listing Labels

```shell
    curl -X GET http://localhost:5000/list_file_labels
```

### Listing Labels with Embeddings

```shell
    curl -X GET http://localhost:5000/list_file_embeddings
```

### Adding a New Label and Embedding

```shell
curl -X POST http://localhost:5000/add_file_label \
  -H "Content-Type: application/json" \
  -d '{"label": "transcript", "embedding": "grade school class semester quarter"}'
```

### Adding a New Label Without Explicit Embedding (Requires OpenAPI Key + Funds)

```shell
    curl -X POST http://localhost:5000/add_file_label \
    -H "Content-Type: application/json" \
    -d '{"label": "invoice"}'
```

### Removing a Label and Embedding

```shell
    curl -X POST http://localhost:5000/remove_file_label \
    -H "Content-Type: application/json" \
    -d '{"label": "invoice"}'
```

## Running Tests

```shell
    pytest
```
