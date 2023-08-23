#!/usr/bin/env python3


def check_coupon(entered_code, correct_code, current_date, expiration_date):
    if entered_code != correct_code:
        return False
    c_month, c_day, c_year = current_date.split()
    e_month, e_day, e_year = expiration_date.split()
    months = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]

    if int(c_year) < int(e_year):
        return True
    elif int(c_year) == int(e_year):
        print(months.index(c_month), months.index(e_month))
        if months.index(c_month) < months.index(e_month):
            return True
        elif months.index(c_month) == months.index(e_month):
            return int(c_day) <= int(e_day)
        else:
            return False
    else:
        return False


if __name__ == "__main__":
    print(check_coupon("123", "123", "September 5, 2014", "October 1, 2014"))
    print(check_coupon("123a", "123", "September 5, 2014", "October 1, 2014"))
