from flask import Flask, render_template, request, jsonify
import pandas as pd
from urllib.parse import urlparse
import http.cookiejar
import urllib.request
import browser_cookie3
import json
from datetime import datetime
from flask import Flask, request, jsonify
import platform
import json
import uuid
import datetime
import requests
import user_agents
from geopy.geocoders import Nominatim
import socket
import psutil
import screeninfo
from http.cookies import SimpleCookie

app = Flask(__name__)

def analyze_cookies(url):
    """Analyze cookies from a given URL"""
    try:
        # Set up headers to mimic a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

        # Make the request
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Get cookies from response
        cookies_data = []
        
        # Process cookies from response
        for cookie_name, cookie_value in response.cookies.items():
            cookie = response.cookies.get(cookie_name)
            cookie_purpose = get_detailed_cookie_purpose(cookie_name, str(cookie_value))
            data_collected = analyze_cookie_data(cookie_name, str(cookie_value))
            
            # Get expiration date
            expires = cookie.expires if hasattr(cookie, 'expires') else None
            if expires:
                expires = datetime.datetime.fromtimestamp(expires).strftime('%Y-%m-%d %H:%M:%S')
            else:
                expires = 'Session'

            cookie_info = {
                'name': cookie_name,
                'value': str(cookie_value)[:20] + '...' if len(str(cookie_value)) > 20 else str(cookie_value),
                'domain': cookie.domain if hasattr(cookie, 'domain') else response.url,
                'path': cookie.path if hasattr(cookie, 'path') else '/',
                'secure': cookie.secure if hasattr(cookie, 'secure') else False,
                'expires': expires,
                'risk_level': assess_cookie_risk(cookie),
                'purpose': cookie_purpose,
                'data_collected': data_collected
            }
            cookies_data.append(cookie_info)

        # Also check Set-Cookie headers for additional cookies
        if 'Set-Cookie' in response.headers:
            cookie = SimpleCookie()
            cookie.load(response.headers['Set-Cookie'])
            for key, morsel in cookie.items():
                if not any(c['name'] == key for c in cookies_data):
                    cookie_purpose = get_detailed_cookie_purpose(key, morsel.value)
                    data_collected = analyze_cookie_data(key, morsel.value)
                    
                    cookie_info = {
                        'name': key,
                        'value': morsel.value[:20] + '...' if len(morsel.value) > 20 else morsel.value,
                        'domain': morsel['domain'] if 'domain' in morsel else response.url,
                        'path': morsel['path'] if 'path' in morsel else '/',
                        'secure': 'secure' in morsel,
                        'expires': morsel['expires'] if 'expires' in morsel else 'Session',
                        'risk_level': 'Medium',  # Default risk level for header cookies
                        'purpose': cookie_purpose,
                        'data_collected': data_collected
                    }
                    cookies_data.append(cookie_info)

        return cookies_data

    except requests.exceptions.RequestException as e:
        return f"Could not connect to the website: {str(e)}"
    except Exception as e:
        return f"Error analyzing website: {str(e)}"

def get_detailed_cookie_purpose(name, value):
    """Get detailed information about what the cookie is used for"""
    name = name.lower()
    
    purposes = {
        'guest_id': 'Tracks your unique visitor identity across sessions',
        'personalization_id': 'Stores your personalization preferences and browsing history',
        '_ga': 'Tracks your behavior, including pages visited and time spent',
        'fbp': 'Tracks your activity across websites with Facebook integration',
        'csrf': 'Protects you from cross-site request forgery attacks',
        'session': 'Maintains your login status and session data',
        'lang': 'Remembers your language preference',
        'theme': 'Stores your visual preference settings',
        '_gid': 'Identifies unique users within a 24-hour period',
        'ads': 'Used for targeted advertising based on your interests',
    }
    
    # Match partial cookie names
    for key, purpose in purposes.items():
        if key in name:
            return purpose
            
    return "Stores website preferences and tracking data"

