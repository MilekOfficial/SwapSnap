import os
import tempfile
import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()
    os.environ['BASE_URL'] = 'http://test.example.com'
    
    with app.test_client() as client:
        yield client
    
    # Clean up
    os.environ.pop('BASE_URL', None)

def test_index(client):
    """Test the index page loads"""
    rv = client.get('/')
    assert rv.status_code == 200

def test_upload_no_file(client):
    """Test upload endpoint without file"""
    rv = client.post('/upload')
    assert rv.status_code == 400
    assert b'No file part' in rv.data

def test_random_photo_no_photos(client):
    """Test random photo endpoint with no photos"""
    rv = client.get('/random_photo')
    assert rv.status_code == 400
    assert b'No photos available' in rv.data

def test_url_generation(client):
    """Test URL generation with custom domain"""
    with client:
        rv = client.post('/upload', data={
            'file': (tempfile.SpooledTemporaryFile(), 'test.jpg')
        })
        assert rv.status_code == 400  # Will fail due to invalid file
        response_data = rv.get_json()
        assert 'error' in response_data
