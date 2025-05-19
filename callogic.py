#! /bin/python3

# Disclaimer: typically it is considered extremely bad practice to create your own date system,
# I just wanted to make one as a learning experience.
# 18.4.2025 3:30 AM i feel like appending to this disclaimer, yeah it was kind of a bad idea haha
# But __date_parse "fixed" now

def __date_parse(wkd_index, max_days,debug=False):
    i = 1
    d = wkd_index # 0 for monday, 6 for sunday
    month = [[],[],[],[],[],[],[]]
    while i <= max_days:
        if debug == True:
            print(d, "index value")
        if d > 6:
            d = 0
            if debug == True:
                print("@@@@@@failsafe reset called@@@@@@")
        month[d].append(i)
        if d < 6:
            d+=1
        else:
            if debug == True:
                print("######reset called######")
            d=0
        
        i+=1
    i=0
    while i <= 6:
        month[i] = set(month[i])
        i+=1
    month = tuple(month)
    return month


'''
what in the actual flying fuck, a leap year set to start on thursday crashes the system
because somehow "d" in date parse can go runaway and end up being higher than 6


'''

def construct_month(month_name,max_days,wkd_index,debug=False):
    vertibar = "│"
    tbar_spacer = "─"
    month_header = f"┌──┤ {month_name} ├"

    while len(month_header + tbar_spacer + "┐") < 24:
        tbar_spacer = tbar_spacer + "─"

    datebar = f"{vertibar} Mo Tu We Th Fr Sa Su {vertibar}"
    calendar = f"{month_header}{tbar_spacer}┐"
    display_month = [calendar,datebar]
    month = __date_parse(wkd_index, max_days,debug)

    i=1
    while i <= max_days:
        d=0
        while d <= 6:
            exists = i in month[d]
            if exists == False:
                day = "--"
            else:
                if len(str(i)) < 2:
                    day = "0" + str(i)
                    i+=1
                else:
                    day = str(i)
                    i+=1
                day_index = d

            if d == 0:
                d_mon = day
            if d == 1:
                d_tue = day
            if d == 2:
                d_wed = day
            if d == 3:
                d_thu = day
            if d == 4:
                d_fri = day
            if d == 5:
                d_sat = day
            if d == 6:
                d_sun = day
            d+=1
        display_month.append(f"│ {d_mon} {d_tue} {d_wed} {d_thu} {d_fri} {d_sat} {d_sun} │")
    
    display_month.append("└──────────────────────┘")
    display_month = tuple(display_month)
    if debug == True:
        for line in display_month:
            print(''.join(line))
        print(f"({display_month},{day_index})")
    return (display_month,day_index) # remember +1 for continuation to next month

def __parse_wkd_index(month):
    if month[1] >= 6:
        return 0
    else:
        return (month[1] + 1)

def construct_year(wkd_index, leap_year=False,debug=False):
    jan = construct_month("January",31,wkd_index,False)
    if leap_year == False:
        feb_days = 28
    else:
        feb_days = 29
    wkd_index = __parse_wkd_index(jan)
    feb = construct_month("February",feb_days,wkd_index,debug)
    wkd_index = __parse_wkd_index(feb)
    mar = construct_month("March",31,wkd_index,debug)
    wkd_index = __parse_wkd_index(mar)
    apr = construct_month("April",30,wkd_index,debug)
    wkd_index = __parse_wkd_index(apr)
    may = construct_month("May",31,wkd_index,debug)
    wkd_index = __parse_wkd_index(may)
    jun = construct_month("June",30,wkd_index,debug)
    wkd_index = __parse_wkd_index(jun)
    jul = construct_month("July",31,wkd_index,debug)
    wkd_index = __parse_wkd_index(jul)
    aug = construct_month("August",31,wkd_index,debug)
    wkd_index = __parse_wkd_index(aug)
    sep = construct_month("September",30,wkd_index,debug)
    wkd_index = __parse_wkd_index(sep)
    octo = construct_month("October",31,wkd_index,debug)
    wkd_index = __parse_wkd_index(octo)
    nov = construct_month("November",30,wkd_index,debug)
    wkd_index = __parse_wkd_index(nov)
    dec = construct_month("December",31,wkd_index,debug)
    return (jan,feb,mar,apr,may,jun,jul,aug,sep,octo,nov,dec,)
