import pandas as pd
import sqlite3
import numpy as np

import numpy as np
import pandas as pd
from sklearn.linear_model import RidgeClassifier, RidgeClassifierCV
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import warnings
warnings.filterwarnings('ignore')

temp_graphs = {
    '150-70': {'подающий': [(-26,130),(-25,130),(-24,130),(-23,130),(-22,130),(-21,130),(-20,130),
                            (-19,130),(-18,130),(-17,130),(-16,127),(-15,124),(-14,122),(-13,119),
                            (-12,117),(-11,114),(-10,111),(-9,109),(-8,106),(-7,103),(-6,101),(-5,98),
                            (-4,95),(-3,93),(-2,90),(-1,87),(-0,85),(1,82),(2,79),(3,76),(4,75),
                            (5,75),(6,75),(7,75),(8,75)],
                 'обратный': [(-26,56),(-25,57),(-24,58),(-23,59),(-22,60),(-21,61),(-20,62),
                            (-19,63),(-18,64),(-17,65),(-16,64),(-15,63),(-14,62),(-13,61),
                            (-12,60),(-11,59),(-10,58),(-9,57),(-8,56),(-7,55),(-6,54),(-5,53),
                            (-4,52),(-3,51),(-2,50),(-1,49),(-0,48),(1,48),(2,48),(3,48),(4,48),
                            (5,48),(6,48),(7,48),(8,48)]},
    '*150-70': {'подающий': [(-26,130),(-25,130),(-24,130),(-23,130),(-22,130),(-21,130),(-20,130),
                            (-19,130),(-18,130),(-17,130),(-16,128),(-15,125),(-14,123),(-13,120),
                            (-12,118),(-11,115),(-10,112),(-9,110),(-8,107),(-7,105),(-6,102),(-5,100),
                            (-4,97),(-3,94),(-2,92),(-1,89),(-0,87),(1,84),(2,81),(3,79),(4,77),
                            (5,77),(6,77),(7,77),(8,77)],
                 'обратный': [(-26,57),(-25,58),(-24,59),(-23,60),(-22,61),(-21,62),(-20,63),
                            (-19,64),(-18,65),(-17,66),(-16,65),(-15,64),(-14,63),(-13,62),
                            (-12,61),(-11,60),(-10,59),(-9,58),(-8,57),(-7,56),(-6,55),(-5,54),
                            (-4,53),(-3,52),(-2,51),(-1,50),(-0,49),(1,48),(2,48),(3,48),(4,48),
                            (5,48),(6,48),(7,48),(8,48)]},
    '130-70': {'подающий': [(-26,130),(-25,129),(-24,128),(-23,126),(-22,124),(-21,122),(-20,119),
                            (-19,117),(-18,115),(-17,113),(-16,111),(-15,109),(-14,107),(-13,104),
                            (-12,102),(-11,100),(-10,98),(-9,96),(-8,93),(-7,91),(-6,89),(-5,87),
                            (-4,85),(-3,82),(-2,80),(-1,78),(-0,76),(1,73),(2,71),(3,70),(4,70),
                            (5,70),(6,70),(7,70),(8,70)],
                 'обратный': [(-26,70),(-25,69),(-24,69),(-23,68),(-22,68),(-21,67),(-20,66),
                            (-19,65),(-18,64),(-17,63),(-16,63),(-15,62),(-14,61),(-13,60),
                            (-12,59),(-11,58),(-10,57),(-9,57),(-8,56),(-7,55),(-6,54),(-5,53),
                            (-4,52),(-3,51),(-2,50),(-1,49),(-0,48),(1,47),(2,46),(3,45),(4,45),
                            (5,45),(6,45),(7,45),(8,45)]},
    '120-70': {'подающий': [(-26,120),(-25,119),(-24,118),(-23,116),(-22,114),(-21,112),(-20,111),
                            (-19,109),(-18,107),(-17,105),(-16,103),(-15,101),(-14,99),(-13,97),
                            (-12,95),(-11,93),(-10,91),(-9,89),(-8,87),(-7,85),(-6,83),(-5,81),
                            (-4,79),(-3,77),(-2,75),(-1,73),(-0,71),(1,68),(2,66),(3,64),(4,62),
                            (5,60),(6,57),(7,55),(8,53)],
                 'обратный': [(-26,70),(-25,69),(-24,69),(-23,68),(-22,67),(-21,67),(-20,66),
                            (-19,65),(-18,64),(-17,63),(-16,62),(-15,61),(-14,61),(-13,60),
                            (-12,59),(-11,58),(-10,57),(-9,56),(-8,55),(-7,54),(-6,53),(-5,52),
                            (-4,51),(-3,50),(-2,49),(-1,48),(-0,47),(1,46),(2,45),(3,44),(4,43),
                            (5,42),(6,41),(7,40),(8,38)]},
    '114-70': {'подающий': [(-26,114),(-25,113),(-24,112),(-23,111),(-22,109),(-21,107),(-20,105),
                            (-19,103),(-18,101),(-17,99),(-16,97),(-15,96),(-14,94),(-13,92),
                            (-12,90),(-11,88),(-10,85),(-9,83),(-8,81),(-7,79),(-6,77),(-5,75),
                            (-4,73),(-3,71),(-2,69),(-1,67),(-0,65),(1,62),(2,60),(3,58),(4,56),
                            (5,53),(6,51),(7,49),(8,46)],
                 'обратный': [(-26,70),(-25,69),(-24,69),(-23,68),(-22,67),(-21,67),(-20,66),
                            (-19,65),(-18,64),(-17,63),(-16,62),(-15,61),(-14,61),(-13,60),
                            (-12,59),(-11,58),(-10,57),(-9,56),(-8,55),(-7,54),(-6,53),(-5,52),
                            (-4,51),(-3,50),(-2,49),(-1,48),(-0,47),(1,46),(2,45),(3,44),(4,43),
                            (5,42),(6,41),(7,40),(8,38)]},
    '105-70': {'подающий': [(-26,105),(-25,104),(-24,103),(-23,102),(-22,100),(-21,98),(-20,96),
                            (-19,95),(-18,93),(-17,91),(-16,89),(-15,88),(-14,86),(-13,84),
                            (-12,82),(-11,81),(-10,79),(-9,77),(-8,75),(-7,73),(-6,71),(-5,70),
                            (-4,68),(-3,66),(-2,64),(-1,62),(-0,60),(1,58),(2,56),(3,54),(4,52),
                            (5,50),(6,48),(7,46),(8,44)],
                 'обратный': [(-26,70),(-25,69),(-24,69),(-23,68),(-22,67),(-21,67),(-20,66),
                            (-19,65),(-18,64),(-17,63),(-16,62),(-15,61),(-14,61),(-13,60),
                            (-12,59),(-11,58),(-10,57),(-9,56),(-8,55),(-7,54),(-6,53),(-5,52),
                            (-4,51),(-3,50),(-2,49),(-1,48),(-0,47),(1,46),(2,45),(3,44),(4,43),
                            (5,42),(6,41),(7,40),(8,38)]},
    '95-70': {'подающий': [(-26,95),(-25,94),(-24,93),(-23,92),(-22,91),(-21,89),(-20,88),
                            (-19,86),(-18,84),(-17,83),(-16,81),(-15,80),(-14,78),(-13,77),
                            (-12,75),(-11,74),(-10,72),(-9,70),(-8,69),(-7,67),(-6,65),(-5,64),
                            (-4,62),(-3,61),(-2,59),(-1,57),(-0,55),(1,54),(2,52),(3,50),(4,48),
                            (5,47),(6,45),(7,43),(8,41)],
                 'обратный': [(-26,70),(-25,69),(-24,69),(-23,68),(-22,67),(-21,67),(-20,66),
                            (-19,65),(-18,64),(-17,63),(-16,62),(-15,61),(-14,61),(-13,60),
                            (-12,59),(-11,58),(-10,57),(-9,56),(-8,55),(-7,54),(-6,53),(-5,52),
                            (-4,51),(-3,50),(-2,49),(-1,48),(-0,47),(1,46),(2,45),(3,44),(4,43),
                            (5,42),(6,41),(7,40),(8,38)]}
}

