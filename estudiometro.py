import tkinter as tk
from tkinter import ttk, Menu, Toplevel, StringVar
from tkinter.messagebox import showinfo, showwarning, askyesno
from time import time
import datetime
import sqlite3


def tiempo_actual():
    """
    tiempo_actual() -> integer
    \n
    Devuelve el tiempo actual como integer mediante el redondeo de "time()".
    """
    return round(time())


class Estudiometro(tk.Frame): 
    
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.tiempo = 0
        self.recursiones = 1
        self.forzar_tiempo = 'no'
        
        self.conexion = sqlite3.connect('parametros.db')
        self.cursor = self.conexion.cursor()
        self.duraciones = self.crear_duracion()

        self.pack()
        self.crear_widgets()


    def crear_duracion(self):
        """
        El módulo responsable de retornar el tipo de dato pivotal para la aplicación. Es una tupla de listas,
        en la clase maestra tiene 3 listas distintas de 2 valores cada una. El primer valor es el string que 
        nombra al segundo valor, siendo éste último el tiempo límite que tiene que durar. Este tiempo límite
        es tomado directamente de la base de datos asociada a la aplicación mediante "retornar_tiempo_bdd(*)".
        \n
        Ejemplo: ['Iteración', 1500], ['Descanso corto', 300], ['Descanso largo', 1800]
        """
        tupla = ['Iteración'], ['Descanso corto'], ['Descanso largo']
        for i, v in enumerate(tupla):
            v.append(self.retornar_tiempo_bdd(v[0]))
        return tupla
        

    def retornar_tiempo_bdd(self, parametro):
        """
        Toma un string que buscará en la base de datos, para retornar el valor integer 
        asociado a ese string.
        \n
        Haciendo uso de la base de datos, podemos retornar los valores almacenados en
        la base de datos, para que el usuario no deba ingresar sus preferencias cada
        vez que abre el programa nuevamente.
        """
        self.cursor.execute('SELECT VALOR FROM PARAMETROS WHERE PARAMETRO=?', (parametro,))
        tupla = self.cursor.fetchall()
        return tupla[0][0]


    def crear_widgets(self): 
        """
        Este módulo crea todos los elementos visuales de Tkinter, que serán actualizados
        posteriormente por el módulo contador(*) y la clase Editor.
        """
        # Creando los botones y labels con sus respectivos command
        self.but_empezar = tk.Button(self, text="¡Comenzar estudio!\nTécnica Pomodoro",
                            width="40", font="'calibri', 11", command = self.comenzar)

        self.but_resumir = tk.Button(self, text="Resumir estudio", width="15",
                            font="'calibri', 10", state="disabled", command=self.resumir) #lambda: self.forzar_tiempo = 'resumir')

        self.lab_contador_tiempo = tk.Label(self, text="0:00:00", 
                            font = ('calibri', 30, 'bold'))

        self.lab_recursiones = tk.Label(self, text="Ronda Nº:", font = ('calibri', 8))

        self.lab_contador_recursiones = tk.Label(self, text=self.recursiones)
        
        self.but_salir = tk.Button(self, text="SALIR", fg="red", width="15", font = ('calibri', 11),
                            command=self.master.destroy)

        self.but_empezar.grid(row = 3, column = 0, columnspan = 2, padx = 6, pady = 5)
        self.but_salir.grid(row = 4, column = 1, padx = 10, pady = 7)
        self.but_resumir.grid(row = 4, column = 0, padx = 10, pady = 7)
        self.lab_contador_tiempo.grid(row = 0, column = 0, columnspan = 2, rowspan = 1, padx = 8, pady = 4)
        self.lab_recursiones.grid(row = 1, column = 0, columnspan = 2, padx = 8, pady = 0)
        self.lab_contador_recursiones.grid(row = 2, column = 0, columnspan = 2, padx = 8, pady = 1)

        # Creando las barras de menú y su contenido
        self.menu_barra = Menu(root)
        root.config(menu=self.menu_barra)

        self.menu_archivo = Menu(self.menu_barra, tearoff=0)
        self.menu_barra.add_cascade(label="Menú", menu=self.menu_archivo)
        self.menu_archivo.add_command(label="Editar intervalos", command= self.abrir_editor)
        self.menu_archivo.add_separator()
        self.menu_archivo.add_command(label="Salir", command= self.master.destroy)
        
        self.menu_ayuda = Menu(self.menu_barra, tearoff=0)
        self.menu_barra.add_cascade(label="Ayuda", menu=self.menu_ayuda)
        self.menu_ayuda.add_command(label="Guía de uso", command = lambda: showinfo(title="Guía", 
message="""Este programa se encarga de mantener un conteo estable por una cantidad de minutos determinada por la técnica Pomodoro.
Al terminar cada lapso, se enviará una notificación desde el programa para continuar a la siguiente etapa, y así sucesivamente hasta que decida finalizar su tarea.
\nPuede editar los minutos de cada lapso de tiempo en el Menú, lo cual reiniciará el conteo y las rondas. 
Sus preferencias permanecerán al reabrir el programa."""))
        self.menu_ayuda.add_command(label="Licencia", command = lambda: showinfo(title="Licencia", 
                                    message="Programación y gráficos por Franco J. Pino.\nHecho con Python 3 (VSCode) y Aseprite."))


    def abrir_editor(self):
        """
        Módulo que se encarga de deshabilitar la opción de la barra menú de donde se abrió, 
        para posteriormente ejecutar la clase Editor.
        """
        self.menu_archivo.entryconfig("Editar intervalos", state="disabled")
        Editor(self.master)


    def comenzar(self):
        """
        Módulo encargado de dar comienzo al módulo recursivo contador(*). Adicionalmente, deshabilita
        el botón que le da comienzo al conteo del programa.
        \n
        Este módulo también es llamado por contador(*) cuando se busca reiniciar el reloj.
        """
        self.but_empezar["state"] = "disabled"
        self.contador(self.duraciones[0][1], tiempo_actual(), 'contando')


    def contador(self, limite, inicio, fase):
        """
        Módulo recursivo. Ejecuta una serie de condiciones a medida que se llama a sí misma cada 1000 ms.\n

        limite -> Cantidad de segundos por la que el módulo contará (int).\n
        inicio -> Tiempo actual en que el módulo fue llamado (int).\n
        fase -> La fase en la que se encuentra el módulo, funciona como flag. Acepta 'contando' y 'descansando'. 
        Cuando fase es 'contando', es porque se está contando actualmente en una iteración. Cuando es 
        'descansando', es porque se está contando un descanso, sea corto o largo.
        """
        if self.forzar_tiempo == 'no': 
            self.tiempo = tiempo_actual() - inicio
            self.lab_contador_tiempo["text"] = datetime.timedelta(seconds=self.tiempo)

        elif self.forzar_tiempo == 'resumir':
            self.lab_contador_tiempo["text"] = datetime.timedelta(seconds=self.tiempo+1)
            self.tiempo = limite
            #self.forzar_tiempo = 'no'

        elif self.forzar_tiempo == 'reiniciar':
            self.reiniciar_reloj('resetear') 
            self.comenzar()
            return
            

        if self.tiempo >= limite and self.recursiones <= 3:
            if fase == 'contando':
                showinfo(title="Comienza descanso", message="¡Ha terminado! Acepte para tomar su descanso corto.")
                self.reiniciar_reloj('descanso')
                self.contador(self.duraciones[1][1], tiempo_actual(), 'descansando')
                return
            elif fase == 'descansando':
                showwarning(title="Terminó el descanso", message="¡Fin del descanso! Acepte para seguir estudiando.")
                self.reiniciar_reloj('iterar')
                self.contador(self.duraciones[0][1], tiempo_actual(), 'contando')
                return

        elif self.tiempo >= limite and self.recursiones >= 4:
            if fase == 'contando':
                showinfo(title="Comienza descanso largo", message="¡Descanso largo! Acepte para tomar su descanso largo. A la mitad del tiempo, ya podrá resumir su estudio.")
                self.reiniciar_reloj('descanso')
                self.contador(self.duraciones[2][1], tiempo_actual(), 'descansando')
                return
            elif fase == 'descansando':
                showwarning(title="Fin del descanso largo", message= "Terminó el descanso largo, ¡de vuelta al estudio!")
                self.reiniciar_reloj('resetear')
                self.but_resumir["state"] = "disabled"
                self.contador(self.duraciones[0][1], tiempo_actual(), 'contando')
                return

        if self. tiempo >= self.duraciones[2][1]/2 and self.recursiones >= 4 and fase == 'descansando':
            self.but_resumir["state"] = "active"

        self.lab_contador_tiempo.after(1000, self.contador, limite, inicio, fase)


    def reiniciar_reloj(self, iteracion):
        """
        Reinicia el reloj y refresca los labels contadores de Estudiometro: tiempo y recursiones. Toma
        un valor string que determina comportamiento adicional.
        \n
        iteracion -> Acepta 'iterar' y 'resetear' 'iterar' provoca que, además, las recursiones aumenten 
        en 1. 'resetear' causa que las recursiones vuelvan a 1, además de refrescar el forzado de tiempo 
        para que deje de hacerlo.
        """
        self.tiempo = 0
        if iteracion == 'iterar':
            self.recursiones += 1
        elif iteracion == 'resetear':
            self.recursiones = 1
            self.forzar_tiempo = 'no'
        self.lab_contador_tiempo["text"] = datetime.timedelta(seconds=self.tiempo)
        self.lab_contador_recursiones["text"] = self.recursiones
        return

 
    def resumir(self):
        """
        Módulo llamado mediante el botón de resumir, que puede ser presionado una vez se llegue
        a la mitad del intervalo de descanso largo. Provoca que contador(*) iguale el tiempo
        al límite, automáticamente pasando a la siguiente fase (en este caso, una iteración).
        """
        self.forzar_tiempo = 'resumir'
        return


