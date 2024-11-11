from flask import Flask, render_template, request, jsonify, session
import json
import requests
import qrcode
from io import BytesIO
from constants import COOKIE_CATEGORIES, COOKIE_PURPOSES
import base64  # Import base64 for encoding

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management

# Your USDT address
USDT_ADDRESS = "0xDC92534Be92780c87f232CD525D99e26892E15f7"  # Update this to your actual USDT address

def categorize_cookie(name):
    """Categorize cookie based on its name"""
    name = name.lower()
    for category, info in COOKIE_CATEGORIES.items():
        if any(pattern in name for pattern in info['patterns']):
            return category, info['icon'], info['description']
    return 'Others', '🔸', 'Miscellaneous purposes'

def analyze_cookie_purpose(name, category):
    """Get cookie purpose based on its name and category"""
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
            url = f'https://{url.strip().lower().replace("http://", "").replace("https://", "").split("/")[0]}'
            http_session = requests.Session()
            response = http_session.get(url, allow_redirects=True)

            for cookie in response.cookies:
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
                    'source': url  # Add the source URL for context
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
