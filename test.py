import sqlite3 

from sqlite3 import Error


def sql_connection():

    try:

        con = sqlite3.connect('parametros.db')

        return con

    except Error:

        print(Error)


def sql_table(con):

    cursorObj = con.cursor()

    cursorObj.execute("CREATE TABLE PARAMETROS (PARAMETRO VARCHAR(15), VALOR INTEGER)")
    
    cursorObj.execute("INSERT INTO PARAMETROS VALUES('Iteración', 1500)")
    cursorObj.execute("INSERT INTO PARAMETROS VALUES('Descanso corto', 300)")
    cursorObj.execute("INSERT INTO PARAMETROS VALUES('Descanso largo', 1800)")

    con.commit()


def sql_searchfromvar(var):

    cursorObj = con.cursor()

    cursorObj.execute('SELECT VALOR FROM PARAMETROS WHERE PARAMETRO=?', (var,))
    tupla = cursorObj.fetchall()
    return tupla[0][0]

def dar_valor():
    return '5'

def sql_updatevar(parametro):

    cursorObj = con.cursor()

    cursorObj.execute('UPDATE PARAMETROS SET VALOR = ? WHERE PARAMETRO = ?', (int(dar_valor())*60, 'Descanso corto',))

con = sql_connection()

#sql_table(con)
#sql_updatevar('Descanso corto')
print(sql_searchfromvar('Descanso corto'))

duraciones = ['Iteración', 'Descanso corto', 'Descanso largo']
for i in range(len(duraciones)):
    duraciones.insert([i])




print("Terminado.")

