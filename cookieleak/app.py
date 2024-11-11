from flask import Flask, render_template, request, jsonify, session
import json
import requests
import qrcode
from io import BytesIO
from constants import COOKIE_CATEGORIES, COOKIE_PURPOSES
import base64

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Your USDT address
USDT_ADDRESS = "0xDC92534Be92780c87f232CD525D99e26892E15f7"

def categorize_cookie(name):
    """Categorize cookie based on its name."""
    name = name.lower()
    for category, info in COOKIE_CATEGORIES.items():
        if any(pattern in name for pattern in info['patterns']):
            return category, info['icon'], info['description']
    return 'Others', '🔸', 'Miscellaneous purposes'

def analyze_cookie_purpose(name, category):
    """Get cookie purpose based on its name and category."""
    name = name.lower()
    if category in COOKIE_PURPOSES:
        for pattern, purpose in COOKIE_PURPOSES[category].items():
            if pattern in name and pattern != 'default':
                return purpose
        return COOKIE_PURPOSES[category]['default']
    return 'General website functionality'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        urls = request.form.get('urls', '').split(',')
        cookies_data = []

        for url in urls:
            base_url = f'https://{url.strip().lower().replace("http://", "").replace("https://", "").split("/")[0]}'
            http_session = requests.Session()

            # Initial request to collect cookies
            response = http_session.get(base_url, allow_redirects=True)

            # Attempt to trigger additional cookies by simulating browser headers
            additional_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Connection': 'keep-alive',
                'Referer': base_url,
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Upgrade-Insecure-Requests': '1'
            }

            # Request multiple times to attempt to gather more cookies
            paths_to_try = ['', '/about', '/contact', '/privacy']
            for path in paths_to_try:
                response = http_session.get(f"{base_url}{path}", headers=additional_headers, allow_redirects=True)

            # Collect all cookies
            for cookie in http_session.cookies:
                name = cookie.name
                value = cookie.value
                category, icon, description = categorize_cookie(name)
                cookie_info = {
                    'name': name,
                    'value': value,
                    'category': category,
                    'category_icon': icon,
                    'category_description': description,
                    'risk_level': analyze_cookie_risk(name, value),
                    'purpose': analyze_cookie_purpose(name, category),
                    'data_collected': analyze_cookie_content(name, value),
                    'source': url
                }
                cookies_data.append(cookie_info)

        # Store cookies data in Flask's session
        session['cookies_data'] = cookies_data

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
    name = name.lower()
    high_risk_indicators = ['id', 'uid', 'guid', 'track', 'analytic', 'visitor']
    medium_risk_indicators = ['pref', 'session', 'login', 'auth']
    if any(indicator in name for indicator in high_risk_indicators):
        return 'High'
    if any(indicator in name for indicator in medium_risk_indicators):
        return 'Medium'
    return 'Low'

def analyze_cookie_content(name, value):
    collected_data = []
    if len(value) > 100:
        collected_data.append(f"Large data string ({len(value)} characters)")
    try:
        json_data = json.loads(value)
        collected_data.append(f"Structured data: {list(json_data.keys())}")
    except:
        if value.isdigit():
            collected_data.append(f"Numeric identifier: {value}")
        elif '.' in value and all(part.isdigit() for part in value.split('.')):
            collected_data.append(f"Version or ID: {value}")
        elif len(value) in [32, 64]:
            collected_data.append(f"Hashed identifier ({len(value)} characters)")
        elif 'true' in value.lower() or 'false' in value.lower():
            collected_data.append(f"Boolean setting: {value}")
        else:
            preview = value[:50] + '...' if len(value) > 50 else value
            collected_data.append(f"Value: {preview}")
    return collected_data

@app.route('/donate')
def donate():
    # Generate QR code for the USDT address
    qr = qrcode.make(USDT_ADDRESS)
    qr_image = BytesIO()
    qr.save(qr_image, format='PNG')
    qr_image.seek(0)

    # Encode the image to base64
    qr_image_base64 = base64.b64encode(qr_image.getvalue()).decode('utf-8')

    return render_template('donate.html', usdt_address=USDT_ADDRESS, qr_image=qr_image_base64)

if __name__ == '__main__':
    app.run(debug=True)
