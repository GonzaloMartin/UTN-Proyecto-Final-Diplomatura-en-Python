import re
import sqlite3
import tkinter as tk
import datetime
import locale
import matplotlib.pyplot as plt

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from tkinter import Tk, Frame

from tkinter import *
from tkinter import ttk
from tkinter.messagebox import *
from tkcalendar import DateEntry

from PIL import Image as PilImage, ImageTk



#-----------------------------INICIO CONTROLADOR-----------------------------#

def actualizar_estado_bar(mensaje): 
    estado.config(text=mensaje)  # Actualiza texto del label
    root.update_idletasks()  # Fuerza la actualización de UI


def actualizar_estado_fecha():
    if var_check_vencimiento.get():
        e_vencimiento.config(state='disabled')
    else:
        e_vencimiento.config(state='normal')


def validar_campos():
    campos_var = [var_producto,
                  var_cantidad,
                  var_monto,
                  var_proveedor,
                  var_fecha,
                  var_vencimiento]
    campos_cb = [cb_responsable, cb_rubro, cb_medio_pago]
    
    for var in campos_var:
        if (type(var) == str or type(var) == int) and not var:
            return False

    for cb in campos_cb:
        if not cb:
            return False

    return True


def limpiar_formulario():
    var_monto.set('')
    var_producto.set('')
    var_cantidad.set('')
    var_proveedor.set('')
    var_responsable.set('')
    var_rubro.set('')
    var_medio_pago.set('')
    cb_responsable.set('')
    cb_rubro.set('')
    cb_medio_pago.set('')

    
def preparar_alta():
    boton_confirmar.config(state='normal', command=alta)
    boton_cancelar.config(state='normal')


def preparar_baja():
    boton_confirmar.config(state='normal', command=baja)
    boton_cancelar.config(state='normal')


def confirmar():
    # La acción se define en cada caso (alta, baja, modificacion)
    boton_confirmar.config(state='disabled')
    boton_cancelar.config(state='disabled')


def cancelar():
    boton_confirmar.config(state='disabled', command=None)
    boton_cancelar.config(state='disabled')
    limpiar_formulario()
    
    
def aplicar_modificacion(compra_id, id_bd):
    
    if not validar_campos():
        actualizar_estado_bar("Todos los campos deben estar llenos.")
        showinfo("Info", "Todos los campos deben estar llenos.")
        cancelar()
        return

    nuevo_valor = {
        'producto': var_producto.get(),
        'cantidad': int(var_cantidad.get()),
        'monto': float(var_monto.get()),
        'responsable': cb_responsable.get(),
        'rubro': cb_rubro.get(),
        'proveedor': var_proveedor.get(),
        'medio_pago': cb_medio_pago.get(),
        'fecha': var_fecha.get(),
        'vencimiento': var_vencimiento.get()
    }

    modificacion_bd(id_bd, nuevo_valor)

    if tree.exists(compra_id):
        tree.item(compra_id, values=(
            nuevo_valor['producto'],
            nuevo_valor['cantidad'],
            nuevo_valor['monto'],
            nuevo_valor['responsable'],
            nuevo_valor['monto'] * nuevo_valor['cantidad'], # Subtotal
            nuevo_valor['rubro'],
            nuevo_valor['proveedor'],
            nuevo_valor['medio_pago'],
            nuevo_valor['fecha'],
            nuevo_valor['vencimiento']
        ))

    actualizar_estado_bar("Registro modificado con ID: " + str(id_bd))
    cargar_total_acumulado()
    limpiar_formulario()
    confirmar()


def cargar_datos_en_treeview():
    registros = consulta_bd()
    for row in registros:
        tree.insert('', 'end', text=str(row[0]), values=row[1:])

def obtener_mes_actual():
    return datetime.datetime.now().month

def obtener_mes_palabra_actual():
    locale.setlocale(locale.LC_TIME, '')  # Para que devuelva el mes en español
    mes_actual = obtener_mes_actual()
    mes_actual_str = datetime.datetime.strptime(str(mes_actual), "%m").strftime("%B")
    return mes_actual_str.capitalize()

def obtener_total_acumulado():
    mes_actual = obtener_mes_actual()
    registros = consulta_bd(mes=mes_actual)
    
    total_acumulado = 0
    for row in registros:
        total_acumulado += row[0]
        
    return total_acumulado

def cargar_total_acumulado():
    total_acumulado = obtener_total_acumulado()
    var_total.set(f"$ {total_acumulado:.2f}")
    return total_acumulado

