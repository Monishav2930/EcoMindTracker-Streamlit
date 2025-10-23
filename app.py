import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
import json
import os

from utils.carbon_calculator import CarbonCalculator
from utils.recommender import EcoRecommender
from utils.ml_model import CarbonPredictor
from utils.gamification import GamificationSystem
from utils.database import DatabaseManager
from utils.pdf_generator import PDFReportGenerator
from data.sample_data import generate_sample_data

# Initialize session state for utilities
if 'carbon_calculator' not in st.session_state:
    st.session_state.carbon_calculator = CarbonCalculator()

if 'recommender' not in st.session_state:
    st.session_state.recommender = EcoRecommender()

if 'predictor' not in st.session_state:
    st.session_state.predictor = CarbonPredictor()

if 'gamification' not in st.session_state:
    st.session_state.gamification = GamificationSystem()

if 'db' not in st.session_state:
    try:
        st.session_state.db = DatabaseManager()
    except (ValueError, ConnectionError) as e:
        st.error(f"⚠️ Database Connection Error: {str(e)}")
        st.info("Please ensure your DATABASE_URL environment variable is properly configured.")
        st.stop()

if 'pdf_generator' not in st.session_state:
    st.session_state.pdf_generator = PDFReportGenerator()

# Authentication state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if 'current_user' not in st.session_state:
    st.session_state.current_user = None

if 'user_id' not in st.session_state:
    st.session_state.user_id = None

