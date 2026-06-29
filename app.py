from flask import Flask, render_template, request, jsonify, send_file, redirect
import json, os
from datetime import datetime
import smtplib
from email.message import EmailMessage
app = Flask(__name__)

PROJECTS = [
    {
        "id": 1,
        "title": "Telecom Customer Retention System",
        "desc": "End-to-end ML pipeline predicting customer churn in telecom. Covers data normalization, feature engineering, model training, evaluation, and deployment-ready insight generation.",
        "tech": ["Python", "Scikit-Learn", "Pandas", "NumPy"],
        "github": "https://github.com/mirzaasadijaz/Telecom-Customer-Retention-Intelligence-System",
        "cat": "ml", "emoji": "📡", 
    },
    {
        "id": 2,
        "title": "Movie Recommendation Engine",
        "desc": "Content-based recommender using TF-IDF vectorization and cosine similarity to suggest films by analyzing genre patterns and user-generated metadata tags.",
        "tech": ["Python", "NLP", "Scikit-Learn", "TF-IDF"],
        "github": "https://github.com/mirzaasadijaz/Movie-Recommendation-Model",
        "cat": "ml", "emoji": "🎬", 
    },
    {
        "id": 3,
        "title": "Google Trends Analyzer",
        "desc": "Market intelligence platform leveraging Google Trends API to map seasonal demand, identify high-value keywords, and uncover competitive patterns from live search data.",
        "tech": ["Python", "Google API", "Pandas", "Plotly"],
        "github": "https://github.com/mirzaasadijaz/Google-Search-Analysis",
        "cat": "analytics", "emoji": "📊",
    },
    {
        "id": 4,
        "title": "JARVIS AI Assistant",
        "desc": "Desktop AI assistant with two-tier NLP architecture. Processes natural voice commands to automate web browsing, play music, and retrieve live information hands-free.",
        "tech": ["Python", "NLP", "Speech Recognition", "Automation"],
        "github": "https://github.com/mirzaasadijaz/JARVIS",
        "cat": "automation", "emoji": "🤖",
    },
    {
        "id": 5,
        "title": "Facebook Auto Poster",
        "desc": "Selenium-powered automation handling login, group navigation, media uploads, and anonymous post toggles with smart error recovery for reliable batch posting operations.",
        "tech": ["Python", "Selenium", "Web Scraping"],
        "github": "https://github.com/mirzaasadijaz/Facebook-Auto-Poster",
        "cat": "automation", "emoji": "📱",
    },
    {
        "id": 6,
        "title": "FB Group Automator",
        "desc": "Desktop GUI automation toolkit with modern dark interface, multi-profile management, and smart login handling for automating Facebook Group comment workflows at scale.",
        "tech": ["Python", "Selenium", "Tkinter", "GUI"],
        "github": "https://github.com/mirzaasadijaz/-FB-Group-Automator",
        "cat": "automation", "emoji": "⚡", 
    },
    {
        "id": 7,
        "title": "LMS-Result-Scraper-and-Analyzer",
        "desc": "Python-based ETL pipeline that uses Selenium to scrape student results from the UAF LMS portal and Pandas to clean data, calculate GPAs, and track historical academic performance.",
        "tech": ["Python", "Selenium","Pandas", "Web Scraping"],
        "github": "https://github.com/mirzaasadijaz/LMS-Result-Scraper-and-Analyzer",
        "cat": "analytics", "emoji": "🎓", 
    },
    {
        "id": 8,
        "title": "Ecommerce Data Analysis",
        "desc": "The primary objective of this project is to explore retail sales data to identify trends, seasonal patterns, and profitability across different customer segments and geographic regions.",
        "tech": ["Python", "Ploty","Pandas", "Seaborn & Matplotlib"],
        "github": "https://github.com/mirzaasadijaz/ecommerce-data-analysis",
        "cat": "analytics", "emoji": "🛒", 
    },
    {
        "id": 9,
        "title": "Website Performance Analysis",
        "desc": "The goal of this analysis is to understand how users interact with the website over time. By correlating Sessions with Engagement Rates, the project seeks to identify high-traffic periods and determine the quality of user interaction during those times.",
        "tech": ["Python", "Seaborn & Matplotlib","Pandas"],
        "github": "https://github.com/mirzaasadijaz/Website-Performance-Analysis",
        "cat": "analytics", "emoji": "🌐", 
    },
]

@app.route('/')
def index():
    return render_template('index.html', projects=PROJECTS)
    
@app.route('/download-resume')
def download_resume():
    path = os.path.join(app.static_folder, 'resume.pdf')
    if os.path.exists(path):
        return send_file(path, as_attachment=True, download_name='Asad_Ijaz_DataScientist_Resume.pdf')
    return redirect('https://linkedin.com/in/asad-ijaz-data-scientist')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