conn_wdb = sqlite3.connect('service/weather.db')
df_wether = pd.read_sql_query('SELECT * FROM melted_weather', conn_wdb)
df_wether = df_wether[df_wether['meteostation'] == 'mean'][['date', 'temperature']]
df_wether['date'] = pd.to_datetime(df_wether['date'])
df_wether = df_wether.sort_values(by=['date'])
df_wether['MA'] = df_wether['temperature'].rolling(7).mean()
df_wether['ON'] = (df_wether['MA'] < 8).astype('int')
df_wether = df_wether.drop(columns=['MA'])

df = pd.read_excel('data/6. Плановые-Внеплановые отключения 01.10.2023-30.04.2023.xlsx')
df = df[['УНОМ', 'Фактическая дата отключения', 'Адрес']]
df['Фактическая дата отключения'] = pd.to_datetime(df['Фактическая дата отключения'].apply(lambda x: x.split(' ')[0]))
df_house_encedent = pd.DataFrame(df.groupby('УНОМ').count()['Фактическая дата отключения'])
df_house_encedent_date = pd.DataFrame(df.groupby(['Фактическая дата отключения', 'УНОМ']).count()['Адрес']).reset_index()
df_house_encedent_date = df_house_encedent_date.rename(columns={'Адрес': 'Отключение'})

