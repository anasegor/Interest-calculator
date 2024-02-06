import sqlite3
from datetime import datetime, timedelta

data=[] # возвращаемый массив значений расчета процентов на каждом периоде

# функция вычисления кол-ва дней между датами(не вкл. последний день)
def calc_sum_days(str_date1,str_date2):
    date1 = datetime.strptime(str_date1, "%Y-%m-%d")
    date2 = datetime.strptime(str_date2, "%Y-%m-%d")
    return (date2 - date1).days
# функция вычисления кол-ва дней до начала след года
def calc_sum_days_end_year(date1):
    date2 = datetime(year=date1.year+1, month=1, day=1)
    return (date2 - date1).days, date2

def calc_count_periods(date_object1,date_object2, owing,rate):
    date_object2_1 = date_object2 - timedelta(days=1)# 1день 2й даты не должен входить в сравнение годов
    # расчет кол-ва периодов
    N = int(date_object2_1.year-date_object1.year+1)
    temp_period=0
    temp_days=0
    temp_date=date_object1
    summ=0

    # первый период:
    if temp_date.year%4==0:
        temp_period=366
    else:
        temp_period=365
    temp_days,temp_date=calc_sum_days_end_year(date_object1) # дата начала след года
    sum_proc=round(owing*rate*temp_days/(temp_period*100),2)
    summ+=sum_proc
    # дата конца нужного года
    date2 = datetime(year=date_object1.year, month=12, day=31)
    data0=[owing,date_object1.strftime("%Y-%m-%d"),date2.strftime("%Y-%m-%d"), temp_days, rate, temp_period, sum_proc]
    data.append(data0)
    # не включая первый и последний период:
    if (N-3)>=0:
        for i in range(1,N-1):
            if (temp_date.year)%4==0:
                temp_period=366
            else:
                temp_period=365
            temp_days=temp_period
            sum_proc=round(owing*rate*temp_days/(temp_period*100),2)
            summ+=sum_proc
            #дата конца нужного года:
            date2 = datetime(year=temp_date.year, month=12, day=31)
            data0=[owing,temp_date.strftime("%Y-%m-%d"),date2.strftime("%Y-%m-%d"), temp_days, rate, temp_period, sum_proc]
            data.append(data0)
            temp_date.year+=1

    #последний период:
    if (N-2)>=0:
        if temp_date.year%4==0:
                temp_period=366
        else:
                temp_period=365
        str_date1 = temp_date.strftime("%Y-%m-%d")
        str_date2 = date_object2.strftime("%Y-%m-%d")
        temp_days=calc_sum_days(str_date1,str_date2)
        sum_proc=round(owing*rate*temp_days/(temp_period*100),2)
        summ+=sum_proc
        str_date2_=(datetime.strptime(str_date2, "%Y-%m-%d")-timedelta(days=1)).strftime("%Y-%m-%d")
        data0=[owing,str_date1,str_date2_, temp_days, rate, temp_period, sum_proc]
        data.append(data0)

    return summ

# внутри функции период расчета до изменения ставки может делиться на подпериоды, если у даты начала и конца разные года
def calc_sum_period(count_days,rate,period,owing,str_date1,str_date2):
    date_object1 = datetime.strptime(str_date1, "%Y-%m-%d")
    date_object2 = datetime.strptime(str_date2, "%Y-%m-%d")#надо убавить 1 день для сравнения годов, тк мы его не считаем 
    date_object2_1 = date_object2 - timedelta(days=1)
    # если делим на календарные дни
    if period!=360:
        # если год начала и конца один и тот же
        if date_object1.year==date_object2_1.year:
            if date_object1.year%4==0: 
                period=366
            else:
                period=365
            # считаем процент
            sum_proc=owing*count_days*rate/(100*period)
            # добавляем в выходную табличку данные:
            data0=[owing,str_date1,date_object2_1.strftime("%Y-%m-%d"), count_days, rate,period, round(sum_proc,2) ]
            data.append(data0)
            return sum_proc
        # иначе отправляем в функцию, которая будет делить период на подпериоды с одинаковым годом в них
        else:
            return calc_count_periods(date_object1,date_object2, owing,rate)
    # если делим на 360
    else:
        # считаем процент
        sum_proc=owing*count_days*rate/(100*period)
        # добавляем в выходную табличку данные:
        data0=[owing,str_date1,date_object2_1.strftime("%Y-%m-%d"), count_days, rate,period, round(sum_proc,2) ]
        data.append(data0)
        return sum_proc