class Editor(Toplevel, tk.Frame):
    """
    La clase Editor se abre desde la barra de menú, y crea una ventana nueva donde es posible editar los valores
    de la clase Estudiometro.
    """
    def __init__(self, master=None):
        super().__init__(master=master)
        self.resizable(width=False, height=False)
        self.protocol('WM_DELETE_WINDOW', self.__Cancel)
        self.title("Editor")
        self.iconbitmap("Estudiometro.ico")
        self.attributes("-topmost", True)
        self.crear_widgets()


    def __Cancel(self, event=None):
        """
        Invocado cuando el usuario intenta cerrar la ventana Editor mediante la X. Pregunta por
        confirmación; de ser otorgada, cerrará la ventana.
        """
        if askyesno(message="Está a punto de cerrar sin guardar sus cambios, ¿desea volver de todas formas?"
                    , title="Confirmar"):
            app.menu_archivo.entryconfig("Editar intervalos", state="active")
            self.destroy()
        else:
            pass


    def crear_widgets(self):
        """
        Creación de todos los widgets dentro de la nueva ventana Editor.
        """
        self.editor_duraciones = app.crear_duracion()
        self.lab_duracion = tk.Label(self, text="Duración", font="'calibri', 13")
        self.but_guardar = tk.Button(self, text="Guardar cambios", command=self.guardar)
        self.but_por_defecto = tk.Button(self, text="Por defecto", command=self.por_defecto)
        self.vcmd = (self.register(self.callback))
        self.largo_texto = []
        
        # Este For crea cada Label y Entry a partir del contenido de la tupla "editor_duraciones".
        # Además, formatea los Entry para que sólo acepten números y queden en dos dígitos máximo.
        for i, v in enumerate(self.editor_duraciones):
            self.largo_texto.append(StringVar())
            lab = tk.Label(self, justify=tk.LEFT, 
                            text = v[0] + ":", anchor='w')
            ent = tk.Entry(self, validate='all', validatecommand=(self.vcmd, '%P'), 
                           width=5, justify=tk.CENTER, textvariable=self.largo_texto[i])
            lab.grid(row=i+1, column=0, pady=2, padx=8)
            ent.grid(row=i+1, column=1, pady=2, padx=8)
            ent.insert(0, round(v[1]/60))            
            v.append(ent)
            self.largo_texto[i].trace('w', self.limitar_texto)

        self.lab_duracion.grid(row=0, column=0, columnspan=2, pady=2, padx=5)
        self.but_guardar.grid(row=4,column=1, pady=2, padx=2)
        self.but_por_defecto.grid(row=4, column=0, pady=2, padx=2)


    def callback(self, P):
        """
        Comprueba que el valor ingresado sea un número.
        """
        if str.isdigit(P) or P == "":
            return True
        else:
            return False

    def limitar_texto(self, *args):
        """
        Condice el texto en los Entry a permanecer en los dos dígitos.
        """
        for i, v in enumerate(self.editor_duraciones):
            valor = v[2].get()
            if len(valor) > 3: self.largo_texto[i].set(valor[:3])


    def guardar(self):
        """
        Este módulo se encarga de tomar los valores ingresados (en minutos) en los entry, convertirlos 
        en segundos, y enviarlos a la BDD, para después retornarlos y asignarlos a la lista.
        """
        for i, v in enumerate(self.editor_duraciones):
            if v[2].get() != "":
                if int(v[2].get()) > 0:
                    app.cursor.execute('UPDATE PARAMETROS SET VALOR = ? WHERE PARAMETRO = ?', 
                                      (int(v[2].get())*60, v[0],))
                    app.duraciones[i][1] = app.retornar_tiempo_bdd(v[0])
                else:
                    showwarning(title="Inválido", message="Los valores deben ser mayores a cero.")
                    return
            else:
                showwarning(title="Inválido", message="Los valores no deben ser nulos.")
                return

        app.conexion.commit()
        
        app.menu_archivo.entryconfig("Editar intervalos", state="active")
        showinfo(title="Cambios guardados", message="Sus cambios han sido aplicados.\nEl reloj se reiniciará.")
        app.forzar_tiempo = 'reiniciar'

        self.destroy()


    def por_defecto(self):
        """
        Este módulo reinicia los valores dentro de los entries, volviéndolos aquellos por default (25, 5, 30).
        """
        for i, v in enumerate(self.editor_duraciones): v[2].delete(0, tk.END)
        self.editor_duraciones[0][2].insert(0, 25)
        self.editor_duraciones[1][2].insert(0, 5)
        self.editor_duraciones[2][2].insert(0, 30)


if __name__ == '__main__':
    root = tk.Tk()
    root.resizable(width=False, height=False)
    root.title("Estudiómetro")
    root.iconbitmap("Estudiometro.ico")
    root.lift()
    app = Estudiometro(master=root)
    app.mainloop()