def login_page():
    """Simple login page"""
    st.set_page_config(
        page_title="EcoMind 🌱 - Login",
        page_icon="🌱",
        layout="centered"
    )
    
    st.markdown('<h1 style="text-align: center; color: #00C851;">EcoMind 🌱</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #FFD700; font-size: 1.2rem;">"Track Smarter. Go Greener."</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.subheader("Welcome to EcoMind")
        st.write("Track your digital carbon footprint and make a difference!")
        
        with st.form("login_form"):
            username = st.text_input("Enter your username", placeholder="eco_warrior")
            email = st.text_input("Email (optional)", placeholder="you@example.com")
            
            submit = st.form_submit_button("Start Tracking", type="primary", use_container_width=True)
            
            if submit:
                if username and len(username) >= 3:
                    # Get or create user
                    user = st.session_state.db.get_user_by_username(username)
                    
                    if user:
                        # Existing user - login
                        st.session_state.current_user = user
                        st.session_state.user_id = user['id']
                        st.session_state.authenticated = True
                        st.success(f"Welcome back, {username}! 🌱")
                        st.rerun()
                    else:
                        # New user - create account
                        user_id = st.session_state.db.create_user(username, email if email else None)
                        user = st.session_state.db.get_user_by_id(user_id)
                        st.session_state.current_user = user
                        st.session_state.user_id = user_id
                        st.session_state.authenticated = True
                        st.success(f"Account created! Welcome, {username}! 🌱")
                        st.rerun()
                else:
                    st.error("Username must be at least 3 characters long")

def check_and_award_badges(user_id: int):
    """Check and award badges based on user activity"""
    logs = st.session_state.db.get_user_activity_logs(user_id)
    
    if not logs:
        return []
    
    newly_earned = []
    current_badges = st.session_state.db.get_user_badges(user_id)
    
    df = pd.DataFrame(logs)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    
    # Check First Steps badge
    if 'First Steps' not in current_badges and len(logs) >= 1:
        if st.session_state.db.award_badge(user_id, 'First Steps'):
            newly_earned.append('First Steps')
    
    # Check Week Warrior badge (7 days tracked)
    if 'Week Warrior' not in current_badges and len(logs) >= 7:
        if st.session_state.db.award_badge(user_id, 'Week Warrior'):
            newly_earned.append('Week Warrior')
    
    # Check Consistency King badge (30 days)
    if 'Consistency King' not in current_badges and len(logs) >= 30:
        if st.session_state.db.award_badge(user_id, 'Consistency King'):
            newly_earned.append('Consistency King')
    
    # Check emission-based badges
    if len(logs) >= 3:
        recent_emissions = df['co2_grams'].tail(7).mean()
        
        emission_badges = [
            ('Eco Novice', 2000),
            ('Green Guardian', 1500),
            ('Carbon Crusher', 1000),
            ('Eco Champion', 500)
        ]
        
        for badge_name, threshold in emission_badges:
            if badge_name not in current_badges and recent_emissions < threshold:
                if st.session_state.db.award_badge(user_id, badge_name):
                    newly_earned.append(badge_name)
    
    # Check Improvement Master badge (50% reduction)
    if 'Improvement Master' not in current_badges and len(logs) >= 14:
        first_week_avg = df['co2_grams'].head(7).mean()
        last_week_avg = df['co2_grams'].tail(7).mean()
        
        if first_week_avg > 0 and (first_week_avg - last_week_avg) / first_week_avg >= 0.5:
            if st.session_state.db.award_badge(user_id, 'Improvement Master'):
                newly_earned.append('Improvement Master')
    
    return newly_earned

def main():
    st.set_page_config(
        page_title="EcoMind 🌱",
        page_icon="🌱",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for dark theme with eco colors
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        color: #00C851;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .tagline {
        text-align: center;
        color: #FFD700;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .metric-container {
        background-color: #21262D;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #00C851;
    }
    .eco-score {
        font-size: 2.5rem;
        font-weight: bold;
        color: #00C851;
    }
    .badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        margin: 0.25rem;
        border-radius: 20px;
        font-weight: bold;
    }
    .badge-bronze { background-color: #CD7F32; color: white; }
    .badge-silver { background-color: #C0C0C0; color: black; }
    .badge-gold { background-color: #FFD700; color: black; }
    .badge-platinum { background-color: #E5E4E2; color: black; }
    .badge-diamond { background-color: #B9F2FF; color: black; }
    </style>
    """, unsafe_allow_html=True)
    
    # Sidebar with user info and logout
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.current_user['username']}")
        st.markdown(f"**Level:** {st.session_state.current_user['current_level']}")
        st.markdown(f"**Score:** {st.session_state.current_user['total_score']}")
        
        # Get user stats
        stats = st.session_state.db.get_user_stats(st.session_state.user_id)
        st.markdown(f"**Days Tracked:** {stats['total_days']}")
        
        st.markdown("---")
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.current_user = None
            st.session_state.user_id = None
            st.rerun()
    
    # Header
    st.markdown('<h1 class="main-header">EcoMind 🌱</h1>', unsafe_allow_html=True)
    st.markdown('<p class="tagline">"Track Smarter. Go Greener."</p>', unsafe_allow_html=True)
    
    # Navigation tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📊 Dashboard", "🔮 Predictions", "💡 Recommendations", "📈 Analytics", "🌍 Community", "👤 Profile"])
    
    with tab1:
        dashboard_tab()
    
    with tab2:
        predictions_tab()
    
    with tab3:
        recommendations_tab()
    
    with tab4:
        analytics_tab()
    
    with tab5:
        community_tab()
    
    with tab6:
        profile_tab()

def dashboard_tab():
    st.header("Digital Carbon Footprint Dashboard")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.subheader("Track Your Digital Activities")
        
        # Activity input form
        with st.form("activity_form"):
            st.write("**Enter today's digital activities:**")
            
            col_a, col_b = st.columns(2)
            with col_a:
                emails_sent = st.number_input("Emails sent", min_value=0, value=20)
                video_calls_hours = st.number_input("Video calls (hours)", min_value=0.0, value=2.0, step=0.5)
            
            with col_b:
                streaming_hours = st.number_input("Streaming (hours)", min_value=0.0, value=3.0, step=0.5)
                cloud_storage_gb = st.number_input("Cloud storage used (GB)", min_value=0.0, value=5.0, step=0.1)
            
            device_hours = st.number_input("Total device usage (hours)", min_value=0.0, value=8.0, step=0.5)
            
            submitted = st.form_submit_button("Calculate Carbon Footprint", type="primary")
            
            if submitted:
                # Calculate carbon footprint
                daily_co2 = st.session_state.carbon_calculator.calculate_daily_footprint(
                    emails_sent, video_calls_hours, streaming_hours, cloud_storage_gb, device_hours
                )
                
                # Save to database
                today = date.today()
                st.session_state.db.add_activity_log(
                    st.session_state.user_id,
                    today,
                    emails_sent,
                    video_calls_hours,
                    streaming_hours,
                    cloud_storage_gb,
                    device_hours,
                    daily_co2
                )
                
                # Update gamification score
                daily_points = st.session_state.gamification.calculate_daily_score(daily_co2)
                st.session_state.gamification.user_score = st.session_state.current_user['total_score'] + daily_points
                new_level = st.session_state.gamification.get_current_level()
                
                # Update user in database
                st.session_state.db.update_user_score(
                    st.session_state.user_id,
                    st.session_state.gamification.user_score,
                    new_level
                )
                
                # Check and award badges
                new_badges = check_and_award_badges(st.session_state.user_id)
                
                # Refresh current user data
                st.session_state.current_user = st.session_state.db.get_user_by_id(st.session_state.user_id)
                
                st.success(f"✅ Today's carbon footprint: **{daily_co2:.2f}g CO₂** (+{daily_points} points)")
                
                if new_badges:
                    st.balloons()
                    st.success(f"🏆 New badge(s) earned: {', '.join(new_badges)}!")
                
                st.rerun()
    
    # Get user's activity logs
    user_logs = st.session_state.db.get_user_activity_logs(st.session_state.user_id)
    
    with col2:
        # Digital Green Score
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.subheader("🌱 Digital Green Score")
        
        if user_logs:
            recent_logs = user_logs[:7]  # Last 7 days
            avg_daily_co2 = np.mean([log['co2_grams'] for log in recent_logs])
            green_score = max(0, 100 - (avg_daily_co2 / 50))
        else:
            green_score = 50
            avg_daily_co2 = 0
        
        st.markdown(f'<div class="eco-score">{green_score:.0f}/100</div>', unsafe_allow_html=True)
        
        # Progress bar for green score
        st.progress(green_score / 100)
        
        if green_score >= 80:
            st.success("🏆 Excellent! You're an eco-champion!")
        elif green_score >= 60:
            st.info("👍 Good job! Room for improvement.")
        else:
            st.warning("⚠️ Let's work on reducing your footprint!")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        # Current level and badges
        st.subheader("🎖️ Your Level")
        st.write(f"**Level:** {st.session_state.current_user['current_level']}")
        
        badges = st.session_state.db.get_user_badges(st.session_state.user_id)
        if badges:
            st.write("**Badges Earned:**")
            for badge in badges[:3]:  # Show first 3
                badge_class = f"badge-{badge.lower().replace(' ', '-')}"
                st.markdown(f'<span class="badge {badge_class}">{badge}</span>', unsafe_allow_html=True)
            if len(badges) > 3:
                st.write(f"+ {len(badges) - 3} more")
    
    # Visualizations
    if user_logs:
        st.subheader("📈 Carbon Footprint Trends")
        
        df = pd.DataFrame(user_logs)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Daily CO2 trend
            fig_trend = px.line(
                df, x='date', y='co2_grams',
                title='Daily CO₂ Emissions Trend',
                labels={'co2_grams': 'CO₂ (grams)', 'date': 'Date'}
            )
            fig_trend.update_traces(line_color='#00C851')
            st.plotly_chart(fig_trend, use_container_width=True)
        
        with col2:
            # Activity breakdown
            if len(df) > 0:
                latest_log = df.iloc[-1]
                activities = {
                    'Emails': latest_log['emails'] * 4,
                    'Video Calls': latest_log['video_calls'] * 150,
                    'Streaming': latest_log['streaming'] * 36,
                    'Cloud Storage': latest_log['cloud_storage'] * 10,
                    'Device Usage': latest_log['device_usage'] * 20
                }
                
                fig_pie = px.pie(
                    values=list(activities.values()),
                    names=list(activities.keys()),
                    title="Today's CO₂ by Activity"
                )
                st.plotly_chart(fig_pie, use_container_width=True)
        
        # Weekly comparison
        st.subheader("📊 Weekly Comparison")
        if len(df) >= 7:
            df['week'] = df['date'].dt.isocalendar().week
            weekly_avg = df.groupby('week')['co2_grams'].mean().reset_index()
            weekly_avg['week_label'] = 'Week ' + weekly_avg['week'].astype(str)
            
            fig_weekly = px.bar(
                weekly_avg, x='week_label', y='co2_grams',
                title='Weekly Average CO₂ Emissions',
                labels={'co2_grams': 'Average CO₂ (grams)', 'week_label': 'Week'}
            )
            fig_weekly.update_traces(marker_color='#00C851')
            st.plotly_chart(fig_weekly, use_container_width=True)
    else:
        st.info("👆 Start tracking your activities to see visualizations!")

def predictions_tab():
    st.header("🔮 AI Carbon Footprint Predictions")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Predict Future Emissions")
        
        with st.form("prediction_form"):
            st.write("**Enter your planned activities:**")
            
            pred_emails = st.number_input("Planned emails to send", min_value=0, value=25)
            pred_video_calls = st.number_input("Planned video call hours", min_value=0.0, value=2.5, step=0.5)
            pred_streaming = st.number_input("Planned streaming hours", min_value=0.0, value=3.5, step=0.5)
            pred_cloud = st.number_input("Expected cloud storage (GB)", min_value=0.0, value=6.0, step=0.1)
            pred_device = st.number_input("Expected device usage (hours)", min_value=0.0, value=9.0, step=0.5)
            
            prediction_days = st.selectbox("Prediction period", [1, 7, 30], index=1)
            
            predict_btn = st.form_submit_button("🔮 Predict Carbon Footprint", type="primary")
            
            if predict_btn:
                # Use ML model for prediction
                predicted_co2 = st.session_state.predictor.predict_emissions(
                    pred_emails, pred_video_calls, pred_streaming, pred_cloud, pred_device, prediction_days
                )
                
                st.success(f"🔮 **Predicted CO₂ for next {prediction_days} day(s): {predicted_co2:.2f}g**")
                
                # Show comparison with current average
                user_logs = st.session_state.db.get_user_activity_logs(st.session_state.user_id, limit=7)
                if user_logs:
                    current_avg = np.mean([log['co2_grams'] for log in user_logs])
                    daily_predicted = predicted_co2 / prediction_days
                    
                    if daily_predicted < current_avg:
                        st.success(f"📉 Great! That's {current_avg - daily_predicted:.2f}g less than your current daily average!")
                    else:
                        st.warning(f"📈 That's {daily_predicted - current_avg:.2f}g more than your current daily average. Consider the recommendations!")
    
    with col2:
        st.subheader("🎯 Optimization Scenarios")
        
        user_logs = st.session_state.db.get_user_activity_logs(st.session_state.user_id, limit=1)
        if user_logs:
            base_data = user_logs[0]
            
            scenarios = {
                "Current": st.session_state.carbon_calculator.calculate_daily_footprint(
                    base_data['emails'], base_data['video_calls'], base_data['streaming'], 
                    base_data['cloud_storage'], base_data['device_usage']
                ),
                "Eco Mode": st.session_state.carbon_calculator.calculate_daily_footprint(
                    base_data['emails'] * 0.7, base_data['video_calls'] * 0.8, base_data['streaming'] * 0.6, 
                    base_data['cloud_storage'] * 0.9, base_data['device_usage'] * 0.8
                ),
                "Green Champion": st.session_state.carbon_calculator.calculate_daily_footprint(
                    base_data['emails'] * 0.5, base_data['video_calls'] * 0.6, base_data['streaming'] * 0.4, 
                    base_data['cloud_storage'] * 0.7, base_data['device_usage'] * 0.6
                )
            }
            
            fig_scenarios = px.bar(
                x=list(scenarios.keys()),
                y=list(scenarios.values()),
                title="Optimization Scenarios",
                labels={'x': 'Scenario', 'y': 'CO₂ (grams)'},
                color=list(scenarios.values()),
                color_continuous_scale='RdYlGn_r'
            )
            st.plotly_chart(fig_scenarios, use_container_width=True)
            
            # Savings calculation
            current_co2 = scenarios["Current"]
            eco_savings = current_co2 - scenarios["Eco Mode"]
            champion_savings = current_co2 - scenarios["Green Champion"]
            
            st.metric("🌱 Eco Mode Savings", f"{eco_savings:.2f}g CO₂", f"{(eco_savings/current_co2*100):.1f}%")
            st.metric("🏆 Green Champion Savings", f"{champion_savings:.2f}g CO₂", f"{(champion_savings/current_co2*100):.1f}%")
        else:
            st.info("Track some activities first to see optimization scenarios!")

def recommendations_tab():
    st.header("💡 Personalized Eco Recommendations")
    
    # Get personalized recommendations
    user_logs = st.session_state.db.get_user_activity_logs(st.session_state.user_id, limit=1)
    if user_logs:
        latest_log = user_logs[0]
        recommendations = st.session_state.recommender.get_recommendations(latest_log)
    else:
        recommendations = st.session_state.recommender.get_general_recommendations()
    
    st.subheader("🌟 Your Daily Eco Tips")
    
    for i, rec in enumerate(recommendations[:3], 1):
        with st.expander(f"💡 Tip {i}: {rec['title']}", expanded=i==1):
            st.write(rec['description'])
            st.info(f"💚 **Potential CO₂ savings:** {rec['co2_savings']}g per day")
            
            # Action button
            if st.button(f"✅ Mark as Done", key=f"tip_{i}"):
                st.success("Great job! Keep up the eco-friendly habits! 🌱")
    
    st.subheader("🔧 Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📧 Schedule Email Batch", type="secondary"):
            st.info("💡 Batching emails can reduce server requests by up to 30%!")
    
    with col2:
        if st.button("🎥 Lower Video Quality", type="secondary"):
            st.info("💡 Reducing video quality from HD to SD saves ~50% bandwidth!")
    
    with col3:
        if st.button("☁️ Clean Cloud Storage", type="secondary"):
            st.info("💡 Regular cleanup can reduce storage emissions by 20%!")
    
    # Voice Assistant / Reminders Section
    st.subheader("🔔 Eco Reminders & Voice Assistant")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write("**Set up daily reminders to improve your eco-habits:**")
        
        # Reminder options
        reminder_options = [
            "🕐 Morning: Review yesterday's footprint",
            "🕒 Midday: Close unused browser tabs",
            "🕕 Afternoon: Batch your emails",
            "🕘 Evening: Track today's activities",
            "🌙 Night: Enable power saving mode"
        ]
        
        selected_reminders = st.multiselect(
            "Choose your reminder schedule:",
            reminder_options,
            default=[reminder_options[0], reminder_options[3]]
        )
        
        if selected_reminders:
            st.success(f"✅ You have {len(selected_reminders)} active reminders")
            
            # Voice message button
            if st.button("🔊 Play Sample Eco Reminder", use_container_width=True):
                st.audio("data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBTOJ0fPTgjMGHm7A7eGVSg0PVqzn77BdGAg+ltryxnMpBSuAy/DbizYHGGS57OihUBELTKXh8bllHAU2jdXzzn0vBSh+zPLaizsIHm/A7eCVSg0PVqzn77BdGAg+ltryxnMpBSuAy/DbizYHGGS57OihUBELTKXh8bllHAU2jdXzzn0vBSh+zPLaizsIHm/A7eCVSg0PVqzn77BdGAg+ltryxnMpBSuAy/DbizYHGGS57OihUBELTKXh8bllHAU2jdXzzn0vBSh+zPLaizsIHm/A7eCVSg0PVqzn77BdGAg+ltryxnMpBSuAy/DbizYHGGS57OihUBELTKXh8bllHAU2jdXzzn0vBSh+zPLaizsIHm/A7eCVSg0PVqzn77BdGAg+ltryxnMpBSuAy/DbizYHGGS57OihUBELTKXh8bllHAU2jdXzzn0vBSh+zPLaizsIHm/A7eCVSg0PVqzn77BdGAg+ltryxnMpBSuAy/DbizYHGGS57OihUBELTKXh8bllHAU2jdXzzn0vBSh+zPLaizsIHm/A7eCVSg0PVqzn77BdGAg+ltryxnMpBSuAy/DbizYHGGS57OihUBELTKXh8bllHAU2jdXzzn0vBSh+zPLaizsI=", format="audio/wav")
                st.info("🌱 EcoMind says: Remember to track your daily activities and close unused browser tabs!")
        else:
            st.info("Select reminders to help you build eco-friendly habits")
    
    with col2:
        st.write("**Quick Voice Tips:**")
        
        tips_list = [
            "💡 Turn off video in calls",
            "💡 Lower streaming quality",
            "💡 Delete old cloud files",
            "💡 Use dark mode",
            "💡 Close idle tabs"
        ]
        
        for tip in tips_list:
            st.write(tip)
        
        if st.button("🎙️ Get Voice Tip", use_container_width=True):
            import random
            tip = random.choice(tips_list)
            st.success(f"🔊 {tip}")
    
    st.markdown("---")
    
    # Educational content
    st.subheader("📚 Learn More About Digital Carbon Footprint")
    
    with st.expander("🌍 Did you know?"):
        st.write("""
        - **Digital Carbon Facts:**
          - The internet accounts for 4% of global CO₂ emissions
          - Streaming 1 hour of video produces ~36g of CO₂
          - Sending 1 email produces ~4g of CO₂
          - Cloud storage produces ~10g of CO₂ per GB per day
          - Video calls produce ~150g of CO₂ per hour
        """)
    
    with st.expander("🎯 Best Practices"):
        st.write("""
        - **Reduce Streaming Impact:**
          - Choose lower video quality when possible
          - Download content for offline viewing
          - Use audio-only for background content
        
        - **Email Efficiency:**
          - Batch emails instead of sending individually
          - Unsubscribe from unused newsletters
          - Use text instead of images when possible
        
        - **Cloud Optimization:**
          - Regular cleanup of unused files
          - Use efficient file formats
          - Enable automatic compression
        """)

def community_tab():
    st.header("🌍 EcoMind Community")
    
    st.write("Connect with eco-conscious users worldwide and compete in carbon reduction challenges!")
    
    # Leaderboard Section
    st.subheader("🏆 Global Leaderboard")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Get leaderboard data
        leaderboard = st.session_state.db.get_leaderboard(limit=20)
        
        if leaderboard:
            # Find current user's rank
            user_rank = None
            for idx, entry in enumerate(leaderboard, 1):
                if entry['username'] == st.session_state.current_user['username']:
                    user_rank = idx
                    break
            
            # Create leaderboard dataframe
            leaderboard_data = []
            for idx, entry in enumerate(leaderboard[:10], 1):  # Top 10
                is_current_user = entry['username'] == st.session_state.current_user['username']
                
                # Medal emojis for top 3
                medal = ""
                if idx == 1:
                    medal = "🥇"
                elif idx == 2:
                    medal = "🥈"
                elif idx == 3:
                    medal = "🥉"
                
                username_display = f"**{entry['username']}**" if is_current_user else entry['username']
                
                leaderboard_data.append({
                    'Rank': f"{medal} {idx}" if medal else str(idx),
                    'User': username_display,
                    'Level': entry['current_level'],
                    'Score': entry['total_score'],
                    'Days': entry['days_tracked'],
                    'Avg CO₂': f"{entry['avg_co2']:.0f}g" if entry['avg_co2'] else "N/A"
                })
            
            df_leaderboard = pd.DataFrame(leaderboard_data)
            st.dataframe(df_leaderboard, use_container_width=True, hide_index=True)
            
            if user_rank:
                if user_rank <= 10:
                    st.success(f"🎉 You're ranked #{user_rank} on the global leaderboard!")
                else:
                    st.info(f"📊 Your current rank: #{user_rank}")
            else:
                st.info("Start tracking to appear on the leaderboard!")
        else:
            st.info("Be the first to join the leaderboard! Start tracking your activities.")
    
    with col2:
        st.write("**Your Community Stats:**")
        
        user_stats = st.session_state.db.get_user_stats(st.session_state.user_id)
        
        if user_stats['total_days'] > 0:
            st.metric("Your Score", st.session_state.current_user['total_score'])
            st.metric("Your Level", st.session_state.current_user['current_level'])
            st.metric("Days Active", user_stats['total_days'])
            
            # Global comparison
            global_avg = 2500
            user_avg = user_stats['avg_daily_co2']
            if user_avg < global_avg:
                improvement = ((global_avg - user_avg) / global_avg * 100)
                st.success(f"✨ {improvement:.0f}% better than global average!")
            else:
                st.info("Keep tracking to improve your rank!")
        else:
            st.info("Track activities to see your stats!")
    
    st.markdown("---")
    
    # Eco Challenges Section
    st.subheader("🎯 Eco Challenges")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Active Challenges:**")
        
        challenges = [
            {
                'name': '7-Day Streak',
                'description': 'Track your footprint for 7 consecutive days',
                'reward': '100 points',
                'icon': '🔥'
            },
            {
                'name': 'Carbon Crusher',
                'description': 'Reduce daily emissions below 1000g for a week',
                'reward': '200 points',
                'icon': '💚'
            },
            {
                'name': 'Email Optimizer',
                'description': 'Send 50% fewer emails than your average',
                'reward': '50 points',
                'icon': '📧'
            },
            {
                'name': 'Streaming Reducer',
                'description': 'Cut streaming time by 30% this week',
                'reward': '75 points',
                'icon': '📺'
            }
        ]
        
        for challenge in challenges:
            with st.expander(f"{challenge['icon']} {challenge['name']}"):
                st.write(f"**Goal:** {challenge['description']}")
                st.info(f"**Reward:** {challenge['reward']}")
                if st.button(f"Join Challenge", key=f"challenge_{challenge['name']}", use_container_width=True):
                    st.success(f"✅ Joined: {challenge['name']}!")
    
    with col2:
        st.write("**Monthly Challenge:**")
        
        st.markdown("""
        <div style="background-color: #1E3A1E; padding: 20px; border-radius: 10px; border-left: 4px solid #00C851;">
            <h3 style="color: #FFD700; margin-top: 0;">🏅 October Green Challenge</h3>
            <p style="color: white;"><strong>Goal:</strong> Reduce your average daily emissions by 25% compared to last month</p>
            <p style="color: #00C851;"><strong>Prize:</strong> 500 bonus points + Platinum badge</p>
            <p style="color: lightgray;"><strong>Time Remaining:</strong> 8 days</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("")
        
        # Challenge progress
        user_logs = st.session_state.db.get_user_activity_logs(st.session_state.user_id)
        if user_logs and len(user_logs) >= 7:
            recent_avg = np.mean([log['co2_grams'] for log in user_logs[:7]])
            st.write("**Your Progress:**")
            st.metric("Recent Avg CO₂", f"{recent_avg:.0f}g/day")
            st.progress(min(100, (2500 - recent_avg) / 2500 * 100) / 100)
        else:
            st.info("Track more days to see your progress!")
    
    st.markdown("---")
    
    # Social Sharing Section
    st.subheader("📤 Share Your Progress")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🐦 Share to Twitter", use_container_width=True):
            user_stats = st.session_state.db.get_user_stats(st.session_state.user_id)
            if user_stats['total_days'] > 0:
                share_text = f"I'm tracking my digital carbon footprint with EcoMind! 🌱 {user_stats['total_days']} days tracked, {user_stats['avg_daily_co2']:.0f}g CO₂ average. Join me in going greener! #EcoMind #DigitalCarbon"
                st.code(share_text, language=None)
                st.success("Copy this text to share on Twitter!")
            else:
                st.info("Track some activities first to share your progress!")
    
    with col2:
        if st.button("📘 Share to Facebook", use_container_width=True):
            st.info("🌱 Share your eco-journey with friends on Facebook!")
            st.write("Tell them about EcoMind and inspire others to track their digital footprint!")
    
    with col3:
        if st.button("🔗 Get Shareable Link", use_container_width=True):
            st.code(f"https://ecomind.app/profile/{st.session_state.current_user['username']}", language=None)
            st.success("Share this link with friends!")
    
    # Friends Comparison (Future feature preview)
    st.markdown("---")
    st.subheader("👥 Compare with Friends")
    st.info("🚧 Coming Soon: Invite friends and compare your eco-scores side by side!")

def analytics_tab():
    st.header("📈 Advanced Analytics Dashboard")
    
    # Get user's activity logs
    all_logs = st.session_state.db.get_user_activity_logs(st.session_state.user_id)
    
    if not all_logs:
        st.info("📊 Start tracking activities to see analytics!")
        return
    
    # Date range filter
    st.subheader("📅 Filter Data by Date Range")
    
    df_all = pd.DataFrame(all_logs)
    df_all['date'] = pd.to_datetime(df_all['date'])
    df_all = df_all.sort_values('date')
    
    min_date = df_all['date'].min().date()
    max_date = df_all['date'].max().date()
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=min_date,
            min_value=min_date,
            max_value=max_date
        )
    
    with col2:
        end_date = st.date_input(
            "End Date",
            value=max_date,
            min_value=min_date,
            max_value=max_date
        )
    
    with col3:
        st.write("")
        st.write("")
        if st.button("🔄 Reset Filters", use_container_width=True):
            st.rerun()
    
    # Filter data by date range
    filtered_logs = st.session_state.db.get_activity_logs_by_date_range(
        st.session_state.user_id,
        start_date,
        end_date
    )
    
    if not filtered_logs:
        st.warning("No data found for selected date range.")
        return
    
    df = pd.DataFrame(filtered_logs)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    
    # Summary statistics for filtered data
    st.subheader("📊 Summary Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_days = len(df)
    total_co2 = df['co2_grams'].sum()
    avg_co2 = df['co2_grams'].mean()
    trend = ((df['co2_grams'].tail(3).mean() - df['co2_grams'].head(3).mean()) / df['co2_grams'].head(3).mean() * 100) if len(df) >= 6 else 0
    
    with col1:
        st.metric("📅 Days in Range", total_days)
    
    with col2:
        st.metric("🌍 Total CO₂", f"{total_co2:.0f}g")
    
    with col3:
        st.metric("📊 Daily Average", f"{avg_co2:.1f}g")
    
    with col4:
        st.metric("📈 Trend", f"{abs(trend):.1f}%", 
                 delta=f"{'Decreasing' if trend < 0 else 'Increasing'}" if trend != 0 else "Stable",
                 delta_color="normal" if trend < 0 else "inverse")
    
    # Detailed activity breakdown
    st.subheader("🔍 Activity Breakdown")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Calculate total CO2 by activity type
        activity_totals = {
            'Emails': df['emails'].sum() * 4,
            'Video Calls': df['video_calls'].sum() * 150,
            'Streaming': df['streaming'].sum() * 36,
            'Cloud Storage': df['cloud_storage'].sum() * 10,
            'Device Usage': df['device_usage'].sum() * 20
        }
        
        fig_breakdown = px.pie(
            values=list(activity_totals.values()),
            names=list(activity_totals.keys()),
            title="Total CO₂ by Activity Type",
            color_discrete_sequence=px.colors.sequential.Greens_r
        )
        st.plotly_chart(fig_breakdown, use_container_width=True)
    
    with col2:
        # Average daily activity
        activity_averages = {
            'Emails': df['emails'].mean(),
            'Video Calls': df['video_calls'].mean(),
            'Streaming': df['streaming'].mean(),
            'Cloud Storage': df['cloud_storage'].mean(),
            'Device Usage': df['device_usage'].mean()
        }
        
        fig_avg = px.bar(
            x=list(activity_averages.keys()),
            y=list(activity_averages.values()),
            title="Average Daily Usage",
            labels={'x': 'Activity', 'y': 'Average'},
            color=list(activity_averages.values()),
            color_continuous_scale='Greens'
        )
        st.plotly_chart(fig_avg, use_container_width=True)
    
    # Trends over time
    st.subheader("📈 Trends Over Time")
    
    # Multi-line chart showing all activities
    fig_trends = go.Figure()
    
    fig_trends.add_trace(go.Scatter(
        x=df['date'], y=df['emails'],
        mode='lines',
        name='Emails',
        line=dict(color='#FF6B6B')
    ))
    
    fig_trends.add_trace(go.Scatter(
        x=df['date'], y=df['video_calls'],
        mode='lines',
        name='Video Calls (hrs)',
        line=dict(color='#4ECDC4')
    ))
    
    fig_trends.add_trace(go.Scatter(
        x=df['date'], y=df['streaming'],
        mode='lines',
        name='Streaming (hrs)',
        line=dict(color='#FFD93D')
    ))
    
    fig_trends.add_trace(go.Scatter(
        x=df['date'], y=df['cloud_storage'],
        mode='lines',
        name='Cloud Storage (GB)',
        line=dict(color='#A8DADC')
    ))
    
    fig_trends.add_trace(go.Scatter(
        x=df['date'], y=df['device_usage'],
        mode='lines',
        name='Device Usage (hrs)',
        line=dict(color='#B4A7D6')
    ))
    
    fig_trends.update_layout(
        title="Activity Trends Over Time",
        xaxis_title="Date",
        yaxis_title="Usage",
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_trends, use_container_width=True)
    
    # CO2 emissions heatmap (by day of week)
    st.subheader("🗓️ Emissions by Day of Week")
    
    df['day_of_week'] = df['date'].dt.day_name()
    df['week_num'] = df['date'].dt.isocalendar().week
    
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    daily_avg = df.groupby('day_of_week')['co2_grams'].mean().reindex(day_order)
    
    fig_days = px.bar(
        x=daily_avg.index,
        y=daily_avg.values,
        title="Average CO₂ Emissions by Day of Week",
        labels={'x': 'Day', 'y': 'Average CO₂ (grams)'},
        color=daily_avg.values,
        color_continuous_scale='RdYlGn_r'
    )
    st.plotly_chart(fig_days, use_container_width=True)
    
    # Detailed data table
    st.subheader("📋 Detailed Data Table")
    
    # Prepare display dataframe
    display_df = df[['date', 'emails', 'video_calls', 'streaming', 'cloud_storage', 'device_usage', 'co2_grams']].copy()
    display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
    display_df = display_df.rename(columns={
        'date': 'Date',
        'emails': 'Emails',
        'video_calls': 'Video Calls (hrs)',
        'streaming': 'Streaming (hrs)',
        'cloud_storage': 'Cloud Storage (GB)',
        'device_usage': 'Device Usage (hrs)',
        'co2_grams': 'CO₂ (grams)'
    })
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # Export options
    st.subheader("📤 Export Analytics Data")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        csv_data = display_df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name=f"ecomind_analytics_{start_date}_{end_date}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        # PDF Report
        pdf_bytes = st.session_state.pdf_generator.generate_analytics_report(
            st.session_state.current_user['username'],
            filtered_logs,
            start_date,
            end_date
        )
        st.download_button(
            label="📕 Download PDF Report",
            data=pdf_bytes,
            file_name=f"ecomind_analytics_{start_date}_{end_date}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    
    with col3:
        # Summary report
        summary_report = f"""EcoMind Analytics Report
Period: {start_date} to {end_date}

Summary Statistics:
- Total Days: {total_days}
- Total CO₂: {total_co2:.2f}g
- Daily Average: {avg_co2:.2f}g
- Best Day: {df['co2_grams'].min():.2f}g
- Worst Day: {df['co2_grams'].max():.2f}g

Activity Breakdown:
- Emails: {df['emails'].sum()} total, {df['emails'].mean():.1f} avg/day
- Video Calls: {df['video_calls'].sum():.1f}hrs total, {df['video_calls'].mean():.1f}hrs avg/day
- Streaming: {df['streaming'].sum():.1f}hrs total, {df['streaming'].mean():.1f}hrs avg/day
- Cloud Storage: {df['cloud_storage'].mean():.1f}GB avg
- Device Usage: {df['device_usage'].sum():.1f}hrs total, {df['device_usage'].mean():.1f}hrs avg/day
"""
        st.download_button(
            label="📄 Download Summary",
            data=summary_report,
            file_name=f"ecomind_report_{start_date}_{end_date}.txt",
            mime="text/plain",
            use_container_width=True
        )

def profile_tab():
    st.header("👤 Your EcoMind Profile")
    
    col1, col2 = st.columns([1, 1])
    
    # Get user data
    user_logs = st.session_state.db.get_user_activity_logs(st.session_state.user_id)
    stats = st.session_state.db.get_user_stats(st.session_state.user_id)
    
    with col1:
        st.subheader("📊 Statistics")
        
        if user_logs:
            st.metric("🗓️ Days Tracked", stats['total_days'])
            st.metric("🌍 Total CO₂ Tracked", f"{stats['total_co2']:.2f}g")
            st.metric("📈 Daily Average", f"{stats['avg_daily_co2']:.2f}g")
            st.metric("🏆 Best Day", f"{stats['best_day_co2']:.2f}g")
            
            # Carbon footprint over time
            df = pd.DataFrame(user_logs)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            fig_profile = px.line(
                df, x='date', y='co2_grams',
                title='Your Carbon Journey',
                labels={'co2_grams': 'Daily CO₂ (grams)', 'date': 'Date'}
            )
            fig_profile.update_traces(line_color='#00C851')
            st.plotly_chart(fig_profile, use_container_width=True)
        else:
            st.info("Start tracking your activities to see your statistics!")
    
    with col2:
        st.subheader("🎖️ Achievements")
        
        # Current level and progress
        st.session_state.gamification.user_score = st.session_state.current_user['total_score']
        current_level = st.session_state.gamification.get_current_level()
        progress = st.session_state.gamification.get_level_progress()
        
        st.write(f"**Current Level:** {current_level}")
        st.progress(progress / 100)
        st.write(f"Progress to next level: {progress:.1f}%")
        
        # Badges display
        st.write("**🏆 Badges Earned:**")
        badges = st.session_state.db.get_user_badges(st.session_state.user_id)
        
        if badges:
            # Display badges in a grid
            for badge in badges:
                badge_info = st.session_state.gamification.get_badge_info(badge)
                if badge_info:
                    st.markdown(f"**{badge_info.get('icon', '🏅')} {badge}**")
                    st.caption(badge_info.get('description', ''))
        else:
            st.info("Keep tracking to earn your first badge! 🌱")
        
        # Global comparison
        st.subheader("🌍 Global Impact")
        if user_logs:
            user_avg = stats['avg_daily_co2']
            global_avg = 2500  # Average global daily digital carbon footprint
            
            comparison = (global_avg - user_avg) / global_avg * 100
            
            if comparison > 0:
                st.success(f"🌟 You're {comparison:.1f}% below the global average!")
            else:
                st.info(f"📈 You're {abs(comparison):.1f}% above global average. Let's improve!")
            
            # Visual comparison
            fig_comparison = go.Figure()
            fig_comparison.add_trace(go.Bar(
                name='You',
                x=['Daily Average'],
                y=[user_avg],
                marker_color='#00C851'
            ))
            fig_comparison.add_trace(go.Bar(
                name='Global Average',
                x=['Daily Average'],
                y=[global_avg],
                marker_color='#FF6B6B'
            ))
            fig_comparison.update_layout(title='You vs Global Average')
            st.plotly_chart(fig_comparison, use_container_width=True)
    
    # Data management
    st.subheader("⚙️ Data Management & Export")
    
    if user_logs:
        st.write("**Export Your Data:**")
        col1, col2 = st.columns(2)
        
        with col1:
            # CSV Export
            df = pd.DataFrame(user_logs)
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV Data",
                data=csv,
                file_name=f"ecomind_data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            # PDF Report Export
            pdf_bytes = st.session_state.pdf_generator.generate_user_report(
                st.session_state.current_user['username'],
                st.session_state.current_user['current_level'],
                st.session_state.current_user['total_score'],
                stats,
                badges,
                user_logs
            )
            st.download_button(
                label="📕 Download PDF Report",
                data=pdf_bytes,
                file_name=f"ecomind_profile_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        
        st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Member Since:**")
        joined_date = st.session_state.current_user['joined_date']
        st.write(joined_date.strftime('%Y-%m-%d') if hasattr(joined_date, 'strftime') else str(joined_date))
    
    with col2:
        if st.button("🔄 Reset All Data", type="secondary", use_container_width=True):
            st.warning("⚠️ This will delete all your activity logs and reset your progress!")
            if st.button("⚠️ Confirm Reset", type="primary", key="confirm_reset"):
                st.session_state.db.delete_user_data(st.session_state.user_id)
                st.session_state.current_user = st.session_state.db.get_user_by_id(st.session_state.user_id)
                st.success("Data reset successfully!")
                st.rerun()

if __name__ == "__main__":
    # Check authentication
    if not st.session_state.authenticated:
        login_page()
    else:
        main()
