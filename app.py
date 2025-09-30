#!/usr/bin/env python3
"""
Feature.fm API Test Dashboard
A Flask application for testing and monitoring Feature.fm API endpoints
"""

import os
import re
import logging
from datetime import datetime
from typing import Any, Dict
from flask import Flask, render_template, request, jsonify, g
from flask_cors import CORS  # type: ignore
from flask_limiter import Limiter  # type: ignore
from flask_limiter.util import get_remote_address  # type: ignore
import requests
import json
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Security: Configure CORS with restricted origins
cors_origins_str = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000')
allowed_origins = cors_origins_str.split(',')
CORS(app, origins=allowed_origins, supports_credentials=True)

# Configure rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per hour", "20 per minute"]
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Feature.fm API Configuration from environment variables
API_KEY = os.getenv('FEATUREFM_API_KEY')
ISS = os.getenv('FEATUREFM_ISS')
SECRET_KEY = os.getenv('FEATUREFM_SECRET_KEY')
BASE_URL = os.getenv('FEATUREFM_BASE_URL', 'https://api.feature.fm')

# Validate required environment variables
if not API_KEY:
    raise ValueError("FEATUREFM_API_KEY environment variable is required")
if not ISS:
    raise ValueError("FEATUREFM_ISS environment variable is required")
if not SECRET_KEY:
    raise ValueError("FEATUREFM_SECRET_KEY environment variable is required")

# Input validation patterns
VALID_ENDPOINT_PATTERN = re.compile(r'^[a-zA-Z0-9/_\-\.]+$')
VALID_METHOD_PATTERN = re.compile(r'^(GET|POST|PUT|DELETE|PATCH)$')
VALID_TEST_ID_PATTERN = re.compile(r'^[a-zA-Z0-9_\-]+$')

# Test results storage
test_results: list[Dict[str, Any]] = []
test_history: list[Dict[str, Any]] = []

def sanitize_for_logging(data: Any) -> str:
    """Sanitize data for logging by removing sensitive information"""
    if isinstance(data, dict):
        sanitized = {}
        for key, value in data.items():
            if any(sensitive in key.lower() for sensitive in ['key', 'secret', 'token', 'password', 'auth']):
                sanitized[key] = '***REDACTED***'
            else:
                sanitized[key] = str(value)[:100] if isinstance(value, str) else value
        return str(sanitized)
    return str(data)[:100]

def validate_endpoint_path(endpoint: str) -> bool:
    """Validate endpoint path to prevent path traversal"""
    if not endpoint or len(endpoint) > 200:
        return False
    if '..' in endpoint or '//' in endpoint:
        return False
    return bool(VALID_ENDPOINT_PATTERN.match(endpoint))

def validate_http_method(method: str) -> bool:
    """Validate HTTP method"""
    return bool(VALID_METHOD_PATTERN.match(method.upper()))

def validate_test_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and sanitize test configuration"""
    validated = {}

    # Validate tests selection
    tests = config.get('tests', 'all')
    if isinstance(tests, str):
        if tests not in ['all']:
            validated['tests'] = 'all'
        else:
            validated['tests'] = tests
    elif isinstance(tests, list):
        # Validate each test ID
        valid_tests = []
        for test_id in tests:
            if isinstance(test_id, str) and VALID_TEST_ID_PATTERN.match(test_id) and len(test_id) <= 50:
                valid_tests.append(test_id)
        validated['tests'] = valid_tests if valid_tests else 'all'  # type: ignore
    else:
        validated['tests'] = 'all'

    return validated

@app.before_request
def security_headers() -> None:
    """Add security headers to all responses"""
    g.start_time = time.time()

@app.after_request
def add_security_headers(response):
    """Add security headers to response"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'

    # Log request with sanitized data
    duration = (time.time() - g.start_time) * 1000
    logger.info(f"{request.method} {request.path} - {response.status_code} - {duration:.2f}ms - IP: {get_remote_address()}")

    return response

