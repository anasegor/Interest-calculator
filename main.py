from tkinter import * 
from tkinter import ttk
import tkinter as tk
from tkinter.ttk import Combobox  
from tkcalendar import Calendar
from datetime import datetime
import calcProc

#флаг для валидации строки
flag=True

# обработка значений из окна, подсчет процентов в функции, вывод результатов
def on_entry(event):
    
    if flag==False: return
    # Проверяем, являются ли строки пустыми
    owing = txt.get()
    date_str1 = txt1.get()
    date_str2 = txt2.get()
    if owing.strip() == "" or date_str1.strip() == "" or date_str2.strip() == "" : 
        return
    
    owing=float(owing)

    if combo1.get()=="в календарных днях(365/366)":
        period=365 #далее будет меняться от года
    else:
        period=360

    if combo2.get()=="в рублях":
        currency=1 
    elif combo2.get()=="в долларах":
        currency=2 
    else:
        currency=3
    
    #оснавная функция для расчетов
    data,sum_days, sum, average_rate=calcProc.calc_proc(date_str1, date_str2, period, owing, currency)
    
    txt0.configure(state='normal')
    txt0.delete(0, END)
    txt0.insert(INSERT, str(sum))
    txt0.configure(state='disabled')

    txt01.configure(state='normal')
    txt01.delete(0, END)
    txt01.insert(INSERT, str(average_rate))
    txt01.configure(state='disabled')

    for row in tree.get_children():
        tree.delete(row)

    for row in data:  
        tree.insert("", "end", values=(f"{row[0]}", f"{row[1]}", f"{row[2]}",f"{row[3]}",f"{row[4]} %",f"{row[5]}",f"{row[6]}"))
    tree.insert("", "end", values=(f"", f"", f"{'Итого:'}",f"{sum_days}",f"{average_rate} %",f"",f"{sum}"))
    tree.pack()

#валидация строки суммы задолженности
def validate(string, action):
    if action == "key":
        if string[-1]==" ":
            lbl_error.configure(text="")
            flag=True
            return True
        if (string[-1].isnumeric() or string[-1]=="."):
            lbl_error.configure(text="")
            flag=True
            return True
        else:
            lbl_error.configure(text="Недопустимое значение поля")
            flag=False
            return False
    else:
        lbl_error.configure(text="")
        flag=True
        return True

# календарь начала периода   
def calc1(event):
    window1 = tk.Toplevel(window)
    window1.title("Начало периода") 
    cal1 = Calendar(window1, selectmode = 'day',
                year = 2020, month = 5,
                day = 22)
    cal1.pack(pady = 20)
    close_button = Button(window1, text="Ок", command=lambda: (window1.destroy(),txt1.delete(0, END),txt1.insert(INSERT, datetime.strptime(cal1.get_date(), "%m/%d/%y").strftime("%Y-%m-%d") )))
    close_button.pack(anchor="center", expand=1)
# календарь конца периода
def calc2(event):
    window1 = tk.Toplevel(window)
    window1.title("Конец периода") 
    cal2 = Calendar(window1, selectmode = 'day',
                year = 2020, month = 5,
                day = 22)
    cal2.pack(pady = 20)
    close_button = Button(window1, text="Ок", command=lambda: (window1.destroy(),txt2.delete(0, END),txt2.insert(INSERT, datetime.strptime(cal2.get_date(), "%m/%d/%y").strftime("%Y-%m-%d"))))
    close_button.pack(anchor="center", expand=1)


# заполнения окна элементами
window = Tk()  
window.title("Калькулятор расчета процента на сумму долга") 
window.geometry('500x400')  

lbl = Label(window, text="Сумма задолженности:", padx=2, pady=5)  
lbl.place(x = 1, y = 1) 
 
check = (window.register(validate), "%P","%V")
txt = Entry(window, width=100, validate="key",validatecommand=check)  
txt.place(x = 145, y = 5, width = 100)
txt.bind('<KeyRelease>', on_entry)

combo2 = Combobox(window)  
combo2['values'] = ("в рублях", "в долларах", "в евро")  #как влияет??
combo2.current(0)  #вариант по умолчанию  
combo2.place(x = 260, y = 5, width = 100)  
combo2.bind("<<ComboboxSelected>>", on_entry)

lbl_error = Label(window,  text="...", padx=2, pady=5, background="#FFCDD2")  
lbl_error.place(x = 250, y = 25) 

lbl = Label(window,  text="Период задолженности:", padx=2, pady=5)  
lbl.place(x = 1, y = 51) 
 
txt1 = Entry(window, width=100,state=NORMAL)  
txt1.place(x = 145, y = 55, width = 100)
txt1.bind('<Button-1>', calc1)
txt1.bind('<FocusIn>', on_entry)

lbl = Label(window,  text="—", padx=2, pady=5)  
lbl.place(x = 250, y = 51) 

txt2 = Entry(window, width=100)  
txt2.place(x = 275, y = 55, width = 100) 
txt2.bind('<Button-1>', calc2)
txt2.bind('<FocusIn>', on_entry)

lbl = Label(window,  text="Период определять:", padx=2, pady=5)
lbl.place(x = 1, y = 105) 

combo1 = Combobox(window)  
combo1['values'] = ("в календарных днях(365/366)", "360 дней в году")  
combo1.current(0)  #вариант по умолчанию  
combo1.place(x = 150, y = 109, width = 250)
combo1.bind("<<ComboboxSelected>>", on_entry)

lbl = Label(window,  text="Проценты:", padx=2, pady=5)
lbl.place(x = 1, y = 255)
txt0 = Entry(window, width=10, state='disabled')  
txt0.place(x = 150, y = 260, width = 150)
lbl = Label(window,  text="Процентная ставка:", padx=2, pady=5)
lbl.place(x = 1, y = 305)
txt01 = Entry(window, width=10, state='disabled')  
txt01.place(x = 150, y = 310, width = 150)

#окно с выводом таблицы расчетов
window_for_result = tk.Toplevel(window)
window_for_result.title("Расчет процентов по правилам статьи 395 ГК РФ") 

frame = Frame(window_for_result)
frame.pack(pady=5)

# таблица для записи результатов вычисления процентов
columns = ("с1", "с2", "с3","с4","с5","с6","с7")
tree = ttk.Treeview(frame, columns=columns, show="headings")
tree.pack(side=LEFT)

tree.column("с1", anchor=CENTER, width=120, minwidth=120)
tree.column("с2", anchor=CENTER, width=80, minwidth=80)
tree.column("с3", anchor=CENTER, width=80, minwidth=80)
tree.column("с4", anchor=CENTER, width=80, minwidth=80)
tree.column("с5", anchor=CENTER, width=120, minwidth=120)
tree.column("с6", anchor=CENTER, width=80, minwidth=80)
tree.column("с7", anchor=CENTER, width=120, minwidth=120)

tree.heading("с1", text="Задолженность", anchor=CENTER)
tree.heading("с2", text="с", anchor=CENTER)
tree.heading("с3", text="по", anchor=CENTER)
tree.heading("с4", text="дни", anchor=CENTER)
tree.heading("с5", text="Процентная ставка", anchor=CENTER)
tree.heading("с6", text="Дней в году", anchor=CENTER)
tree.heading("с7", text="Проценты", anchor=CENTER)

sb = Scrollbar(frame, orient=VERTICAL)
sb.pack(side=RIGHT, fill=Y)
tree.config(yscrollcommand=sb.set)
sb.config(command=tree.yview)

window.mainloop() 