def actualizar_label_total_acumulado():
    mes_actual_str = obtener_mes_palabra_actual()
    l_total.config(text=f"Total {mes_actual_str}:")
    
#-------------------------------FIN CONTROLADOR------------------------------#

##############################################################################

#--------------------------------INICIO MODELO-------------------------------#

#-----ABMC-----#
def alta():
    total_acumulado = cargar_total_acumulado()
    
    var_fecha.set(cal_fecha.get_date().strftime("%Y-%m-%d"))
    if var_check_vencimiento.get():
        vencimiento_value = 'N/A'
    else:
        vencimiento_value = e_vencimiento.get_date().strftime("%Y-%m-%d")

    var_vencimiento.set(vencimiento_value)

    if not var_producto.get() or not var_cantidad.get() or not var_monto.get() or not cb_responsable.get():
        actualizar_estado_bar("Se deben completar todos los campos de ingreso")
        showinfo("Info", "Se deben completar todos los campos de ingreso")
        cancelar()
        return

    valores = {
        'monto': float(var_monto.get()),
        'producto': var_producto.get(),
        'rubro': cb_rubro.get(),
        'fecha': cal_fecha.get_date().strftime("%Y-%m-%d"),
        'proveedor': var_proveedor.get(),
        'medio_pago': cb_medio_pago.get(),
        'responsable': cb_responsable.get(),
        'cantidad': int(var_cantidad.get()),
        'vencimiento': vencimiento_value
    }

    for valor in valores.values():
        if not valor:
            showinfo("Info", "Todos los campos de alta deben tener contenido.")
            actualizar_estado_bar("Todos los campos de alta deben tener contenido.")
            cancelar()
            return
        
    conn = conectar_base_de_datos()
    ultimo_id = alta_bd(conn, valores)

    subtotal_acumulado = round(valores['cantidad'] * valores['monto'], 2)

    tree.insert('',
                'end',
                text=str(ultimo_id),
                values=(valores['producto'],
                        valores['cantidad'],
                        valores['monto'],
                        valores['responsable'],
                        f"{subtotal_acumulado:.2f}",
                        valores['rubro'],
                        valores['proveedor'],
                        valores['medio_pago'],
                        valores['fecha'],
                        valores['vencimiento']))

    cargar_total_acumulado()
    actualizar_estado_bar("Se dio de alta el registro con ID: " + str(ultimo_id))
    limpiar_formulario()
    confirmar()


def baja():
    total_acumulado = cargar_total_acumulado()
    
    compra_id = tree.focus()
    if not compra_id:
        showinfo("Info", "Debe seleccionar un registro para dar de Baja.")
        actualizar_estado_bar("Debe seleccionar un registro para dar de Baja.")
        cancelar()
        return
    
    valores = tree.item(compra_id, 'values')

    subtotal_str = valores[4]

    if re.match(r'^\d+(\.\d+)?$', subtotal_str): # Enteros >= 0 y decimales >= 0
        subtotal_eliminar = float(subtotal_str)
    else:
        showinfo("Error", "El subtotal no es un número válido.")
        actualizar_estado_bar("El subtotal no es un número válido.")
        cancelar()
        return

    id_bd_str = tree.item(compra_id, 'text')

    if re.match(r'^\d+$', id_bd_str): # Enteros >= 0
        id_bd = int(id_bd_str)
    else:
        showinfo("Error",  "El ID no es un número válido.")
        actualizar_estado_bar("El ID no es un número válido.")
        cancelar()
        return

    baja_bd(id_bd)
    
    cargar_total_acumulado()
    tree.delete(compra_id)
    
    actualizar_estado_bar("Se dio de baja el registro con ID: " + str(id_bd))
    confirmar()
    
    
def modificacion():
    compra_id = tree.focus()
    if not compra_id:
        showinfo("Info", "Debe seleccionar un registro para Modificar.")
        actualizar_estado_bar("Debe seleccionar un registro para Modificar.")
        cancelar()
        return
    
    id_bd = int(tree.item(compra_id, 'text'))
    
    valores = tree.item(compra_id, 'values')
    var_producto.set(valores[0])
    var_cantidad.set(valores[1])
    var_monto.set(valores[2])
    var_fecha.set(valores[8])
    cb_responsable.set(valores[3])
    cb_rubro.set(valores[5])
    cb_medio_pago.set(valores[7])
    var_proveedor.set(valores[6])
    var_vencimiento.set(valores[9])
    
    actualizar_estado_bar("Modificando registro ID: " + str(id_bd))
    
    boton_confirmar.config(state='normal', command=lambda: aplicar_modificacion(compra_id, id_bd))
    boton_cancelar.config(state='normal')