@app.route('/')
def index():
    """Serve the dashboard HTML"""
    return render_template('dashboard.html')

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current API configuration (masked)"""
    return jsonify({
        'api_key': API_KEY[:8] + '...' if API_KEY else None,
        'iss': ISS,
        'base_url': BASE_URL,
        'configured': bool(API_KEY and ISS and SECRET_KEY)
    })

@app.route('/api/proxy/<path:endpoint>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
@limiter.limit("10 per minute")
def proxy_api(endpoint: str):
    """
    Proxy API requests to Feature.fm to bypass CORS
    Handles all HTTP methods and forwards headers appropriately
    """
    try:
        # Input validation
        if not validate_endpoint_path(endpoint):
            logger.warning(f"Invalid endpoint path attempted: {sanitize_for_logging(endpoint)}")
            return {'error': 'Invalid endpoint path'}, 400

        if not validate_http_method(request.method):
            logger.warning(f"Invalid HTTP method attempted: {request.method}")
            return {'error': 'Invalid HTTP method'}, 400

        # Validate and sanitize request data
        request_data = None
        if request.method in ['POST', 'PUT', 'PATCH']:
            if request.is_json:
                try:
                    request_data = request.get_json()
                    if not isinstance(request_data, dict):
                        return {'error': 'Request data must be a JSON object'}, 400
                except Exception:
                    return {'error': 'Invalid JSON in request body'}, 400

        # Build headers for Feature.fm API
        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': API_KEY,
            'X-ISS': ISS,
            'X-Secret-Key': SECRET_KEY
        }

        # Get any additional headers from the request (with validation)
        access_id = request.headers.get('X-Access-Id')
        auth_token = request.headers.get('Authorization')

        if access_id and len(access_id) <= 100:
            headers['X-Access-Id'] = access_id
        if auth_token and len(auth_token) <= 500:
            headers['Authorization'] = auth_token

        # Log sanitized request info
        logger.info(f"Proxying {request.method} request to endpoint: {endpoint}")

        # Construct full URL
        url = f"{BASE_URL}/{endpoint}"

        # Add query parameters if present (with validation)
        if request.args:
            from urllib.parse import urlencode
            # Limit query parameters
            if len(dict(request.args)) <= 20:
                url += '?' + urlencode(request.args)

        # Make the request based on method
        response = None
        if request.method == 'GET':
            response = requests.get(url, headers=headers, timeout=30)
        elif request.method == 'POST':
            response = requests.post(url, headers=headers, json=request_data, timeout=30)
        elif request.method == 'PUT':
            response = requests.put(url, headers=headers, json=request_data, timeout=30)
        elif request.method == 'PATCH':
            response = requests.patch(url, headers=headers, json=request_data, timeout=30)
        elif request.method == 'DELETE':
            response = requests.delete(url, headers=headers, timeout=30)

        if response is None:
            return {'error': 'Unsupported HTTP method'}, 405

        # Log response status
        logger.info(f"API response status: {response.status_code}")

        # Return response
        try:
            return response.json(), response.status_code
        except json.JSONDecodeError:
            # Limit response text size for security
            response_text = response.text[:1000] if response.text else ''
            return {'message': response_text}, response.status_code

    except requests.exceptions.Timeout:
        logger.error("Request timeout in proxy")
        return {'error': 'Service temporarily unavailable'}, 504
    except requests.exceptions.RequestException as e:
        logger.error(f"Proxy request error: {sanitize_for_logging(str(e))}")
        return {'error': 'External service error'}, 502
    except Exception as e:
        logger.error(f"Unexpected proxy error: {sanitize_for_logging(str(e))}")
        return {'error': 'Internal server error'}, 500

@app.route('/api/run-tests', methods=['POST'])
@limiter.limit("5 per minute")
def run_tests():
    """Run all Feature.fm API tests"""
    global test_results, test_history
    test_results = []

    try:
        # Get and validate test configuration from request
        raw_config = request.get_json() if request.is_json else {}
        if not isinstance(raw_config, dict):
            return {'error': 'Request must contain a JSON object'}, 400

        test_config = validate_test_config(raw_config)
        logger.info(f"Running tests with config: {sanitize_for_logging(test_config)}")

        selected_tests = test_config.get('tests', 'all')

        # Define comprehensive test cases
        all_test_cases = [
            {
                'id': 'auth',
                'name': 'Authentication Test',
                'description': 'Verify API authentication with credentials',
                'endpoint': 'auth/verify',
                'method': 'GET',
                'category': 'Authentication',
                'data': None
            },
            {
                'id': 'links_list',
                'name': 'List Smart Links',
                'description': 'Retrieve all smart links',
                'endpoint': 'links',
                'method': 'GET',
                'category': 'Links',
                'data': None
            },
            {
                'id': 'links_create',
                'name': 'Create Smart Link',
                'description': 'Create a new smart link',
                'endpoint': 'links',
                'method': 'POST',
                'category': 'Links',
                'data': {
                    'url': 'https://open.spotify.com/track/4PTG3Z6ehGkBFwjybzWkR8',
                    'title': f'Test Link {datetime.now().strftime("%Y%m%d%H%M%S")}',
                    'artist': 'Test Artist',
                    'custom_domain': None
                }
            },
            {
                'id': 'analytics_overview',
                'name': 'Analytics Overview',
                'description': 'Get analytics overview data',
                'endpoint': 'analytics/overview',
                'method': 'GET',
                'category': 'Analytics',
                'params': {
                    'period': '7d'
                },
                'data': None
            },
            {
                'id': 'analytics_clicks',
                'name': 'Click Analytics',
                'description': 'Get detailed click analytics',
                'endpoint': 'analytics/clicks',
                'method': 'GET',
                'category': 'Analytics',
                'params': {
                    'period': '30d',
                    'group_by': 'day'
                },
                'data': None
            },
            {
                'id': 'artists_list',
                'name': 'List Artists',
                'description': 'Retrieve all artists',
                'endpoint': 'artists',
                'method': 'GET',
                'category': 'Artists',
                'data': None
            },
            {
                'id': 'releases_list',
                'name': 'List Releases',
                'description': 'Retrieve all releases',
                'endpoint': 'releases',
                'method': 'GET',
                'category': 'Releases',
                'data': None
            },
            {
                'id': 'campaigns_list',
                'name': 'List Campaigns',
                'description': 'Retrieve all marketing campaigns',
                'endpoint': 'campaigns',
                'method': 'GET',
                'category': 'Campaigns',
                'data': None
            },
            {
                'id': 'pixels_list',
                'name': 'List Tracking Pixels',
                'description': 'Retrieve all tracking pixels',
                'endpoint': 'pixels',
                'method': 'GET',
                'category': 'Tracking',
                'data': None
            },
            {
                'id': 'webhooks_list',
                'name': 'List Webhooks',
                'description': 'Retrieve configured webhooks',
                'endpoint': 'webhooks',
                'method': 'GET',
                'category': 'Webhooks',
                'data': None
            }
        ]

        # Filter tests based on selection
        if selected_tests == 'all':
            test_cases = all_test_cases
        elif isinstance(selected_tests, list):
            test_cases = [t for t in all_test_cases if t['id'] in selected_tests]
        else:
            test_cases = all_test_cases

        # Run each test
        for test in test_cases:
            result = run_single_test(test)
            test_results.append(result)

        # Calculate statistics
        total = len(test_results)
        passed = sum(1 for r in test_results if r['status'] == 'passed')
        failed = sum(1 for r in test_results if r['status'] == 'failed')

        # Store in history
        test_run = {
            'timestamp': datetime.now().isoformat(),
            'total': total,
            'passed': passed,
            'failed': failed,
            'results': test_results
        }
        test_history.append(test_run)

        # Keep only last 10 runs in history
        if len(test_history) > 10:
            test_history = test_history[-10:]
    
        return jsonify(test_run)

    except Exception as e:
        logger.error(f"Error running tests: {sanitize_for_logging(str(e))}")
        return {'error': 'Failed to run tests'}, 500

def run_single_test(test):
    """Run a single API test with comprehensive error handling"""
    start_time = time.time()
    
    headers = {
        'X-API-Key': API_KEY,
        'X-ISS': ISS,
        'X-Secret-Key': SECRET_KEY,
        'Content-Type': 'application/json'
    }
    
    url = f"{BASE_URL}/{test['endpoint']}"
    
    # Add query parameters if present
    params = test.get('params', None)
    
    try:
        # Make the request
        if test['method'] == 'GET':
            response = requests.get(url, headers=headers, params=params, timeout=10)
        elif test['method'] == 'POST':
            response = requests.post(url, headers=headers, json=test['data'], timeout=10)
        elif test['method'] == 'PUT':
            response = requests.put(url, headers=headers, json=test['data'], timeout=10)
        elif test['method'] == 'PATCH':
            response = requests.patch(url, headers=headers, json=test['data'], timeout=10)
        elif test['method'] == 'DELETE':
            response = requests.delete(url, headers=headers, timeout=10)
        
        duration = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        # Determine test status
        if 200 <= response.status_code < 400:
            status = 'passed'
        else:
            status = 'failed'
        
        # Parse response body
        try:
            response_data = response.json()
        except (json.JSONDecodeError, ValueError):
            response_data = response.text[:500] if response.text else None
        
        return {
            'id': test.get('id', ''),
            'name': test['name'],
            'description': test['description'],
            'category': test.get('category', 'General'),
            'endpoint': test['endpoint'],
            'method': test['method'],
            'status': status,
            'statusCode': response.status_code,
            'duration': round(duration, 2),
            'timestamp': datetime.now().isoformat(),
            'response': response_data,
            'request': {
                'headers': {k: v[:20] + '...' if len(v) > 20 else v for k, v in headers.items()},
                'data': test.get('data'),
                'params': params
            }
        }
        
    except requests.exceptions.Timeout:
        return create_error_result(test, 'Timeout', time.time() - start_time)
    except requests.exceptions.ConnectionError:
        return create_error_result(test, 'Connection Error', time.time() - start_time)
    except Exception as e:
        return create_error_result(test, str(e), time.time() - start_time)

def create_error_result(test, error_message, duration):
    """Create a standardized error result"""
    return {
        'id': test.get('id', ''),
        'name': test['name'],
        'description': test['description'],
        'category': test.get('category', 'General'),
        'endpoint': test['endpoint'],
        'method': test['method'],
        'status': 'failed',
        'statusCode': 0,
        'duration': round(duration * 1000, 2),
        'timestamp': datetime.now().isoformat(),
        'error': error_message
    }

@app.route('/api/test-results', methods=['GET'])
def get_test_results():
    """Get the latest test results"""
    if not test_results:
        return jsonify({'message': 'No tests have been run yet'}), 404
    return jsonify(test_results)

@app.route('/api/test-history', methods=['GET'])
def get_test_history():
    """Get test run history"""
    return jsonify(test_history)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint with API connectivity test"""
    api_status = 'unknown'
    
    # Try to verify API connectivity
    try:
        headers = {
            'X-API-Key': API_KEY,
            'X-ISS': ISS,
            'X-Secret-Key': SECRET_KEY
        }
        response = requests.get(f"{BASE_URL}/health", headers=headers, timeout=5)
        api_status = 'connected' if response.status_code < 500 else 'error'
    except (requests.RequestException, Exception):
        api_status = 'disconnected'
    
    return jsonify({
        'status': 'healthy',
        'service': 'Feature.fm API Test Dashboard',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat(),
        'api_status': api_status,
        'environment': os.getenv('FLASK_ENV', 'production')
    })

@app.errorhandler(400)
def bad_request(error):
    """Handle 400 errors"""
    logger.warning(f"Bad request from {get_remote_address()}: {sanitize_for_logging(str(error))}")
    return jsonify({'error': 'Bad request'}), 400

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    logger.info(f"404 error from {get_remote_address()}: {request.path}")
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors"""
    logger.warning(f"Method not allowed from {get_remote_address()}: {request.method} {request.path}")
    return jsonify({'error': 'Method not allowed'}), 405

@app.errorhandler(429)
def ratelimit_handler(e):
    """Handle rate limit exceeded errors"""
    logger.warning(f"Rate limit exceeded from {get_remote_address()}: {e.description}")
    return jsonify({'error': 'Rate limit exceeded', 'message': 'Too many requests'}), 429

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {sanitize_for_logging(str(error))}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"""
    ╔══════════════════════════════════════════════╗
    ║     Feature.fm API Test Dashboard            ║
    ║                                              ║
    ║     Running on: http://localhost:{port}      ║
    ║     Debug mode: {debug}                      ║
    ╚══════════════════════════════════════════════╝
    """)
    
    # Security: Only bind to localhost to prevent external access
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    app.run(debug=debug, port=port, host=host)