df_events = pd.read_excel('data/5. Перечень событий за период 01.10.2023-30.04.2023 (ЦУ КГХ)/События за период_01.01.2024-30.04.2024.xlsx', sheet_name='Выгрузка')
df_events_2 = pd.read_excel('data/5. Перечень событий за период 01.10.2023-30.04.2023 (ЦУ КГХ)/События за период_01.10.2023-31.12.2023.xlsx', sheet_name='Выгрузка')
df_events = pd.concat([df_events, df_events_2])
df_events = df_events[df_events['Наименование'] == 'Температура в квартире ниже нормативной']
df_events = df_events[['Дата создания во внешней системе', 'УНОМ', 'Наименование']]
df_events['УНОМ'] = df_events['УНОМ'].astype('int')
df_events['Дата создания во внешней системе'] = pd.to_datetime(df_events['Дата создания во внешней системе'].apply(lambda x: x.split(' ')[0]))
df_events = df_events.groupby(['УНОМ', 'Дата создания во внешней системе']).count().reset_index()

df_ASUPR = pd.read_excel('data/11.Выгрузка_ОДПУ_отопление_ВАО_20240522.xlsx')
df_ASUPR = df_ASUPR[['Адрес', 'UNOM', 'Месяц/Год', 'Объём поданого теплоносителя в систему ЦО', 'Объём обратного теплоносителя из системы ЦО', 'Расход тепловой энергии ', \
                     'Температура подачи', 'Температура обратки', 'Ошибки', 'Наработка часов счётчика', 'Центральное отопление(контур)', 'ID УУ']]
