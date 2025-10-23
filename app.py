import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os

from utils.carbon_calculator import CarbonCalculator
from utils.recommender import EcoRecommender
from utils.ml_model import CarbonPredictor
from utils.gamification import GamificationSystem
from data.sample_data import generate_sample_data

# Initialize session state
if 'user_data' not in st.session_state:
    st.session_state.user_data = {
        'daily_logs': [],
        'total_score': 0,
        'badges': [],
        'level': 'Bronze',
        'joined_date': datetime.now().strftime("%Y-%m-%d")
    }

if 'carbon_calculator' not in st.session_state:
    st.session_state.carbon_calculator = CarbonCalculator()

if 'recommender' not in st.session_state:
    st.session_state.recommender = EcoRecommender()

if 'predictor' not in st.session_state:
    st.session_state.predictor = CarbonPredictor()

if 'gamification' not in st.session_state:
    st.session_state.gamification = GamificationSystem()

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
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="main-header">EcoMind 🌱</h1>', unsafe_allow_html=True)
    st.markdown('<p class="tagline">"Track Smarter. Go Greener."</p>', unsafe_allow_html=True)
    
    # Navigation tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "🔮 Predictions", "💡 Recommendations", "👤 Profile"])
    
    with tab1:
        dashboard_tab()
    
    with tab2:
        predictions_tab()
    
    with tab3:
        recommendations_tab()
    
    with tab4:
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
                
                # Add to user logs
                today = datetime.now().strftime("%Y-%m-%d")
                log_entry = {
                    'date': today,
                    'emails': emails_sent,
                    'video_calls': video_calls_hours,
                    'streaming': streaming_hours,
                    'cloud_storage': cloud_storage_gb,
                    'device_usage': device_hours,
                    'co2_grams': daily_co2
                }
                
                # Remove existing entry for today if exists
                st.session_state.user_data['daily_logs'] = [
                    log for log in st.session_state.user_data['daily_logs'] 
                    if log['date'] != today
                ]
                st.session_state.user_data['daily_logs'].append(log_entry)
                
                # Update gamification
                st.session_state.gamification.update_score(daily_co2)
                
                st.success(f"✅ Today's carbon footprint: **{daily_co2:.2f}g CO₂**")
                st.rerun()
    
    with col2:
        # Digital Green Score
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.subheader("🌱 Digital Green Score")
        
        if st.session_state.user_data['daily_logs']:
            recent_logs = st.session_state.user_data['daily_logs'][-7:]  # Last 7 days
            avg_daily_co2 = np.mean([log['co2_grams'] for log in recent_logs])
            green_score = max(0, 100 - (avg_daily_co2 / 50))  # Scale to 0-100
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
        current_level = st.session_state.gamification.get_current_level()
        st.write(f"**Level:** {current_level}")
        
        badges = st.session_state.gamification.get_badges()
        if badges:
            st.write("**Badges Earned:**")
            for badge in badges:
                badge_class = f"badge-{badge.lower()}"
                st.markdown(f'<span class="badge {badge_class}">{badge}</span>', unsafe_allow_html=True)
    
    # Visualizations
    if st.session_state.user_data['daily_logs']:
        st.subheader("📈 Carbon Footprint Trends")
        
        df = pd.DataFrame(st.session_state.user_data['daily_logs'])
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
                    'Emails': latest_log['emails'] * 4,  # 4g per email
                    'Video Calls': latest_log['video_calls'] * 150,  # 150g per hour
                    'Streaming': latest_log['streaming'] * 36,  # 36g per hour
                    'Cloud Storage': latest_log['cloud_storage'] * 10,  # 10g per GB
                    'Device Usage': latest_log['device_usage'] * 20  # 20g per hour
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
                if st.session_state.user_data['daily_logs']:
                    current_avg = np.mean([log['co2_grams'] for log in st.session_state.user_data['daily_logs'][-7:]])
                    daily_predicted = predicted_co2 / prediction_days
                    
                    if daily_predicted < current_avg:
                        st.success(f"📉 Great! That's {current_avg - daily_predicted:.2f}g less than your current daily average!")
                    else:
                        st.warning(f"📈 That's {daily_predicted - current_avg:.2f}g more than your current daily average. Consider the recommendations!")
    
    with col2:
        st.subheader("🎯 Optimization Scenarios")
        
        if st.session_state.user_data['daily_logs']:
            # Show different scenarios
            base_data = st.session_state.user_data['daily_logs'][-1] if st.session_state.user_data['daily_logs'] else {
                'emails': 20, 'video_calls': 2, 'streaming': 3, 'cloud_storage': 5, 'device_usage': 8
            }
            
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