def analyze_cookie_data(name, value):
    """Analyze what kind of data is stored in the cookie"""
    name = name.lower()
    collected_data = []
    
    data_indicators = {
        'id': 'Your unique identifier',
        'user': 'Your user preferences',
        'session': 'Your current browsing session',
        'login': 'Your login status',
        'auth': 'Your authentication details',
        'track': 'Your browsing behavior',
        'analytics': 'Your interaction patterns',
        'ads': 'Your advertising profile',
        'geo': 'Your approximate location',
        'lang': 'Your language preference',
        'theme': 'Your visual preferences',
        'consent': 'Your cookie preferences',
    }
    
    # Check value format for additional insights
    if value:
        if len(value) > 100:
            collected_data.append("Detailed tracking data")
        if value.isdigit():
            collected_data.append("Numerical identifier")
        if 'timestamp' in value.lower():
            collected_data.append("Time-based tracking")
            
    # Match cookie name patterns
    for indicator, data_type in data_indicators.items():
        if indicator in name:
            collected_data.append(data_type)
    
    return collected_data if collected_data else ["Basic website interaction data"]

def assess_cookie_risk(cookie):
    """Assess the privacy risk level of a cookie"""
    name = cookie.name.lower() if hasattr(cookie, 'name') else ''
    
    # High risk indicators
    high_risk = ['track', 'analytic', 'gtm', 'pixel', 'fb', 'google']
    # Medium risk indicators
    medium_risk = ['session', 'user', 'pref', 'id']
    # Low risk indicators
    low_risk = ['csrf', 'security', 'locale', 'language']

    for term in high_risk:
        if term in name:
            return 'High'
            
    for term in medium_risk:
        if term in name:
            return 'Medium'
            
    for term in low_risk:
        if term in name:
            return 'Low'
            
    return 'Medium'  # Default risk level

def get_real_user_data(request_headers):
    """Collect real data that websites can access about the user"""
    user_agent = user_agents.parse(request_headers.get('User-Agent', ''))
    
    # Basic browser/device data
    browser_data = {
        'browser': user_agent.browser.family,
        'browser_version': user_agent.browser.version_string,
        'os': user_agent.os.family,
        'device': user_agent.device.family if user_agent.device.family != 'Other' else 'Desktop/Laptop'
    }
    
    # Screen and window data
    try:
        screens = screeninfo.get_monitors()
        screen_data = {
            'resolution': f"{screens[0].width}x{screens[0].height}",
            'color_depth': screens[0].width_mm  # in bits
        }
    except:
        screen_data = {
            'resolution': 'Unable to detect',
            'color_depth': 'Unable to detect'
        }
    
    # Time and locale data
    time_data = {
        'timezone': datetime.datetime.now().astimezone().tzname(),
        'local_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'language': request_headers.get('Accept-Language', 'Unknown')
    }
    
    # Network data
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        
        # Get public IP (using a public API)
        public_ip_response = requests.get('https://api.ipify.org?format=json')
        public_ip = public_ip_response.json()['ip'] if public_ip_response.status_code == 200 else 'Unknown'
        
        # Get location from IP
        geolocator = Nominatim(user_agent="cookieleak")
        location = geolocator.geocode(public_ip)
        
        network_data = {
            'ip_address': public_ip,
            'approximate_location': f"{location.city}, {location.country}" if location else 'Unknown',
            'connection_type': 'Wifi/Ethernet',  # This is approximate
            'isp': socket.getfqdn(public_ip)
        }
    except:
        network_data = {
            'ip_address': 'Protected',
            'approximate_location': 'Protected',
            'connection_type': 'Protected',
            'isp': 'Protected'
        }
    
    # System resources (can indicate device type/performance)
    system_data = {
        'cpu_cores': psutil.cpu_count(),
        'memory_total': f"{round(psutil.virtual_memory().total / (1024.0 ** 3), 2)} GB",
        'platform': platform.system(),
        'platform_version': platform.version()
    }
    
    # Browser capabilities and settings
    browser_capabilities = {
        'cookies_enabled': request_headers.get('Cookie') is not None,
        'javascript_enabled': True,  # This will be verified client-side
        'do_not_track': request_headers.get('DNT') == '1',
        'plugins': [],  # Will be populated client-side
        'fonts': []  # Will be populated client-side
    }
    
    return {
        'browser_data': browser_data,
        'screen_data': screen_data,
        'time_data': time_data,
        'network_data': network_data,
        'system_data': system_data,
        'browser_capabilities': browser_capabilities
    }

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        url = request.form.get('url', '')
        print(f"Received URL: {url}")
        
        url = url.strip().lower()
        url = url.replace('http://', '').replace('https://', '')
        url = url.split('/')[0]
        url = f'https://{url}'
        
        session = requests.Session()
        response = session.get(url, 
                           timeout=5,
                           headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124'},
                           allow_redirects=True)
        
        cookies_data = []
        
        # Process both session cookies and response cookies
        all_cookies = {**session.cookies.get_dict(), **response.cookies.get_dict()}
        
        for name, value in all_cookies.items():
            cookie_info = {
                'name': name,
                'value': value,  # Show the actual value
                'domain': response.url,
                'expires': 'Session',
                'risk_level': analyze_cookie_risk(name, value),
                'purpose': analyze_cookie_purpose(name, value),
                'data_collected': analyze_cookie_content(name, value)
            }
            cookies_data.append(cookie_info)
        
        return jsonify({
            'cookies': cookies_data,
            'stats': {
                'total_cookies': len(cookies_data),
                'high_risk': len([c for c in cookies_data if c['risk_level'] == 'High']),
                'medium_risk': len([c for c in cookies_data if c['risk_level'] == 'Medium']),
                'low_risk': len([c for c in cookies_data if c['risk_level'] == 'Low'])
            }
        })
            
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'})

