from flask import Flask, render_template, request, jsonify
import pandas as pd
from urllib.parse import urlparse
import http.cookiejar
import urllib.request
import browser_cookie3
import json
from datetime import datetime

app = Flask(__name__)

def analyze_cookies(url):
    """Analyze cookies from a given URL"""
    cookie_jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
    
    try:
        opener.open(url)
        cookies_data = []
        
        for cookie in cookie_jar:
            cookie_info = {
                'name': cookie.name,
                'value': cookie.value[:20] + '...' if len(cookie.value) > 20 else cookie.value,
                'domain': cookie.domain,
                'path': cookie.path,
                'secure': cookie.secure,
                'expires': datetime.fromtimestamp(cookie.expires).strftime('%Y-%m-%d %H:%M:%S') if cookie.expires else 'Session',
                'risk_level': assess_cookie_risk(cookie)
            }
            cookies_data.append(cookie_info)
            
        return cookies_data
    except Exception as e:
        return str(e)

def assess_cookie_risk(cookie):
    """Assess the privacy risk level of a cookie"""
    risk_score = 0
    
    # Check for third-party cookies
    if not cookie.domain.startswith('.'):
        risk_score += 2
        
    # Check for long expiration dates
    if cookie.expires:
        days_until_expiry = (datetime.fromtimestamp(cookie.expires) - datetime.now()).days
        if days_until_expiry > 365:
            risk_score += 2
            
    # Check for secure flag
    if not cookie.secure:
        risk_score += 1
        
    if risk_score <= 1:
        return 'Low'
    elif risk_score <= 3:
        return 'Medium'
    else:
        return 'High'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    url = request.form.get('url')
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
        
    cookies_data = analyze_cookies(url)
    if isinstance(cookies_data, str):
        return jsonify({'error': cookies_data})
        
    stats = {
        'total_cookies': len(cookies_data),
        'high_risk': len([c for c in cookies_data if c['risk_level'] == 'High']),
        'medium_risk': len([c for c in cookies_data if c['risk_level'] == 'Medium']),
        'low_risk': len([c for c in cookies_data if c['risk_level'] == 'Low'])
    }
    
    return jsonify({
        'cookies': cookies_data,
        'stats': stats
    })

if __name__ == '__main__':
    app.run(debug=True)