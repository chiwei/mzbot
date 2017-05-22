import math

checklist ='0123456789ABCDEFGHJKLMNPQRTUWXY0'

def validator(usci):
    result=''
    if len(usci)!=18:
        return
    elif len(usci)==18:
        v_sum=0
        for i in range(1,18):
            v_sum = v_sum+checklist.index(usci[i-1])*(pow(3,i-1)%31)
            print(v_sum)
        checkbit = 31-v_sum%31
        print(checklist[checkbit])
        result=usci[0:17]+str(checklist[checkbit])
    return result
