#-*-encoding:utf-8-*-
import sqlite3

def queryOrgByCode(orgCode):
    print(orgCode)
    resultStr=''
    conn = sqlite3.connect('data\orgstd.db')
    c = conn.cursor()
    c.execute('select areacode,areaname,orgcode,orgname,usci,tkmc from orgstd where orgcode=?',[orgCode])
    for row in c:
        rAreacode = row[0]
        rAreaname = row[1]
        rOrgname = row[3]
        rUsci = row[4]
        rTkmc = row[5]
        if row[0]!=None:
            resultStr ='单位代码：'+orgCode+'\n'+'查询结果：\n'+'单位名称：'+row[3]+'   '+'区划代码：'+row[0]+'    '+'区划名称：'+row[1]+'   '+'所在台卡：'+row[5]
        else:
            resultStr ='单位代码：'+orgCode+'\n'+'查询结果：无此单位！'
        print(resultStr)
    c.close()
    return resultStr

