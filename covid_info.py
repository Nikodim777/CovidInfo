import sys
import requests as req
import matplotlib.pyplot as plot
from collections import OrderedDict
from bs4 import BeautifulSoup as bs

#Получение минимальной численности населения (для отсечения стран с меньшим населением)
if len(sys.argv) > 1:
    if sys.argv[1] == "/?":
        print("Формат - 'covid_info [n]' где n - мининимум населения для рассматриваемых стран")
        exit(0)
    minpopul = int(sys.argv[1])
else:
    minpopul = 0

#Получение страницы с данными о населении стран
res = req.get("https://en.wikipedia.org/wiki/List_of_countries_and_dependencies_by_population")
pagepop = bs(res.text, "html.parser")
#Получение всех строк таблицы данных
pops = pagepop.table.tbody.find_all("tr")
#Получение страницы с данными о заболеваемости Covid19
res = req.get("https://en.wikipedia.org/wiki/COVID-19_pandemic_by_country_and_territory")
pagecov = bs(res.text, "html.parser")
#Получение всех строк таблицы данных
covtable = pagecov.find(id = "thetable")
covs = covtable.tbody.find_all("tr", {"class":""})

datapop = {} #Словарь содержащий инфу о населении стран

for i in range(1,len(pops)):
    if pops[i].th.text != "–\n" and pops[i].th.text != "" and pops[i].th.text != "—\n": #Отсеиваем псевдо-страны
        try:
            tdnum = pops[i].find("td", {"style":"text-align:right"}) #Получаем численность населения
            datapop[pops[i].td.a.text] = int(tdnum.text.replace(",","")) #Создаём запись о стране
        except:
            continue
        
datacov = {} #Словарь содержащий инфу о заболеваемости в странах

for i in range(0,len(covs)):
    datael = []
    cov_info = covs[i].find_all("td")
    try: #Пытаемся получить инфу о заразившихся
        datael.append(int(cov_info[0].text.rstrip("\n").replace(",","")))
    except:
        datael.append(0)
    try: #Пытаемся получить инфу об умерших
        datael.append(int(cov_info[1].text.rstrip("\n").replace(",","")))
    except:
        datael.append(0)
    try: #Пытаемся получить инфу о выздоровевших
        datael.append(int(cov_info[2].text.rstrip("\n").replace(",","")))
    except:
        datael.append(0)
        
    heads = covs[i].find_all("th")
    datacov[heads[1].a.text] = datael #Создаём запись

sicklist = {} #Словарь отношений числа заразившихся к населению
deathlist = {} #Словарь отношений числа  умерших к населению
heallist = {} #Словарь отношений числа выздоровевших к населению
cursicklist = {} #Словарь отношений числа заражённых к населению

for country,popul in datapop.items():
    if popul < minpopul:
        break
    
    try:
        covlist = datacov[country] #Получаем данные о заболеваемости
    except:
        continue

    aspect = round((covlist[0]/popul)*100,3)
    sicklist[country] = aspect
    
    aspect = round((covlist[1]/popul)*100,3)
    deathlist[country] = aspect
    
    aspect = round((covlist[2]/popul)*100,3)
    heallist[country] = aspect
    
    aspect = round(((covlist[0] - covlist[1] - covlist[2])/popul)*100,3)
    cursicklist[country] = aspect

print("Число рассматриваемых стран - ",len(sicklist))

sort_sl = OrderedDict(sorted(sicklist.items(), key = lambda i:i[1], reverse = True))
sort_dl = OrderedDict(sorted(deathlist.items(), key = lambda i:i[1], reverse = True))
sort_hl = OrderedDict(sorted(heallist.items(), key = lambda i:i[1], reverse = True))
sort_cl = OrderedDict(sorted(cursicklist.items(), key = lambda i:i[1], reverse = True))

while(True):
    print("Введите 0 что-бы получить график отношений (число заразившихся/население) по странам")
    print("Введите 1 что-бы получить график отношений (число умерших/население) по странам")
    print("Введите 2 что-бы получить график отношений (число выздоровевших/население) по странам")
    print("Введите 3 что-бы получить график отношений (число зараженных/население) по странам")
    print("Введите 4 что-бы получить csv-файл информации о COVID19 по странам")
    print("Введите любое другое число что-бы выйти")

    inp_val = int(input())

    if inp_val < 4:
        plot.clf() #Очищаем график
        figManager = plot.get_current_fig_manager() 
        figManager.resize(1300,500) #Настраиваем размер окна
        plot.subplots_adjust(left=0.045, right=0.98) #Настраиваем положение графика в окне
        plot.ylabel("Процент")
        
        if inp_val == 0:
            plot.bar(range(len(sicklist)),sort_sl.values())
            plot.title("График отношения числа заразившихся к численности населения")
            plot.xticks(range(len(sicklist)),sort_sl.keys())
        elif inp_val == 1:
            plot.bar(range(len(deathlist)),sort_dl.values())
            plot.title("График отношения числа умерших к численности населения")
            plot.xticks(range(len(deathlist)),sort_dl.keys())
        elif inp_val == 2:
            plot.bar(range(len(heallist)),sort_hl.values())
            plot.title("График отношения числа выздоровевших к численности населения")
            plot.xticks(range(len(heallist)),sort_hl.keys())
        elif inp_val == 3:
            plot.bar(range(len(cursicklist)),sort_cl.values())
            plot.title("График отношения числа заражённых к численности населения")
            plot.xticks(range(len(cursicklist)),sort_cl.keys())
            
        plot.show()
    elif inp_val == 4:
        file = open("covid_info.csv","w", encoding="cp1251")
        file.write("Страна,Заразившиеся/Население в %,Умершие/Население в %,Выздоровевшие/Население в %,Зараженные/Население в %\n")
        for country in sort_sl.keys():
            file.write("{0},{1},{2},{3},{4}\n".format(country,sort_sl[country],sort_dl[country],sort_hl[country],sort_cl[country]).encode('utf8').decode('cp1251'))
        file.close()
    else:
        break


