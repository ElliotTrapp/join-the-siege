import copy
from io import BytesIO

import pytest
from src.app import app

default_labels = {
    "labels": [
        "advertisement",
        "bank_statement",
        "drivers_license",
        "email",
        "invoice",
        "news_article",
        "presentation",
        "resume",
    ]
}

default_embeddings = {
    "embeddings": {
        "advertisement": "advertisement campaign brand product service "
        "price discount offer promotion\n"
        "call action target audience slogan tagline "
        "logo image video medium platform reach\n"
        "impression click conversion sale budget "
        "duration placement keywords demographic\n"
        "psychographics market research competitor "
        "analysis creative brief headline "
        "subheadline\n"
        "body copy testimonial endorsement social "
        "medium influencer banner popup flyer "
        "brochure\n"
        "jingle radio print digital outdoor "
        "sponsorship event marketing\n",
        "bank_statement": "account number statement date beginning "
        "balance ending balance transaction\n"
        "deposit withdrawal interest fee ach check "
        "balance available fund overdraft bank\n"
        "name account holder debit credit transfer "
        "description direct deposit atm withdrawal\n"
        "online banking date transaction reference "
        "number merchant name transaction type\n"
        "currency exchange rate fee charge statement "
        "period statement cycle statement summary\n"
        "minimum payment due payment due date late "
        "fee interest rate statement balance "
        "available\n"
        "credit credit limit payment received "
        "payment posted pending transaction "
        "electronic\n"
        "fund transfer wire transfer statement "
        "message alert notification\n",
        "drivers_license": "driver driving license number name address "
        "date birth issue expiration state\n"
        "class endorsement restriction signature "
        "organ donor barcode photo gender height\n"
        "weight eye color hair color seal license "
        "type unique identifier issuing authority\n"
        "country residence expiration renewal "
        "suspension revocation restriction "
        "condition\n"
        "veteran status veteran indicator veteran "
        "designation veteran code wheel \n",
        "email": "email sender recipient subject date time bcc body "
        "attachment reply forward\n"
        "signature header footer message content type "
        "priority read status folder label thread\n"
        "conversation inbox outbox spam junk draft archive "
        "unsubscribe autoreply encryption\n"
        "phishing virus filter delivery receipt read receipt "
        "importance confidentiality disclaimer\n"
        "formatting hyperlink inline image embedded video "
        "contact list distribution list\n"
        "reply forward chain message size server smtp imap "
        "pop\n",
        "invoice": "invoice number invoice invoice date due date "
        "reference number seller name\n"
        "seller address seller contact vendor supplier "
        "buyer name buyer address customer\n"
        "client recipient item description product name sku "
        "quantity unit price rate item\n"
        "code description subtotal total tax tax rate vat "
        "gst discount shipping handling\n"
        "fee grand total amount due balance due payment "
        "term payment method payment instruction\n"
        "bank detail account number term condition note "
        "comment purchase order number number\n"
        "delivery date salesperson currency tax tax number "
        "invoice status\n",
        "news_article": "headline byline date author location source "
        "content paragraph quote\n"
        "interview statement background summary update "
        "event topic category section editor\n"
        "publisher deadline publication edition "
        "circulation reporter correspondent press\n"
        "release breaking news feature article opinion "
        "editorial analysis review headline\n"
        "image caption infographic timeline statistic "
        "eyewitness account eyewitness testimony\n",
        "presentation": "title slide agenda introduction overview "
        "content section conclusion\n"
        "summary speaker note visuals chart graph "
        "bullet point key message audience duration\n"
        "handout transition animation objective "
        "takeaway feedback rehearsal timing layout\n"
        "design theme font color contrast multimedia "
        "video audio hyperlink citation reference\n"
        "quote statistic data comparison highlight "
        "challenge solution recommendation next\n"
        "step closing remark\n",
        "resume": "name contact information summary objective "
        "experience education skill certification\n"
        "achievement reference profile job title employer "
        "date responsibility accomplishment\n"
        "project leadership teamwork communication "
        "problemsolving technical proficiency software\n"
        "language award honor volunteer work internship "
        "publication professional affiliation\n"
        "career goal training workshop seminar professional "
        "development",
    }
}


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_no_file_in_request(client):
    response = client.post("/classify_file")
    assert response.status_code == 400


def test_no_selected_file(client):
    data = {"file": (BytesIO(b""), "")}  # Empty filename
    response = client.post(
        "/classify_file", data=data, content_type="multipart/form-data"
    )
    assert response.status_code == 400


def test_list_file_labels(client):
    response = client.get("/list_file_labels")
    assert response.status_code == 200
    assert response.get_json() == default_labels


def test_list_file_embeddings(client):
    response = client.get("/list_file_embeddings")
    assert response.status_code == 200
    assert response.get_json() == default_embeddings


def test_remove_file_label(client):
    data = {"label": "invoice"}
    response = client.post(
        "/remove_file_label", json=data, content_type="application/json"
    )
    updated_labels = copy.deepcopy(default_labels)
    updated_labels["labels"].remove("invoice")
    assert response.status_code == 200
    assert response.get_json() == updated_labels


def test_add_file_label_without_openai(client):
    """Expect this to fail"""
    data = {"label": "invoice"}
    response = client.post(
        "/add_file_label", json=data, content_type="application/json"
    )
    updated_labels = copy.deepcopy(default_labels)
    updated_labels["labels"].append("invoice")
    assert response.status_code == 500
    assert response.get_json() == {
        "error": "failed to add label invoice, failed to generate a new embedding from OpenAI, OPENAI_API_KEY environment variable needs to be set to query LLM"
    }


@pytest.mark.skip("requires OpenAI API Key to be set and funds for API calls")
def test_add_file_label(client):
    """Only works with OPENAI_API_KEY set"""
    data = {"label": "invoice"}
    response = client.post(
        "/add_file_label", json=data, content_type="application/json"
    )
    updated_labels = copy.deepcopy(default_labels)
    updated_labels["labels"].append("invoice")
    assert response.status_code == 200
    assert response.get_json() == updated_labels


def test_add_file_label_with_embedding(client):
    data = {"label": "memo", "embedding": "memo embedding"}
    response = client.post(
        "/add_file_label", json=data, content_type="application/json"
    )
    assert response.status_code == 200
    assert "memo" in response.get_json()["labels"]
    # Make sure the embedding is correct
    response = client.get("/list_file_embeddings")
    assert response.status_code == 200
    assert response.get_json()["embeddings"]["memo"] == "memo embedding"


def test_classify_file(client, mocker):
    mocker.patch("src.classifier.Classifier.classify", return_value=("test_class", 1.0))

    data = {"file": (BytesIO(b"dummy content"), "file.txt")}
    response = client.post(
        "/classify_file", data=data, content_type="multipart/form-data"
    )
    assert response.status_code == 200
    assert response.get_json() == {"confidence": 1.0, "doc_class": "test_class"}


def test_classify_files(client, mocker):
    mocker.patch("src.classifier.Classifier.classify", return_value=("test_class", 1.0))

    files = {
        "files[]": [
            (BytesIO(b"dummy content"), "drivers_licence_2.jpg",),
            (BytesIO(b"dummy content"), "invoice_1.pdf"),
        ]
    }
    response = client.post(
        "/classify_files", data=files, content_type="multipart/form-data"
    )
    assert response.status_code == 200
    assert response.get_json() == [
        {
            "file": "drivers_licence_2.jpg",
            "result": {"confidence": 1.0, "doc_class": "test_class"},
        },
        {
            "file": "invoice_1.pdf",
            "result": {"confidence": 1.0, "doc_class": "test_class"},
        },
    ]
