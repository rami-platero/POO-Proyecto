from datetime import datetime

def validateForm(request_form, lista):
    for field in lista:
        if field not in request_form:
            raise ValueError
        if not str(request_form[field]).strip():
            raise ValueError

def parseToDate(data: str, format='%Y-%m-%d'):
    return datetime.strptime(data, format).date()