import check_if_forest
import retrieve_weather_data
import pandas as pd
import matplotlib.pyplot as plt

raw_coordinate = """
                33°53'23.6"S 150°29'11.8"E
                """

if_forest = check_if_forest.check_if_forest(f"{raw_coordinate}")

if if_forest["is_forest"]:
    monthly_df = retrieve_weather_data.download_and_process_weather_data(raw_coordinate)

    monthly_df["fire_risk_score"] = (
        monthly_df["temperature_2m_mean"] * 0.5 +
        monthly_df["wind_speed_10m_max"] * 0.4 -
        monthly_df["precipitation_sum"] * 0.1
    )

    monthly_df["month"] = pd.to_datetime(monthly_df["year_month"].astype(str)).dt.month
    monthly_df["month_name"] = pd.to_datetime(monthly_df["month"], format="%m").dt.strftime("%B")

    avg_by_month = monthly_df.groupby("month_name")["fire_risk_score"].mean().reindex([
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ])

    colors = [
        "red" if val >= 20 else
        "yellow" if val >= 14 else
        "blue"
        for val in avg_by_month
    ]

    avg_by_month.plot(kind="bar", color=colors, edgecolor="black")
    plt.title("10-Year Average Monthly Fire Risk Score")
    plt.xlabel("Month")
    plt.ylabel("Average Risk Score")
    plt.xticks(rotation=45)
    plt.grid(axis='y')
    plt.tight_layout()
    plt.savefig("fire_risk_plot.png")
    plt.show()
else:
    print("This area is likely not a forested region.")