def consulta():
    termino_busqueda = var_consulta.get()
    # Si término_busqueda contiene "*", se muestran todos los registros
    if "*" in termino_busqueda: termino_busqueda = ""
    
    registros = consulta_bd()

    # Crea objeto regex desde 'termino_busqueda' NO sensible a mayúsculas
    regex = re.compile(termino_busqueda, re.IGNORECASE) 

    registros_filtrados = []
    for row in registros:
        row_str = ' '.join(map(str, row))  # Registro -> cadena
        if regex.search(row_str):
            registros_filtrados.append(row)

    for i in tree.get_children():
        tree.delete(i)

    for row in registros_filtrados:
        tree.insert('', 'end', text=str(row[0]), values=row[1:])

    if termino_busqueda == "": # Si no se especifica un término de búsqueda
        actualizar_estado_bar(f"Se muestran todos los registros.")
    else:
        actualizar_estado_bar(f"Resultados de la búsqueda para: {termino_busqueda}")

    cargar_total_acumulado()
#-----FIN ABMC-----#

#-----BASE DE DATOS-----#
def conectar_base_de_datos():
    conn = sqlite3.connect('BD/base_de_datos.db')
    return conn


def desconectar_base_de_datos(conn):
    conn.close()


def crear_tabla(conn):
    cursor = conn.cursor()
    query = """CREATE TABLE IF NOT EXISTS gastos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            producto_servicio TEXT,
            cantidad INTEGER,
            monto FLOAT,
            responsable TEXT,
            subtotal FLOAT,
            rubro TEXT,
            proveedor TEXT,
            medio_de_pago TEXT,
            fecha DATE,
            vencimiento DATE
            );"""
    cursor.execute(query)
    conn.commit()


