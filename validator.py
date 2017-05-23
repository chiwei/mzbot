import math

#####USCC
checklist ='0123456789ABCDEFGHJKLMNPQRTUWXY0'

##### barcode 9
checklistBarcode='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
barcodePow=[3,7,9,10,5,8,4,2]
barcodeCheckbit = [0,1,2,3,4,5,6,7,8,9,'X',0]

def validator(usci):
    result=''
    if len(usci)!=18:
        return
    elif len(usci)==18:
        v_sum=0
        for i in range(1,18):
            v_sum = v_sum+checklist.index(usci[i-1])*(pow(3,i-1)%31)
        checkbit = 31-v_sum%31
        result=usci[0:17]+str(checklist[checkbit])
        if result == usci:
            return True
        else:
            return False
    else:
        return False

def validatorBarcode(barcode):
    result = ''
    if len(barcode) !=9:
        return
    elif len(barcode) == 9:
        v_sum = 0
        for i in range(1,9):
            v_sum = v_sum+checklistBarcode.index(barcode[i-1])*barcodePow[i-1]
        checkbit = 11 - v_sum%11
        result = barcode[0:8]+str(barcodeCheckbit[checkbit])
        if result == barcode:
            return True
        else:
            return False
    else:
        return False