df_ASUPR['Подмес/Утечка'] = df_ASUPR['Объём поданого теплоносителя в систему ЦО'].astype('float') - df_ASUPR['Объём обратного теплоносителя из системы ЦО'].astype('float')
df_ASUPR['Объём поданого теплоносителя в систему ЦО'] = df_ASUPR['Объём поданого теплоносителя в систему ЦО'].astype('float')
df_ASUPR['dT'] = df_ASUPR['Температура подачи'].astype('float') - df_ASUPR['Температура обратки'].astype('float')
df_ASUPR['Температура обратки'] = df_ASUPR['Температура обратки'].astype('float')
df_ASUPR['Месяц/Год'] = pd.to_datetime(df_ASUPR['Месяц/Год'], format="%d-%m-%Y")
df_ASUPR = df_ASUPR.drop(columns=['Объём обратного теплоносителя из системы ЦО'])
df_ASUPR = df_ASUPR.merge(df_wether, left_on='Месяц/Год', right_on='date', how='left')
df_ASUPR = df_ASUPR.drop(columns=['date'])
df_ASUPR['Подмес/Утечка'] = df_ASUPR['Подмес/Утечка'].astype('float')
df_ASUPR['Расход тепловой энергии '] = df_ASUPR['Расход тепловой энергии '].astype('float')
df_ASUPR['Температура подачи'] = df_ASUPR['Температура подачи'].astype('float')
df_ASUPR['Наработка часов счётчика'] = df_ASUPR['Наработка часов счётчика'].astype('float')
df_ASUPR = df_ASUPR.merge(df_events, left_on=['UNOM', 'Месяц/Год'], right_on=['УНОМ', 'Дата создания во внешней системе'], how='left')
df_ASUPR = df_ASUPR.drop(columns=['Дата создания во внешней системе', 'УНОМ'])
df_ASUPR['Наименование'] = df_ASUPR['Наименование'].fillna(0)
df_ASUPR = df_ASUPR.rename(columns={'Наименование': 'Количество жалоб'})
df_ASUPR = df_ASUPR.merge(df_house_encedent_date, left_on=['UNOM', 'Месяц/Год'], right_on=['УНОМ', 'Фактическая дата отключения'], how='left')
df_ASUPR = df_ASUPR.drop(columns=['УНОМ', 'Фактическая дата отключения'])
df_ASUPR['Ошибки'] = df_ASUPR['Ошибки'].astype('str')
df_ASUPR = df_ASUPR.groupby(['UNOM', 'Месяц/Год']).agg({'Объём поданого теплоносителя в систему ЦО':'sum',
                                                                           'Расход тепловой энергии ':'sum',
                                                                           'ID УУ': 'min',
                                                                           'temperature':'mean',
                                                                           'dT': 'mean',
                                                                           'Температура подачи':'mean',
                                                                           'Наработка часов счётчика': 'min',
                                                                           'Центральное отопление(контур)': 'min',
                                                                           'Количество жалоб': 'min',
                                                                           'Отключение': 'min',
                                                                           'Ошибки': lambda x: ','.join([X for X in x if X != 'nan']),
                                                                           'Подмес/Утечка': 'sum',
                                                                           'Адрес': 'min',
                                                                           'Температура обратки': 'mean',
                                                                           'ON': 'min'
                                                                           }).reset_index()
df_ASUPR['Ошибки'] = df_ASUPR['Ошибки'].replace({'': np.nan})
df_ASUPR = df_ASUPR[df_ASUPR['Центральное отопление(контур)'].isin(['ЦО1', 'ЦО2', 'ЦО3', 'ЦО4', 'ТЭ1', 'ТЭ2'])]

errors = list(df_ASUPR['Ошибки'].value_counts().index)
errors_UE = [err for err in errors if 'U' in err or 'E' in err]


