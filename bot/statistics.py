import matplotlib.pyplot as plt
import requests
from datetime import datetime
# import numpy as np


def val(value, year, month, day):
    num = requests.get(f"https://www.nbrb.by/api/exrates/rates/{value}?parammode=2&ondate="
                       f"{year}-{month}-{day}").json()["Cur_OfficialRate"]
    return num


def get_week_stat(e_now, m_now, d_now, usd_value, eur_value, rub_value):
    usd = val("USD", e_now, m_now, d_now)
    usd_value.append(usd)
    eur = val("EUR", e_now, m_now, d_now)
    eur_value.append(eur)
    rub = val("RUB", e_now, m_now, d_now)
    rub_value.append(rub)


def main():
    now = datetime.today()
    e_now = now.year
    m_now = now.month
    d_now = now.day
    wd_now = now.weekday()

    print(e_now, m_now, d_now, wd_now)

    day_week = [1, 2, 3, 4, 5]
    usd_value = []
    eur_value = []
    rub_value = []

    if str(wd_now) == "4":  # пятница - 4 НЕ ЗАБЫТЬ ПОМЕНЯТЬ НА ПЯТНИЦУ
        print("Friday now")
        for i in range(0, 5):
            if d_now - i > 0:
                d_now = d_now - i
                # при нормальном раскладе
                get_week_stat(e_now, m_now, d_now, usd_value, eur_value, rub_value)

            elif m_now-1 > 0:
                m_now = m_now - 1
                if str(m_now) in "1357810" or m_now == 12:
                    m_now = 32
                if str(m_now) in "469" or m_now == 11:
                    m_now = 31
                if str(m_now) in "2":
                    m_now = 29
                get_week_stat(e_now, m_now, d_now, usd_value, eur_value, rub_value)
            else:
                e_now = e_now - 1
                m_now = 12
                d_now = 31
                get_week_stat(e_now, m_now, d_now, usd_value, eur_value, rub_value)

    e_now = now.year
    m_now = now.month
    d_now = now.day

    usd_value = usd_value[::-1]
    eur_value = eur_value[::-1]
    rub_value = rub_value[::-1]

    print(usd_value)
    print(eur_value)
    print(rub_value)

    plt.title("Динамика роста валют за неделю")    # dynamics of currency growth for the week
    plt.xlabel("День недели")
    plt.ylabel("Цена за единицу валюты")
    plt.xticks(day_week, ["Пн", "Вт", "Ср", "Чт", "Пт"])
    plt.plot(day_week, usd_value, label="1 Доллар", marker="o")
    plt.plot(day_week, eur_value, label="1 Евро", marker="o")
    plt.plot(day_week, rub_value, label="100 Российских рублей", marker="o")
    plt.legend()
    plt.savefig(f"friday apply/{e_now}-{m_now}-{d_now}.png")
    plt.show()


if __name__ == '__main__':
    main()
