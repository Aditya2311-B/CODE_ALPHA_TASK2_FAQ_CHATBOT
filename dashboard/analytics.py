from sqlalchemy import func
from datetime import datetime, timedelta
from database import db, FAQ, ChatSession, ChatMessage, AnalyticsLog, User

def get_analytics_summary():
    """
    Query database and compute statistics for the analytics dashboard.
    """
    # 1. Total FAQ Count
    total_faqs = FAQ.query.count()

    # 2. Total Queries Logged
    total_queries = AnalyticsLog.query.count()

    # 3. Active Users (Users who asked a query in the last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    active_users = db.session.query(
        func.count(func.distinct(AnalyticsLog.user_id))
    ).filter(AnalyticsLog.timestamp >= seven_days_ago).scalar() or 0

    # 4. Average Confidence Score
    avg_confidence = db.session.query(
        func.avg(AnalyticsLog.confidence_score)
    ).scalar()
    avg_confidence = float(avg_confidence) * 100 if avg_confidence is not None else 0.0

    # 5. Most Asked Questions (Top 5 matched FAQs)
    most_asked = db.session.query(
        FAQ.question,
        func.count(AnalyticsLog.id).label('count')
    ).join(AnalyticsLog, FAQ.id == AnalyticsLog.matched_faq_id)\
     .group_by(FAQ.id)\
     .order_by(func.count(AnalyticsLog.id).desc())\
     .limit(5).all()
     
    most_asked_data = [{"question": row[0], "count": row[1]} for row in most_asked]

    # 6. Chats/Queries per Day (Last 7 Days)
    daily_chats = db.session.query(
        func.date(AnalyticsLog.timestamp).label('date'),
        func.count(AnalyticsLog.id).label('count')
    ).filter(AnalyticsLog.timestamp >= seven_days_ago)\
     .group_by(func.date(AnalyticsLog.timestamp))\
     .order_by('date')\
     .all()
     
    daily_chats_data = [{"date": str(row[0]), "count": row[1]} for row in daily_chats]

    # If the daily chats data is empty, let's prepopulate with today's date and 0 count
    if not daily_chats_data:
        today_str = datetime.utcnow().strftime('%Y-%m-%d')
        daily_chats_data = [{"date": today_str, "count": 0}]

    # 7. Top Searched Topics (Category distribution based on analytics logs)
    top_topics = db.session.query(
        FAQ.category,
        func.count(AnalyticsLog.id).label('count')
    ).join(AnalyticsLog, FAQ.id == AnalyticsLog.matched_faq_id)\
     .group_by(FAQ.category)\
     .order_by(func.count(AnalyticsLog.id).desc())\
     .all()
     
    top_topics_data = [{"category": row[0], "count": row[1]} for row in top_topics]

    return {
        "total_faqs": total_faqs,
        "total_queries": total_queries,
        "active_users": active_users,
        "avg_confidence": round(avg_confidence, 2),
        "most_asked": most_asked_data,
        "daily_chats": daily_chats_data,
        "top_topics": top_topics_data
    }
