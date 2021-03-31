import tkinter as tk
from tkinter import ttk, Menu, Toplevel, StringVar
from tkinter.messagebox import showinfo, showwarning, askyesno
from time import time
from clase_Estudiometro import *
import datetime
import sqlite3


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