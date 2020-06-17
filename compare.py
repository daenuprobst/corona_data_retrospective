import pandas as pd
from pandas.plotting import register_matplotlib_converters
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import seaborn as sns
import numpy as np

register_matplotlib_converters()
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%d. %m."))
#plt.gca().xaxis.set_major_locator(mdates.DayLocator())
#plt.gca().xaxis.set_major_locator(mdates.MonthLocator())

sns.set(rc={'figure.figsize':(11.7 / 3 ,8.27 / 3)})

sns.set_style("ticks")
sns.set_context("paper")


def main():
    df_bag = pd.read_csv("Sheet_2_(d)_(2)_Full_Data_data.csv", usecols=["Datum", "Canton", "Anzahl laborbestätigte Fälle", "pttod_1"])
    df_bag["Datum"] = pd.to_datetime(df_bag["Datum"], format="%d.%m.%Y")
    df_bag = df_bag.groupby(["Datum", "Canton"]).sum().reset_index()

    df_bag_c_tmp = df_bag.pivot(index="Datum", columns="Canton", values=["Anzahl laborbestätigte Fälle"]).reset_index()
    df_bag_c = pd.DataFrame(df_bag_c_tmp["Datum"])
    for col in df_bag_c_tmp["Anzahl laborbestätigte Fälle"]:
        df_bag_c[col] = df_bag_c_tmp["Anzahl laborbestätigte Fälle"][col]
    df_bag_c['CH'] = df_bag_c.sum(axis=1)
    df_bag_c = df_bag_c.set_index("Datum")

    df_bag_f_tmp = df_bag.pivot(index="Datum", columns="Canton", values=["pttod_1"]).reset_index()
    df_bag_f = pd.DataFrame(df_bag_f_tmp["Datum"])
    for col in df_bag_f_tmp["pttod_1"]:
        df_bag_f[col] = df_bag_f_tmp["pttod_1"][col]
    df_bag_f['CH'] = df_bag_f.sum(axis=1)
    df_bag_f = df_bag_f.set_index("Datum")

    df_bag_archive_c = pd.read_csv("webarchive_bag.csv").dropna()
    df_bag_archive_c["Date"] = pd.to_datetime(df_bag_archive_c["Date"], format="%d/%m/%Y")
    df_bag_archive_c = df_bag_archive_c.set_index("Date")
    
    df_cantons_c = pd.read_csv("https://raw.githubusercontent.com/daenuprobst/covid19-cases-switzerland/master/covid19_cases_switzerland_openzh.csv")
    df_cantons_f = pd.read_csv("https://raw.githubusercontent.com/daenuprobst/covid19-cases-switzerland/master/covid19_fatalities_switzerland_openzh.csv")
    df_cantons_c["Date"] = pd.to_datetime(df_cantons_c["Date"])
    df_cantons_f["Date"] = pd.to_datetime(df_cantons_f["Date"])

    df_cantons_c = df_cantons_c[(df_cantons_c["Date"] >= df_bag_c.index.min()) & (df_cantons_c["Date"] <= df_bag_c.index.max())]
    df_cantons_f = df_cantons_f[(df_cantons_f["Date"] >= df_bag_f.index.min()) & (df_cantons_f["Date"] <= df_bag_f.index.max())]
    df_cantons_c = df_cantons_c.set_index("Date")
    df_cantons_f = df_cantons_f.set_index("Date")
    df_cantons_c = df_cantons_c.fillna(method="ffill", axis=0).fillna(0)
    df_cantons_f = df_cantons_f.fillna(method="ffill", axis=0).fillna(0)
    df_cantons_c = df_cantons_c.diff().fillna(0)
    df_cantons_f = df_cantons_f.diff().fillna(0)

    df_bag_c_cum = df_bag_c.cumsum()
    df_bag_f_cum = df_bag_f.cumsum()
    df_cantons_c_cum = df_cantons_c.cumsum()
    df_cantons_f_cum = df_cantons_f.cumsum()


    fig, ax = plt.subplots()
    ax.axvspan(pd.Timestamp(2020, 3, 15), pd.Timestamp(2020, 3, 17), alpha=0.25, color="r", lw=0)
    ax.plot(df_cantons_c.index, [0] * len(df_cantons_c.index), dashes=[2, 2], c="gray")
    ax.plot(df_cantons_c.index, (df_bag_c_cum - df_cantons_c_cum)["CH"], label="post-hoc")
    ax.plot(df_cantons_c.index, df_bag_archive_c["CH_CUM"] - df_cantons_c_cum["CH"], label="archive")
    ax.set_xlabel("Date")
    ax.set_ylabel("FOPH - Cantonal Cases")
    # plt.title("Difference between COVID-19 Cases Reported by the BAG and the Cantons")
    plt.legend(frameon=False)
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d. %m."))
    plt.tight_layout()
    plt.savefig("bag_vs_cantona_c.png", format="png", dpi=600)

    fig, ax = plt.subplots()
    ax.plot(df_cantons_f.index, (df_bag_f_cum - df_cantons_f_cum)["CH"], label="post-hoc")
    ax.set_xlabel("Date")
    ax.set_ylabel("FOPH - Cantonal Fatalities")
    # plt.title("Difference between COVID-19 Fatalities Reported by the BAG and the Cantons")
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d. %m."))
    plt.legend(frameon=False)
    plt.tight_layout()
    plt.savefig("bag_vs_cantona_f.png", format="png", dpi=600)

    fig, ax = plt.subplots()
    ax.axvspan(pd.Timestamp(2020, 3, 15), pd.Timestamp(2020, 3, 17), alpha=0.25, color="r", lw=0)
    ax.plot(df_cantons_c.index, df_cantons_c_cum["CH"], label="Cantons")
    ax.plot(df_bag_c.index, df_bag_c_cum["CH"], label="FOPH (post-hoc)")
    ax.plot(df_bag_archive_c.index, df_bag_archive_c["CH_CUM"], label="FOPH (archive)")
    ax.plot(df_cantons_c.index - pd.DateOffset(1), df_cantons_c_cum["CH"], label="Cantons (- 1 day)", dashes=[5, 5], c="gray")
    ax.set_xlabel("Date")
    ax.set_ylabel("Cases")
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d. %m."))
    plt.legend(frameon=False)
    # plt.title("Cumulative Daily Cases")
    plt.tight_layout()
    plt.savefig("bag_vs_cantona_compared.png", format="png", dpi=600)

    fig, ax = plt.subplots(figsize=(11.7 / 3 ,8.27 / 4))
    ax.plot(df_cantons_c.index[:20], df_cantons_c_cum["CH"][:20], label="Cantons")
    ax.set_xlabel("Date")
    ax.set_ylabel("Cases")
    ax.set_yscale("log")
    ax.xaxis.set_major_locator(mdates.WeekdayLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d. %m."))
    plt.legend(frameon=False)
    plt.tight_layout()
    plt.savefig("cantons_log.png", format="png", dpi=600)

    fig, ax = plt.subplots(figsize=(11.7 / 3 ,8.27 / 4))
    ax.plot(df_cantons_c.index[:20], df_cantons_c_cum["CH"][:20], label="Cantons")
    ax.set_xlabel("Date")
    ax.set_ylabel("Cases")
    ax.xaxis.set_major_locator(mdates.WeekdayLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d. %m."))
    plt.legend(frameon=False)
    plt.tight_layout()
    plt.savefig("cantons.png", format="png", dpi=600)

    cantons_c_cum = df_cantons_c_cum["CH"].values
    bag_c_cum = df_bag_c_cum["CH"].values

    print(np.sum(np.abs(cantons_c_cum - bag_c_cum)))

    # Shift a day back
    cantons_c_cum = np.delete(cantons_c_cum, 0)
    bag_c_cum = np.delete(bag_c_cum, -1)
    print(np.sum(np.abs(cantons_c_cum - bag_c_cum)))

    # Shift two days back
    cantons_c_cum = np.delete(cantons_c_cum, 0)
    bag_c_cum = np.delete(bag_c_cum, -1)
    print(np.sum(np.abs(cantons_c_cum - bag_c_cum)))

    print("\n")

    # To do the same for the archive, first join data sets
    df_bag_archive_c.drop(columns=["CH"], inplace=True)
    df_joined = df_bag_c_cum.join(df_bag_archive_c, how="inner")
    

    cantons_c_cum = df_joined["CH_CUM"].values
    bag_c_cum = df_joined["CH"].values

    print(np.sum(np.abs(cantons_c_cum - bag_c_cum)))

    # Shift a day back
    cantons_c_cum = np.delete(cantons_c_cum, 0)
    bag_c_cum = np.delete(bag_c_cum, -1)
    print(np.sum(np.abs(cantons_c_cum - bag_c_cum)))

    # Shift two days back
    cantons_c_cum = np.delete(cantons_c_cum, 0)
    bag_c_cum = np.delete(bag_c_cum, -1)
    print(np.sum(np.abs(cantons_c_cum - bag_c_cum)))

    # Shift three days back
    cantons_c_cum = np.delete(cantons_c_cum, 0)
    bag_c_cum = np.delete(bag_c_cum, -1)
    print(np.sum(np.abs(cantons_c_cum - bag_c_cum)))

    # Shift four days back
    cantons_c_cum = np.delete(cantons_c_cum, 0)
    bag_c_cum = np.delete(bag_c_cum, -1)
    print(np.sum(np.abs(cantons_c_cum - bag_c_cum)))


if __name__ == "__main__":
    main()