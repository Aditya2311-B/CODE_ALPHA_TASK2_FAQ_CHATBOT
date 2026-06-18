import json
import io
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, send_file
from flask_login import login_required, current_user
from database import db, FAQ
from dashboard.analytics import get_analytics_summary
from chatbot import vectorizer

dashboard_bp = Blueprint('dashboard', __name__)

def refit_vectorizer():
    """Helper to refit the chatbot vectorizer when FAQ data changes."""
    all_faqs = FAQ.query.all()
    vectorizer.fit_faqs(all_faqs)

@dashboard_bp.route('/dashboard')
@login_required
def home():
    """
    Renders FAQ management CRUD dashboard.
    Supports a 'search' query parameter for keyword searches.
    """
    search_query = request.args.get('search', '').strip()
    
    if search_query:
        faqs = FAQ.query.filter(
            FAQ.question.like(f"%{search_query}%") |
            FAQ.answer.like(f"%{search_query}%") |
            FAQ.category.like(f"%{search_query}%")
        ).all()
    else:
        faqs = FAQ.query.all()
        
    total_count = FAQ.query.count()
    return render_template(
        'dashboard.html', 
        faqs=faqs, 
        total_count=total_count, 
        search_query=search_query
    )

@dashboard_bp.route('/dashboard/analytics')
@login_required
def analytics_view():
    """Renders the Analytics dashboard containing Chart.js data models."""
    stats = get_analytics_summary()
    return render_template('analytics.html', stats=stats)

@dashboard_bp.route('/dashboard/upload', methods=['POST'])
@login_required
def upload_faqs():
    """
    Allows admins to upload a JSON file containing FAQs.
    Merges uploaded items, skipping exact duplicates by question string.
    """
    if 'file' not in request.files:
        flash("No file part in the request", "danger")
        return redirect(url_for('dashboard.home'))
        
    file = request.files['file']
    if file.filename == '':
        flash("No selected file", "danger")
        return redirect(url_for('dashboard.home'))
        
    if file and file.filename.endswith('.json'):
        try:
            content = file.read().decode('utf-8')
            faq_list = json.loads(content)
            
            if not isinstance(faq_list, list):
                flash("Invalid JSON format. Expected a list of FAQ objects.", "danger")
                return redirect(url_for('dashboard.home'))
                
            added_count = 0
            for item in faq_list:
                q = item.get('question')
                a = item.get('answer')
                cat = item.get('category', 'General')
                if q and a:
                    # check if duplicate question exists to avoid double inserts
                    existing = FAQ.query.filter_by(question=q).first()
                    if not existing:
                        faq = FAQ(question=q, answer=a, category=cat)
                        db.session.add(faq)
                        added_count += 1
                        
            db.session.commit()
            refit_vectorizer() # Recache vectors
            flash(f"Successfully uploaded FAQ file. Added {added_count} new FAQs.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error parsing JSON: {str(e)}", "danger")
    else:
        flash("Please upload a valid JSON file.", "danger")
        
    return redirect(url_for('dashboard.home'))

@dashboard_bp.route('/dashboard/download')
@login_required
def download_faqs():
    """
    Exports the current database FAQs into a download-ready JSON file.
    """
    faqs = FAQ.query.all()
    faq_data = [faq.to_dict() for faq in faqs]
    
    # Send as JSON attachment
    json_str = json.dumps(faq_data, indent=2)
    bytes_io = io.BytesIO(json_str.encode('utf-8'))
    
    return send_file(
        bytes_io,
        mimetype='application/json',
        as_attachment=True,
        download_name='faqs_export.json'
    )