def alta_bd(conn, valores):
    conn = conectar_base_de_datos()
    cursor = conn.cursor()

    query = """INSERT INTO gastos (producto_servicio,
            cantidad,
            monto,
            responsable,
            subtotal,
            rubro, proveedor,
            medio_de_pago,
            fecha,
            vencimiento)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""
               
    subtotal = valores['cantidad'] * valores['monto']
    
    data = (valores['producto'], 
            valores['cantidad'], 
            valores['monto'], 
            valores['responsable'], 
            subtotal, valores['rubro'], 
            valores['proveedor'], 
            valores['medio_pago'], 
            valores['fecha'], 
            valores['vencimiento'])

    cursor.execute(query, data)
    conn.commit()
    ultimo_id = cursor.lastrowid 
    desconectar_base_de_datos(conn)
    return ultimo_id
    

def baja_bd(id_registro):
    conn = conectar_base_de_datos()
    cursor = conn.cursor()
    query = "DELETE FROM gastos WHERE id = ?;"
    cursor.execute(query, (id_registro,))
    conn.commit()
    desconectar_base_de_datos(conn)


def modificacion_bd(id_registro, valores):
    conn = conectar_base_de_datos()
    cursor = conn.cursor()
    query = """UPDATE gastos SET
            producto_servicio = ?,
            cantidad = ?,
            monto = ?,
            responsable = ?,
            subtotal = ?,
            rubro = ?,
            proveedor = ?,
            medio_de_pago = ?,
            fecha = ?,
            vencimiento = ?
            WHERE id = ?;"""

    subtotal = int(valores['cantidad'] * valores['monto'] * 100) / 100.0
    data = (valores['producto'],
            valores['cantidad'],
            valores['monto'],
            valores['responsable'],
            subtotal, valores['rubro'],
            valores['proveedor'],
            valores['medio_pago'],
            valores['fecha'],
            valores['vencimiento'],
            id_registro)

    cursor.execute(query, data)
    conn.commit()
    desconectar_base_de_datos(conn)

    
def consulta_bd(mes=None):
    # Consulta todos los registros. Pero si se especifica 1 mes, filtra por mes
    conn = conectar_base_de_datos()
    cursor = conn.cursor()
    if mes is not None:
        query = "SELECT subtotal FROM gastos WHERE strftime('%m', fecha) = ?;"
        cursor.execute(query, (f"{mes:02d}",))
    else:
        query = """SELECT * FROM gastos;"""
        cursor.execute(query)
    rows = cursor.fetchall()
    desconectar_base_de_datos(conn)
    return rows


conn = conectar_base_de_datos()
crear_tabla(conn)
#-----FIN BASE DE DATOS-----#

#-----GRAFICO (DATOS)-----#
def get_data_for_graph():
    conn = conectar_base_de_datos()
    cursor = conn.cursor()
    cursor.execute("SELECT rubro, SUM(subtotal) FROM gastos GROUP BY rubro")
    data = cursor.fetchall()
    num_mes_actual = str(obtener_mes_actual())
    mes_palabra = obtener_mes_palabra_actual()
    desconectar_base_de_datos(conn)
    return data
#-----FIN GRAFICO (DATOS)-----#

#---------------------------------FIN MODELO---------------------------------#

##############################################################################

#--------------------------------INICIO VISTA--------------------------------#

root = Tk()
root.grid_rowconfigure(12, weight=1)
root.title('Gestor de compras')
root.geometry('1600x900')     # Tamaño de la ventana standard notebook 14'
# screen_ancho = root.winfo_screenwidth()
# screen_alto = root.winfo_screenheight() - 75
# root.geometry(f'{screen_ancho}x{screen_alto}')
# root.resizable(False, False)  # Para que no se pueda redimensionar la ventana

#-----FRAMES-----#
frame_formulario = LabelFrame(root, text="Ingreso de datos", padx=10, pady=10)
frame_formulario.grid(row=2, column=0, columnspan=2, rowspan=6, padx=10,
                      pady=10, sticky="we")

frame_estado = Frame(root, borderwidth=1, relief="solid")
frame_estado.grid(row=0, column=2, padx=0, pady=10, columnspan=3)

frame_treeview = Frame(root)
frame_treeview.grid(row=12, column=0, columnspan=11, padx=10, pady=10,
                    sticky='nsew')
frame_treeview.grid_rowconfigure(0, weight=1)
frame_treeview.grid_columnconfigure(0, weight=1)

frame_grafico = Frame(root, borderwidth=1, relief="solid")
frame_grafico.grid(row=2, column=3, rowspan=9, padx=10, pady=0, sticky='nsew')
#-----FIN FRAMES-----#

var_id = IntVar()
var_producto = StringVar()
var_cantidad = IntVar()
var_monto = StringVar()
var_responsable = StringVar()
var_subtotal = StringVar()
var_total = StringVar()
var_rubro = StringVar()
var_proveedor = StringVar()
var_medio_pago = StringVar()
var_fecha = StringVar()
var_vencimiento = StringVar()
var_check_vencimiento = BooleanVar()
var_consulta = StringVar()

variables_a_validar = [var_producto,
                       var_cantidad,
                       var_monto,
                       var_responsable,
                       var_proveedor,
                       var_medio_pago,
                       var_rubro, var_fecha, 
                       var_vencimiento]

opciones_rubro = ["Mantenimiento", "Impuestos", "Servicios",
                  "Mercado", "Limpieza", "Colegio", "Otros"]

opciones_medio_pago = ["Efectivo", "Billetera virtual",
                       "Cheque", "Tarjeta de Crédito",
                       "Tarjeta de Débito", "Transferencia", "Otro"]

opciones_responsable = ["Gonzalo", "Matías", "Juan"]

#-----WIDGETS-----#

#-----HEADER-----#
imagen_original = PilImage.open("imgs/python_logo_tn.png")
imagen_resize = imagen_original.resize((50, 50))
foto = ImageTk.PhotoImage(imagen_resize)
img = Label(root, image=foto)
img.grid(row=0, column=0, padx=10, pady=5, sticky=E)

title = Label(root, text='GESTOR DE COMPRAS PYTHON',
              font = ('Arial', 20, 'bold'))
title.grid(row=0, column=1, sticky=W)
#-----FIN HEADER-----#

#-----ESTADO-----#
estado = Label(frame_estado, text="Bienvenido.", font=('Arial', 10),
               width=50, anchor=W)
estado.grid(row=0, column=0, sticky=W, padx=0, pady=0)
#-----FIN ESTADO-----#

#-----FORMULARIO-----#
we_ancho = 30
wcb_ancho = we_ancho - 2
l_producto = Label(frame_formulario, text='Producto:')
l_producto.grid(row=2, column=0, sticky=W)
e_producto = Entry(frame_formulario, textvariable=var_producto, width=we_ancho)
e_producto.grid(row=3, column=0, sticky='w', pady=5)

l_cantidad = Label(frame_formulario, text='Cantidad:')
l_cantidad.grid(row=2, column=1, sticky=W, padx=10)
e_cantidad = Entry(frame_formulario, textvariable=var_cantidad, width=we_ancho)
e_cantidad.grid(row=3, column=1, sticky='w', padx=10, pady=5)

l_monto = Label(frame_formulario, text='Monto:')
l_monto.grid(row=2, column=2, sticky=SW)
e_monto = Entry(frame_formulario, textvariable=var_monto, width=we_ancho)
e_monto.grid(row=3, column=2, sticky='w', pady=5)

l_responsable = Label(frame_formulario, text='Responsable:')
l_responsable.grid(row=4, column=0, sticky=SW)
cb_responsable = ttk.Combobox(frame_formulario, values=opciones_responsable,
                              width=wcb_ancho)
cb_responsable.grid(row=5, column=0, sticky='w', pady=5)

l_rubro = Label(frame_formulario, text='Rubro:')
l_rubro.grid(row=4, column=1, sticky=SW, padx=10)
cb_rubro = ttk.Combobox(frame_formulario, values=opciones_rubro, width=wcb_ancho)
cb_rubro.grid(row=5, column=1, sticky='w', padx=10, pady=5)

l_proveedor = Label(frame_formulario, text='Proveedor:')
l_proveedor.grid(row=4, column=2, sticky=SW)
e_proveedor = Entry(frame_formulario, textvariable=var_proveedor, width=we_ancho)
e_proveedor.grid(row=5, column=2, sticky='w', pady=5)

l_medio_pago = Label(frame_formulario, text='Medio de pago:')
l_medio_pago.grid(row=6, column=0, sticky=SW)
cb_medio_pago = ttk.Combobox(frame_formulario, values=opciones_medio_pago,
                             width=wcb_ancho)
cb_medio_pago.grid(row=7, column=0, sticky='w', pady=5)

l_fecha = Label(frame_formulario, text='Fecha:')
l_fecha.grid(row=6, column=1, sticky=SW, padx=10)
cal_fecha = DateEntry(frame_formulario, width=wcb_ancho, background='darkblue',
                      foreground='white', borderwidth=2)
cal_fecha.grid(row=7, column=1, sticky='w', padx=10, pady=5)

l_vencimiento = Label(frame_formulario, text='Vencimiento:')
l_vencimiento.grid(row=6, column=2, sticky=SW)
e_vencimiento = DateEntry(frame_formulario, width=wcb_ancho, background='darkblue',
                          foreground='white', borderwidth=2)
e_vencimiento.grid(row=7, column=2, sticky='w', pady=5)

l_consulta = Label(root, text='Consulta:')
l_consulta.grid(row=9, column=0, sticky=W, padx=10, pady=(0, 5))
e_consulta = Entry (root, textvariable=var_consulta, width=25)
e_consulta.grid(row=10, column=0, sticky='nsew', padx=10)

l_total = Label(root, text='Total ', font=('Arial', 10, 'bold'))
l_total.grid(row=8, column=2, sticky=S, pady=5)
e_total = Entry(root, textvariable=var_total, width=20, 
                font=('Arial', 10, 'bold'), justify='center', state='readonly')
e_total.grid(row=9, column=2, sticky='nsew', padx=10, pady=5)
#-----FIN FORMULARIO-----#

#-----BOTONES-----#
boton_alta = Button(root, text='Alta', command=preparar_alta, bg='grey',fg='white', width=15)
boton_alta.grid(row=3, column=2, sticky=N)

boton_baja = Button(root, text='Baja', command=preparar_baja, bg='grey',fg='white', width=15)
boton_baja.grid(row=5, column=2, sticky=N)

boton_modificacion = Button(root, text='Modificacion',
                            command=modificacion, bg='grey',fg='white', width=15)
boton_modificacion.grid(row=7, column=2, sticky=N)

boton_buscar = Button(root, text='Buscar', command=consulta, bg='grey',fg='white',width=15)
boton_buscar.grid(row=10, column=1, sticky=W)

boton_confirmar = Button(root, text='Confirmar', state='disabled', command=confirmar, width=15,
                         bg='green',fg='white')
boton_confirmar.grid(row=8, column=0, sticky=E)

boton_cancelar = Button(root, text='Cancelar', state='disabled', command=cancelar, width=15,
                        bg='red',fg='white')
boton_cancelar.grid(row=8, column=1, sticky=W)

ch_vencimiento = Checkbutton(frame_formulario, text='N/A',
                             variable=var_check_vencimiento,
                             command=actualizar_estado_fecha)
ch_vencimiento.grid(row=6, column=2, sticky=SE, padx=5)

grafico_temp = Button(frame_grafico, text='ACA VA EL GRÁFICO', bg='white',
                     width=57, pady=118, state='disabled')
grafico_temp.grid(row=0, column=0, padx=0, pady=0, sticky='e')
#-----FIN BOTONES-----#

#-----TREEVIEW-----#
tree = ttk.Treeview(frame_treeview)
tree.grid(row=0, column=0, sticky='nsew')

tree_scroll_vertical = Scrollbar(frame_treeview, orient="vertical",
                                 command=tree.yview)
tree_scroll_vertical.grid(row=0, column=1, sticky='ns')

tree.configure(yscrollcommand=tree_scroll_vertical.set)

estilo = ttk.Style(frame_treeview)
estilo.theme_use("default")
estilo.configure("Treeview.Heading", 
                 font=('Calibri', 10, 'bold'), 
                 background='black', 
                 foreground='white')

tree['column'] = ('col1', 'col2', 'col3', 'col4', 'col5', 
                  'col6', 'col7', 'col8', 'col9', 'col10')

tree.column('#0', width=50, minwidth=50, stretch=NO) # id
tree.column('col1', width=190, minwidth=50, stretch=NO) # Producto
tree.column('col2', width=70, minwidth=50, stretch=NO) # Cantidad
tree.column('col3', width=90, minwidth=50, stretch=NO) # Monto
tree.column('col4', width=105, minwidth=50, stretch=NO) # Responsable
tree.column('col5', width=125, minwidth=50, stretch=NO) # Subtotal
tree.column('col6', width=115, minwidth=50, stretch=NO) # Rubro
tree.column('col7', width=220, minwidth=50, stretch=NO) # Proveedor
tree.column('col8', width=180, minwidth=50, stretch=NO) # Medio de Pago
tree.column('col9', width=90, minwidth=50, stretch=NO) # Fecha
tree.column('col10', width=100, minwidth=50, stretch=NO) # Vencimiento

tree.heading('#0', text='Id')
tree.heading('col1', text='Producto')
tree.heading('col2', text='Cantidad')
tree.heading('col3', text='Monto')
tree.heading('col4', text='Responsable')
tree.heading('col5', text='Subtotal')
tree.heading('col6', text='Rubro')
tree.heading('col7', text='Proveedor')
tree.heading('col8', text='Medio de pago')
tree.heading('col9', text='Fecha')
tree.heading('col10', text='Vencimiento')
#-----FIN TREEVIEW-----#

#-----GRAFICO-----#
def create_graph(frame_grafico):
    data = get_data_for_graph()
    mes_palabra = obtener_mes_palabra_actual()
    rubros = [row[0][:4] for row in data]
    totales = [row[1] for row in data]
    
    fig = Figure(figsize=(6, 4), dpi=75)
    plot = fig.add_subplot(1, 1, 1)
    
    colors = plt.cm.get_cmap('tab20', len(rubros))

    bars = plot.bar(rubros, totales, color=[colors(i) for i in range(len(rubros))])
    
    plot.set_xticks(range(len(rubros)))
    plot.set_xticklabels(rubros, ha='center', fontsize='small')
    
    # Keep the labels on top of the bars
    for bar, total in zip(bars, totales):
        yval = bar.get_height()
        plot.text(bar.get_x() + bar.get_width()/2.0, yval, f'${total:.2f}', va='bottom', ha='center', fontsize='small')

    # Remove y-axis labels (left side vertical axis)
    plot.set_yticks([])
    plot.set_title(f'Total de Gastos por Rubro en {mes_palabra}', fontsize=12)
    
    canvas = FigureCanvasTkAgg(fig, master=frame_grafico)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True)


grafico_temp.destroy()
create_graph(frame_grafico)
#-----FIN GRAFICO-----#

#-----FIN WIDGETS-----#

actualizar_label_total_acumulado()
cargar_total_acumulado()
cargar_datos_en_treeview()
root.mainloop()
#---------------------------------FIN VISTA----------------------------------#