# точка входа. Принимает на вход дату начала и конца расчета в виде строк, период для расчета(по кол-ву дней в календарном годе или 360),
# задолженность и валюту
def calc_proc(strDate1, strDate2, period, owing, currency):
    data.clear()
    sum_proc=0 # общий процент
    sum_days=0 # общее кол-во дней
    rate=0 # ставка
    average_rate=0 # средняя ставка
    flag=True
    cur_date=strDate1 # текущая дата начала подпериода
    #подкл. к БД:
    connection = sqlite3.connect('my_database.db')
    cur = connection.cursor() 

    # получаем 1ю ставку (действовала до займа):
    cur.execute(f"""
                    SELECT date,rate 
                    FROM DateRate 
                    WHERE date = (
                                SELECT max(date) 
                                FROM DateRate 
                                WHERE date <= '{strDate1}')
                    """)
    row = cur.fetchone()

    #ставка в зависимости от валюты фиксированная или получена из БД:
    if currency==1:
        rate=row[1]
    elif currency==2:
        rate=1.29
    else:
        rate=0.7
    
    # цикл по всему периоду расчета:
    while cur_date < strDate2:
    #считаем след. ставку
        # если последний день в периоде задолженности равен дню изменения ставки:
        if cur_date==strDate2:
            #период для расчета
            if period!=360:
                date_object = datetime.strptime(strDate2, "%Y-%m-%d")
                year = date_object.year
                if year%4==0:
                    period=366
                else: period=365
            #считаем процент:
            sum_proc+=owing*count_days*rate/(100*period) 

            sum_days+=1
            average_rate+=rate
            break
        else:
            try:
                cur.execute(f"""
                            SELECT date,rate 
                            FROM DateRate 
                            WHERE date = (
                                        SELECT min(date) 
                                        FROM DateRate 
                                        WHERE date <= '{strDate2}' AND date > '{cur_date}')
                            """)

                row = cur.fetchone()
                next_date=row[0]
            #если ошибка(в бд не найдена новая дата изм. ставки), то в оставшемся периоде больше нет изменений ставки
            except TypeError:
                next_date=strDate2
                date_object = datetime.strptime(next_date, "%Y-%m-%d")
                # Прибавляем 1 день к дате(чтобы учесть последний день)
                new_date_object = date_object + timedelta(days=1)
                next_date = new_date_object.strftime("%Y-%m-%d")
                # кол-во дней до след ставки
                count_days=calc_sum_days(cur_date,next_date)
                # вычисляем процент
                sum_proc+=round(calc_sum_period(count_days,rate,period,owing,cur_date,next_date),2)

                sum_days+=count_days
                average_rate+=count_days*rate
                break
            # если нет ошибки(след дата и ставка найдены)
            if flag==True:
                # кол-во дней до след ставки
                count_days=calc_sum_days(cur_date,next_date)
                # вычисляем процент
                sum_proc+=round(calc_sum_period(count_days,rate,period,owing,cur_date,next_date),2)

                sum_days+=count_days
                average_rate+=count_days*rate

            #ставка в зависимости от валюты фиксированная или получена из БД:
            if currency==1:
                rate=row[1]
            elif currency==2:
                rate=1.29
            else:
                rate=0.7
                
            cur_date=row[0]

    connection.commit()
    connection.close()
    # расчет средней ставки
    average_rate/=sum_days
    average_rate=round(average_rate,2)
    
    return data,sum_days,round(sum_proc,2), average_rate
