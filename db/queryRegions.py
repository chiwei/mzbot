#-*-encoding:utf-8-*-
import sqlite3

def queryRegionByCode(regioncode):
    print(regioncode)
    resultStr=""
    conn = sqlite3.connect('data/regionlib.db')
    c = conn.cursor()
    c.execute('select year,region_code,region_name from regionlib where region_code=? order by year desc',[regioncode])
    for row in c:
        if row[0]!= None:
            resultStr+='年份:'+row[0]+'    '+'区划代码：'+row[1]+'    '+'区划名称：'+row[2]+'\n'
    c.close()
    return resultStr

