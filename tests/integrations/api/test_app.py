import os.path

import pytest
from fastapi.testclient import TestClient
from src.api import create_app


@pytest.fixture
def client():
    app = create_app()
    return TestClient(app)


def get_auth_header(test_client, username):
    response = test_client.post("/token", data={"username": username, "password": "ciao"})
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    return headers


def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the API!"}


def test_login(client):
    response = client.post("/token", data={"username": "john", "password": "ciao"})
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_get_docs_list(client):
    headers = get_auth_header(client, 'john')
    response = client.get("/users/me/documents", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    # check names
    assert response.json() == ['K-10_docs/10-K_mcdonalds.pdf', 'K-10_docs/amzn-20221231.pdf']


def test_get_doc(client):
    headers = get_auth_header(client, 'john')
    # Assuming you have an existing document named 'example_document.pdf'
    document_name = '10-K_mcdonalds.pdf'
    response = client.get(f"/users/me/documents/{document_name}", headers=headers)
    assert response.status_code == 200
    assert response.headers['Content-Disposition'] == f"attachment; filename={document_name}"
    assert response.headers['Content-Type'] == 'application/octet-stream'


def test_upload_document_admin(client):
    # Simulate an authenticated user (you may need to create a valid UserModel instance)
    headers = get_auth_header(client, 'jarred')

    # Mock the UploadFile object
    class MockUploadFile:
        def __init__(self, filename, file):
            self.filename = filename
            self.file = file

    # Replace 'file_content' with the actual content of the file you want to upload
    file_content = b"Your file content goes here"
    upload_file = MockUploadFile(filename="test_file.txt", file=file_content)

    # Simulate the request to the endpoint
    response = client.post(
        "/users/me/documents",
        files={"file": (upload_file.filename, upload_file.file)},
        data={"folder_path": "K-10_docs"},
        headers=headers,
    )
    # Check the response status code and content
    assert response.status_code == 200
    assert response.json() == {"message": f"Document {upload_file.filename} successfully uploaded to S3!"}


def test_upload_document_non_admin(client):
    # Simulate an authenticated user (you may need to create a valid UserModel instance)
    headers = get_auth_header(client, 'john')

    # Mock the UploadFile object
    class MockUploadFile:
        def __init__(self, filename, file):
            self.filename = filename
            self.file = file

    # Replace 'file_content' with the actual content of the file you want to upload
    file_content = b"Your file content goes here"
    upload_file = MockUploadFile(filename="test_file.txt", file=file_content)
    response = client.post(
        "/users/me/documents",
        files={"file": (upload_file.filename, upload_file.file)},
        data={"folder_path": "K-10_docs"},
        headers=headers,
    )
    assert response.status_code == 401


"""
def test_upload_doc(client):
    # Replace 'test_document.pdf' with the name of the file you want to upload for testing
    filename = os.path.dirname(os.path)
    with open(filename, 'rb') as file:
        response = client.post("/users/me/documents", files={"file": (filename, file)})
    assert response.status_code == 200
    assert "Document test_document.pdf successfully uploaded to S3!" in response.json()["message"]
"""
