import os
import pytest
from PIL import Image
from io import BytesIO
from app import app
from modules.image_handler import process_image

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_route(client):
    """Test the index route returns 200."""
    rv = client.get('/')
    assert rv.status_code == 200

def test_health_check(client):
    """Test the health check endpoint."""
    rv = client.get('/health')
    assert rv.status_code == 200
    assert rv.json['status'] == 'healthy'

def test_404_handler(client):
    """Test 404 error handler."""
    rv = client.get('/nonexistent')
    assert rv.status_code == 404

def test_upload_no_file(client):
    """Test upload endpoint with no file."""
    rv = client.post('/upload')
    assert rv.status_code == 400
    assert b'No file part' in rv.data

def test_upload_empty_file(client):
    """Test upload endpoint with empty file."""
    rv = client.post('/upload', data={'file': (BytesIO(), '')})
    assert rv.status_code == 400
    assert b'No selected file' in rv.data

def test_upload_invalid_extension(client):
    """Test upload endpoint with invalid file extension."""
    data = {'file': (BytesIO(b'my file contents'), 'test.txt')}
    rv = client.post('/upload', data=data)
    assert rv.status_code == 400
    assert b'File type not allowed' in rv.data

def test_image_processing():
    """Test image processing function."""
    # Create a test image
    img = Image.new('RGB', (2000, 1500), color='red')
    img_io = BytesIO()
    img.save(img_io, 'JPEG')
    img_io.seek(0)
    
    # Process the image
    result = process_image(img_io)
    
    # Check if result is valid
    assert result is not None
    
    # Check if image was resized
    processed_img = Image.open(result)
    assert processed_img.size[0] <= 1920
    assert processed_img.size[1] <= 1080

def test_auth_routes(client):
    """Test authentication routes."""
    # Test login page
    rv = client.get('/auth')
    assert rv.status_code == 200
    
    # Test login with invalid credentials
    rv = client.post('/login', data={
        'username': 'test',
        'password': 'wrong'
    })
    assert rv.status_code == 302  # Redirect
    
    # Test registration
    rv = client.post('/register', data={
        'username': 'newuser',
        'email': 'test@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    })
    assert rv.status_code == 302  # Redirect
