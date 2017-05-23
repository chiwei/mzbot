#-*-encoding:utf-8-*-
import sqlite3

def queryOrgByCode(orgCode):
    print(orgCode)
    resultStr=''
    conn = sqlite3.connect('data\orgstd.db')
    c = conn.cursor()
    c.execute('select areacode,areaname,orgcode,orgname,usci,tkmc from orgstd where orgcode=?',[orgCode])
    for row in c:
        if row[0]!=None:
            resultStr ='单位代码：'+orgCode+'\n单位名称：'+row[3]+'   '+'区划代码：'+row[0]+'    '+'区划名称：'+row[1]+'   '+'所在台卡：'+row[5]
        print(resultStr)
    c.close()
    return resultStr

