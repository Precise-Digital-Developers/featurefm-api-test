# Feature.fm API Test Suite

A testing framework for the Feature.fm music marketing platform API,
featuring both command-line and web dashboard interfaces.

## Features

- 🎵 Complete API endpoint testing
- 🖥️ Interactive web dashboard
- 📊 Detailed test results and analytics
- 🔄 Automatic retry logic with exponential backoff
- 📝 JSON result export

## Prerequisites

- Python 3.10+
- Feature.fm API credentials (API key, ISS, Secret key)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/featurefm-api-tests.git
cd featurefm-api-tests
```

1. Install dependencies:

```bash
pip install -r requirements.txt
```

1. Set up environment variables:

```bash
cp .env.example .env
# Edit .env with your actual credentials
```

## Usage

### Command Line Interface

Run all tests:

```bash
python featurefm_api_tests.py
```

Run specific test:

```bash
python featurefm_api_tests.py --test create_smartlink
```

List available tests:

```bash
python featurefm_api_tests.py --list-tests
```

### Web Dashboard

1. Start the Flask server:

```bash
python app.py
```

1. Open your browser to `http://localhost:5000`

## Available Tests

### Authentication

- Basic API key authentication
- JWT token authentication

### Artist Management

- List artists
- Create artist
- Get artist details

### Smart Links

- Create smart link
- List smart links
- Get smart link analytics

### Campaigns

- Create pre-save campaign
- List campaigns

### Additional Features

- Action pages
- Releases
- Webhooks
- Analytics
- Partners API

## Configuration

Create a `.env` file with your credentials:

```env
FEATUREFM_API_KEY=your_api_key
FEATUREFM_ISS=your_iss_identifier
FEATUREFM_SECRET_KEY=your_secret_key
FEATUREFM_BASE_URL=https://api.feature.fm
```

## Project Structure

```text
featurefm-api-tests/
├── featurefm_api_tests.py  # Main test suite
├── app.py                  # Flask dashboard server
├── templates/
│   └── dashboard.html      # Dashboard UI
├── .env                    # Environment variables (not tracked)
├── .env.example            # Example environment file
├── requirements.txt        # Python dependencies
└── README.md               # This file
```