def analyze_cookie_risk(name, value):
    """Analyze the risk level based on cookie content"""
    name = name.lower()
    high_risk_indicators = ['id', 'uid', 'guid', 'track', 'analytic', 'visitor']
    medium_risk_indicators = ['pref', 'session', 'login', 'auth']
    
    if any(indicator in name for indicator in high_risk_indicators):
        return 'High'
    if any(indicator in name for indicator in medium_risk_indicators):
        return 'Medium'
    return 'Low'

def analyze_cookie_purpose(name, value):
    """Analyze what the cookie is used for"""
    name = name.lower()
    purposes = {
        'id': 'Identifies you uniquely across sessions',
        'session': 'Maintains your current session state',
        'auth': 'Keeps you logged in',
        'pref': 'Stores your preferences',
        'theme': 'Remembers your visual settings',
        'lang': 'Stores your language preference',
        'track': 'Tracks your behavior on the site',
        'analytic': 'Analyzes how you use the site',
        'ads': 'Used for targeted advertising'
    }
    
    for key, purpose in purposes.items():
        if key in name:
            return purpose
    return 'General website functionality'

def analyze_cookie_content(name, value):
    """Analyze what information is stored in the cookie"""
    collected_data = []
    
    # Check for common patterns in the value
    if len(value) > 100:
        collected_data.append(f"Large data string ({len(value)} characters)")
    
    try:
        # Check if it's JSON
        json_data = json.loads(value)
        collected_data.append(f"Structured data: {list(json_data.keys())}")
    except:
        # Check for common patterns
        if value.isdigit():
            collected_data.append(f"Numeric identifier: {value}")
        elif '.' in value and all(part.isdigit() for part in value.split('.')):
            collected_data.append(f"Version or ID: {value}")
        elif len(value) == 32 or len(value) == 64:
            collected_data.append(f"Hashed identifier ({len(value)} characters)")
        elif 'true' in value.lower() or 'false' in value.lower():
            collected_data.append(f"Boolean setting: {value}")
        else:
            # Show a preview of the actual value
            preview = value[:50] + '...' if len(value) > 50 else value
            collected_data.append(f"Value: {preview}")
    
    return collected_data

@app.route('/get_user_data', methods=['GET'])
def get_user_data():
    """Endpoint to get real-time user data"""
    user_data = get_real_user_data(request.headers)
    return jsonify(user_data)

if __name__ == '__main__':
    app.run(debug=True)