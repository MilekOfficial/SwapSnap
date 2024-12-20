# SwapSnap

A modern photo sharing web application built with Flask.

## Features

- User authentication and authorization
- Photo upload with automatic optimization
- Emoji reactions to photos
- Random photo discovery
- Rate limiting for API endpoints
- Responsive design with Bootstrap 5
- Comprehensive error handling and logging

## Prerequisites

- Python 3.8 or higher
- pip package manager
- Virtual environment (recommended)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/swapsnap.git
cd swapsnap
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r req.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory with the following:
```
SECRET_KEY=your-secret-key-here
BASE_URL=http://localhost:8000
```

## Project Structure

```
swapsnap/
├── modules/
│   ├── auth.py         # Authentication logic
│   ├── image_handler.py # Image processing
│   └── reactions.py    # Emoji reactions
├── static/
│   ├── css/
│   └── js/
├── templates/
│   ├── auth.html
│   ├── index.html
│   ├── 404.html
│   └── 500.html
├── tests/
│   └── test_app.py
├── app.py             # Main application
├── req.txt           # Dependencies
└── README.md
```

## Running the Application

1. Start the development server:
```bash
python app.py
```

2. Visit `http://localhost:8000` in your browser

## Running Tests

```bash
pytest tests/
```

## API Endpoints

- `GET /` - Home page
- `POST /upload` - Upload a photo
- `GET /uploads/<filename>` - Retrieve a photo
- `POST /api/reaction` - Add reaction to a photo
- `GET /health` - Health check endpoint

## Security Features

- CSRF protection with Flask-WTF
- Rate limiting with Flask-Limiter
- Secure file uploads with extension validation
- Password hashing for user accounts
- Environment variable management
- Input validation and sanitization

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
