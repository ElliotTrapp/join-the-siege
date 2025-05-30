# File Classifier

This is my solution to [Heron Data's join-the-siege technical challenge.](https://github.com/heron-data/join-the-siege)

## Overview

The general approach I took is based on using text embeddings to calculate cosine distance between the text parsed from pdfs, OCR, etc. and reference embeddings that contain a bunch of keywords for each document type. I took this approach because it's extremely compute efficient, realitively easy for humans to implement, maintain, and evaluate, and has performance on par with much more advanced and resource intensive approaches. I've used a similiar approach in image processing because you can do the same thing with converting a string of pixels to an embedding, calculate cosine distance, and get an estimate for how "similar" the images are. I really like this approach.

*Handling poorly named files:* The classifier now completely ignores the filename and extension and relies on the file header to check what format the file is in. I've never been a fan of relying on filenames for semantic information about a file. It violates one of the best tongue-in-cheek principles of web development: "never trust the user".

*Scaling to new industries:* I expanded the classifier to support several new built in document types including advertisements, news articles, and emails. Obviously you can never anticipate all labels your user will want so I made it really easy to add support for new documents via the new `add_file_label/` endpoint. You can even just add the simple label (ex. `transcript`) and if you provide your OpenAI API Key in the `.env` file it will send a preformatted prompt to request an embedding for your document type and add it to the configuration. None of this requires a restart or downtime for the system. You can also remove labels incase you have too many of them.

*Processing larger volumes of documents:* There is now a `classify_files/` endpoint where you can submit multiple files to be classified.

*Other improvements include:* 

- Logging
- Comments
- Type hints
- Simple CI/CD pipeline
- Basic docker support
- 


## Improvements

[] New tests
- Tests for list_file_labels, list_file_embeddings remove_file_label, add_file_label, classify_files
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

## Future Work

1. Currently there is no quality check on the automatic embedding generated from OpenAI. In my ad-hoc tests it seems to be serviceable but a future human confirmation step, perhaps using a better LLM model, and maybe providing more input in the prompt are all ways to improve the quality of the embeddings being generated.
2. I'd add a very basic web app on top of the API so that non-technical users can upload files via a browser. [streamlit.io](https://streamlit.io/) is a library I would look into using to setup a very basic, user-friendly web frontend.
3. Add support for archives like zip files and tarvballs
4. Add support for grabbing files from S3 or Google Drive