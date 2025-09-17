# ai_chatbot.py
def ai_chatbot(prompt=None, battery_data=None, forecast_data=None):
    """
    Dummy AI chatbot with specific predefined answers.
    """

    answers = {
        "How many hours will my battery last?": 
            f"⏳ Your battery can last around {battery_data['runtime_hours']:.1f} hours at the current load.",

        "Is my battery level safe right now?": 
            f"🔋 Your battery is at {battery_data['current_charge']} kWh ({(battery_data['current_charge']/battery_data['capacity']*100):.1f}%). This is considered safe.",

        "When is the best time to charge my battery?": 
            "☀️ The best time to charge your battery is during peak solar hours, usually between 10 AM and 3 PM.",

        "How much solar energy is available today?": 
            f"☀️ Today's average solar radiation is {forecast_data['solar_avg']:.2f} kWh/m².",

        "When is the peak solar time?": 
            "☀️ Peak solar energy is typically at noon (12–2 PM).",

        "What is the wind speed trend?": 
            f"🌬️ Average wind speed is {forecast_data['wind_avg']:.2f} m/s, with a peak of {forecast_data['wind_peak']:.2f} m/s.",

        "Should I use grid or renewable energy right now?": 
            "⚡ Use renewable energy during the day when solar/wind is available. Switch to grid at night if battery is low.",

        "Give me tips for extending my battery life.": 
            "💡 Avoid deep discharges, use renewable sources during the day, and maintain battery charge between 20%–80%."
    }

    if prompt and prompt in answers:
        return answers[prompt]
    elif prompt:
        return f"🤖 You asked: '{prompt}'. Try selecting a question from the dropdown!"
    else:
        # Auto Insights (default mode)
        return (
            "✅ Battery is healthy.\n"
            f"☀️ Solar average: {forecast_data['solar_avg']:.2f} kWh/m².\n"
            f"🌬️ Wind average: {forecast_data['wind_avg']:.2f} m/s.\n"
            "⚡ Recommendation: Use renewables during the day, grid at night."
        )