df = pd.read_excel('data/14. ВАО_Многоквартирные_дома_с_технико_экономическими_характеристиками.xlsx')
df = df.drop(0)
col_769 = pd.read_excel('data/14. ВАО_Многоквартирные_дома_с_технико_экономическими_характеристиками.xlsx', sheet_name='COL_769')
col_769 = col_769.drop(0)
col_770 = pd.read_excel('data/14. ВАО_Многоквартирные_дома_с_технико_экономическими_характеристиками.xlsx', sheet_name='COL_770')
col_770 = col_770.drop(0)
col_758 = pd.read_excel('data/14. ВАО_Многоквартирные_дома_с_технико_экономическими_характеристиками.xlsx', sheet_name='COL_758')
col_758 = col_758.drop(0)
df['col_770'] = df['col_770'].replace(col_770['Объекты модели - Признак аварийности здания (1182)'].values, col_770['Unnamed: 1'].values)
df['col_769'] = df['col_769'].replace(col_769['Объекты модели - Материалы стен (305)'].values, col_769['Unnamed: 1'].values)
df['col_758'] = df['col_758'].replace(col_758['Объекты модели - Серии проектов (323)'].values, col_758['Unnamed: 1'].values)
df = df[['unom', 'address', 'col_758', 'col_769', 'col_761', 'col_766', 'col_762', 'col_770']]
df = df.rename(columns={'col_758': 'Серии проэктов', 'col_769': 'Стены', 'col_761': 'Квартиры', 'col_766': 'Износ', 'col_762': 'Площадь', 'col_770': 'Аварийность'})
df['Площадь'] = df['Площадь'].astype('float')
df['Квартиры'] = df['Квартиры'].astype('float')
df['Износ'] = df['Износ'].fillna(-1).astype('int')
df_join_adress = pd.read_excel('service/crossaddress_odpu-moek.xlsx')
df_moek = pd.read_excel('data/7. Схема подключений МОЭК.xlsx')
df_moek['Адрес строения'] = df_moek['Адрес строения'].replace(df_join_adress['address2'].values, df_join_adress['address1'].values)
df_moek = df_moek[['Адрес строения', 'Вид ТП', 'Источник теплоснабжения', 'Тип по размещению', 'Номер ТП']]
df_moek = df_moek.merge(df_ASUPR[['UNOM', 'Адрес']], left_on='Адрес строения', right_on='Адрес', how='left').drop(columns=['Адрес строения'])
df = df.merge(df_moek, left_on='unom', right_on='UNOM', how='left').drop(columns=['Адрес', 'UNOM'])
df_iznos = pd.read_excel('service/серии домов и износ.xlsx')
df = df.merge(df_iznos.drop(columns=['alter_address', 'alter_unom']), on='unom', how='left')
df = df.drop_duplicates()
df = df.drop(columns=['Серии проэктов', 'lat', 'lon', 'Площадь', 'total_living_area', 'total_nliving_area', 'Квартиры'])
df['old'] = 2024 - df['year_of_building']
df = df.drop(columns=['year_of_building', 'address', 'Износ', 'Аварийность'])

def interpolate_graph(graph, temp):
    # Интерполяция линейным способом
    return np.interp(temp, [x[0] for x in graph], [x[1] for x in graph])

def determine_graph(df_address):
    min_rmse = float('inf')
    best_graph = None
    best_mae = None
    best_r2 = None

    for graph_name, graph in temp_graphs.items():
        # Интерполяция температурных графиков для всех температур наружного воздуха
        predicted_supply = interpolate_graph(graph['подающий'], df_address['temperature'])
        predicted_return = interpolate_graph(graph['обратный'], df_address['temperature'])

        # Вычисление среднеквадратичной ошибки для подающего и обратного трубопроводов
        rmse_supply = mean_squared_error(df_address['Температура подачи'], predicted_supply, squared=False)
        rmse_return = mean_squared_error(df_address['Температура обратки'], predicted_return, squared=False)

        # Вычисление средней абсолютной ошибки для подающего и обратного трубопроводов
        mae_supply = mean_absolute_error(df_address['Температура подачи'], predicted_supply)
        mae_return = mean_absolute_error(df_address['Температура обратки'], predicted_return)

        # Вычисление R-квадрата для подающего и обратного трубопроводов
        r2_supply = r2_score(df_address['Температура подачи'], predicted_supply)
        r2_return = r2_score(df_address['Температура обратки'], predicted_return)

        # Суммируем ошибки для подающего и обратного трубопроводов
        total_rmse = rmse_supply + rmse_return
        total_mae = mae_supply + mae_return
        avg_r2 = (r2_supply + r2_return) / 2

        # Определяем график с наименьшей ошибкой
        if total_rmse < min_rmse:
            min_rmse = total_rmse
            best_graph = graph_name
            best_mae = total_mae / 2  # Среднее значение MAE для подающего и обратного трубопроводов
            best_r2 = avg_r2  # Среднее значение R-квадрата для подающего и обратного трубопроводов

    return best_graph, min_rmse, best_mae, best_r2