def recommendations_tab():
    st.header("💡 Personalized Eco Recommendations")
    
    # Get personalized recommendations
    if st.session_state.user_data['daily_logs']:
        latest_log = st.session_state.user_data['daily_logs'][-1]
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

def profile_tab():
    st.header("👤 Your EcoMind Profile")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📊 Statistics")
        
        if st.session_state.user_data['daily_logs']:
            logs_df = pd.DataFrame(st.session_state.user_data['daily_logs'])
            
            total_days = len(logs_df)
            total_co2 = logs_df['co2_grams'].sum()
            avg_daily_co2 = logs_df['co2_grams'].mean()
            best_day_co2 = logs_df['co2_grams'].min()
            
            st.metric("🗓️ Days Tracked", total_days)
            st.metric("🌍 Total CO₂ Tracked", f"{total_co2:.2f}g")
            st.metric("📈 Daily Average", f"{avg_daily_co2:.2f}g")
            st.metric("🏆 Best Day", f"{best_day_co2:.2f}g")
            
            # Carbon footprint over time
            logs_df['date'] = pd.to_datetime(logs_df['date'])
            logs_df = logs_df.sort_values('date')
            
            fig_profile = px.line(
                logs_df, x='date', y='co2_grams',
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
        current_level = st.session_state.gamification.get_current_level()
        progress = st.session_state.gamification.get_level_progress()
        
        st.write(f"**Current Level:** {current_level}")
        st.progress(progress / 100)
        st.write(f"Progress to next level: {progress:.1f}%")
        
        # Badges display
        st.write("**🏆 Badges Earned:**")
        badges = st.session_state.gamification.get_badges()
        
        if badges:
            badge_cols = st.columns(len(badges))
            for i, badge in enumerate(badges):
                with badge_cols[i]:
                    badge_class = f"badge-{badge.lower()}"
                    st.markdown(f'<div style="text-align: center;"><span class="badge {badge_class}">{badge}</span></div>', unsafe_allow_html=True)
        else:
            st.info("Keep tracking to earn your first badge! 🌱")
        
        # Global comparison
        st.subheader("🌍 Global Impact")
        if st.session_state.user_data['daily_logs']:
            user_avg = np.mean([log['co2_grams'] for log in st.session_state.user_data['daily_logs']])
            global_avg = 2500  # Average global daily digital carbon footprint
            
            comparison = (global_avg - user_avg) / global_avg * 100
            
            if comparison > 0:
                st.success(f"🌟 You're {comparison:.1f}% below the global average!")
                st.balloons()
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
    st.subheader("⚙️ Data Management")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📤 Export Data", type="secondary"):
            if st.session_state.user_data['daily_logs']:
                df = pd.DataFrame(st.session_state.user_data['daily_logs'])
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"ecomind_data_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No data to export yet!")
    
    with col2:
        if st.button("🔄 Reset Data", type="secondary"):
            if st.button("⚠️ Confirm Reset", type="primary"):
                st.session_state.user_data = {
                    'daily_logs': [],
                    'total_score': 0,
                    'badges': [],
                    'level': 'Bronze',
                    'joined_date': datetime.now().strftime("%Y-%m-%d")
                }
                st.success("Data reset successfully!")
                st.rerun()
    
    with col3:
        st.write("**Member Since:**")
        st.write(st.session_state.user_data['joined_date'])

if __name__ == "__main__":
    main()