# Получение уникальных адресов
ddf = df_ASUPR[['ID УУ', 'temperature', 'Месяц/Год', 'Температура подачи', 'Температура обратки']].dropna().copy()
addresses = ddf['ID УУ'].unique()

graph_results = []

# Итерация по адресам
for address in addresses:
    df_address = ddf[ddf['ID УУ'] == address]
    graph_result, min_rmse, best_mae, best_r2 = determine_graph(df_address)
    graph_results.append((address, graph_result, min_rmse, best_mae, best_r2))

result_df = pd.DataFrame(graph_results, columns=['ID УУ', 'Температурный график', 'RMSE', 'MAE', 'R-квадрат'])

df_ASUPR = df_ASUPR.merge(result_df[['ID УУ', 'Температурный график']], left_on='ID УУ', right_on='ID УУ', how='left')

def prosentage_temp_delta(row):
    try:
        graff = row['Температурный график']
        T1 = row['Температура подачи']
        T2 = row['Температура обратки']
        T = row['temperature']
        T1_ = interpolate_graph(temp_graphs[graff]['подающий'], T)
        T2_ = interpolate_graph(temp_graphs[graff]['обратный'], T)
        if row['ON'] == 1:
            dT1 = abs(T1 - T1_) / abs(T1)
            if T2 > T2_:
                dT2 = abs(T2 - T2_) / abs(T2)
            else:
                dT2 = 0
        else:
            dT1 = 0
            dT2 = 0
        if dT1 > 0.03:    
            ERR1 = dT1 - 0.03
        else:
            ERR1 = 0
        if dT2 > 0.05:
            ERR2 = dT2 - 0.05
        else:
            ERR2 = 0
        row['ERR1'] = ERR1
        row['ERR2'] = ERR2
    except:
        row['ERR1'] = np.nan
        row['ERR2'] = np.nan
    return row

df_ASUPR = df_ASUPR.apply(prosentage_temp_delta, axis=1)
df_ASUPR['ERR'] = (df_ASUPR['ERR1'] + df_ASUPR['ERR2']) / 2

df_ASUPR_good = df_ASUPR[(~df_ASUPR['Ошибки'].isin(errors_UE)) & (df_ASUPR['Наработка часов счётчика'] >= 23.9) & (df_ASUPR['Температура подачи'] != 0) & (df_ASUPR['ON'] == 1)]
df_ASUPR_good = df_ASUPR_good.merge(df[['unom', 'Номер ТП']], left_on='UNOM', right_on='unom', how='left').drop(columns=['unom'])
df_ASUPR_good['target'] = (df_ASUPR_good['Объём поданого теплоносителя в систему ЦО'] <= 10).astype('int')

dates = sorted(df_ASUPR['Месяц/Год'].unique())
per1, per2 = dates[0: int(len(dates) / 3)], dates[int(len(dates) / 3):]

df1 = df_ASUPR_good[df_ASUPR_good['Месяц/Год'].isin(per1)]
df2 = df_ASUPR_good[df_ASUPR_good['Месяц/Год'].isin(per2)]

df1_x = df1[df1['target'] == 0]
df2_x = df2[df2['target'] == 0]

df1_agg_y = df1.groupby('UNOM').agg({'target': 'max'}).reset_index()
df2_agg_y = df2.groupby('UNOM').agg({'target': 'max'}).reset_index()

df1_agg = df1_x.groupby('UNOM').agg({'Объём поданого теплоносителя в систему ЦО':['mean', 'std', 'median'],
                         'Расход тепловой энергии ': ['mean', 'std', 'median'],
                         'temperature': 'mean',
                         'Центральное отопление(контур)': 'min',
                         'Количество жалоб': 'mean',
                         'Подмес/Утечка': ['mean', 'std'],
                         'ERR': ['mean', 'std'],
                         'ERR1': ['mean', 'std'],
                         'ERR2': ['mean', 'std'],
                         'Номер ТП': 'min',
                         'target': 'max'
                         }).reset_index()

df2_agg = df2_x.groupby('UNOM').agg({'Объём поданого теплоносителя в систему ЦО':['mean', 'std', 'median'],
                         'Расход тепловой энергии ': ['mean', 'std', 'median'],
                         'temperature': 'mean',
                         'Центральное отопление(контур)': 'min',
                         'Количество жалоб': 'mean',
                         'Подмес/Утечка': ['mean', 'std'],
                         'ERR': ['mean', 'std'],
                         'ERR1': ['mean', 'std'],
                         'ERR2': ['mean', 'std'],
                         'Номер ТП': 'min',
                         'target': 'max'
                         }).reset_index()

df1_agg.columns = list(map(lambda x: x[0] + '_' + x[1], df1_agg.columns))
df2_agg.columns = list(map(lambda x: x[0] + '_' + x[1], df2_agg.columns))



df_agg_merged = df2_agg.merge(df, left_on='UNOM_', right_on='unom', how='left').drop(columns=['unom']).dropna(subset=['Объём поданого теплоносителя в систему ЦО_std'])

X_data = df_agg_merged.drop(columns=['Номер ТП_min', 'Номер ТП', 'Вид ТП', 'ERR1_mean', 'ERR1_std', 'ERR2_mean', 'ERR2_std', 'Тип по размещению', 'Источник теплоснабжения',
                                      'Центральное отопление(контур)_min'])

df2_agg_y_ = df2_agg_y.rename(columns={'target': 'target2'})
y_data = df_agg_merged.merge(df2_agg_y_, left_on='UNOM_', right_on='UNOM', how='left')[['UNOM_', 'target2']]

X_data = X_data.merge(y_data, on='UNOM_', how='right')

UNOMS = X_data['UNOM_']
y_data = X_data['target2']
X_data = X_data.drop(columns=['target2', 'UNOM_'])

y_data = y_data.fillna(0)

if False: # Для не линейных моделей
    X_data = X_data.fillna(-100)
else: # Для линейных моделей
    X_data['Расход тепловой энергии _mean'] = X_data['Расход тепловой энергии _mean'].fillna(X_data['predict_wear'].median())
    X_data['Расход тепловой энергии _median'] = X_data['Расход тепловой энергии _median'].fillna(X_data['total_area'].median())
    X_data['predict_wear'] = X_data['predict_wear'].fillna(X_data['predict_wear'].median())
    X_data['total_area'] = X_data['total_area'].fillna(X_data['predict_wear'].median())
    X_data['old'] = X_data['old'].fillna(X_data['predict_wear'].median())

model = pd.read_pickle('service/model_cat.pkl')
scaler = MinMaxScaler()
le = LabelEncoder()
X_data['predict_serie'] = le.fit_transform(X_data['predict_serie'].astype('str'))
le2 = LabelEncoder()
X_data['Стены'] = le2.fit_transform(X_data['Стены'].astype('str'))


def predict():
    y_pred = model.predict_proba(X_data)[:, 1]
    result_df = pd.DataFrame({'UNOM': UNOMS, 'preds': y_pred})
    return pd.concat([result_df, X_data], axis=1)
