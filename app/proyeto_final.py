import re
import sqlite3
import tkinter as tk

from tkinter import *
from tkinter import ttk
from tkinter.messagebox import *
from tkcalendar import DateEntry

from PIL import Image, ImageTk


total_acumulado=0
mensaje_prompt = "Bienvenido."

#-----------------------------INICIO CONTROLADOR-----------------------------#

def actualizar_estado_bar():
    global mensaje_prompt
    
    estado.config(text=mensaje_prompt)  # Actualiza texto del label
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
    
    
def aplicar_modificacion(compra_id, id_bd):
    global mensaje_prompt
    
    if not validar_campos():
        mensaje_prompt = "Todos los campos deben estar llenos."
        actualizar_estado_bar()
        showinfo("Info", mensaje_prompt)
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

    mensaje_prompt = "Registro modificado con ID: " + str(id_bd)
    actualizar_estado_bar()
    limpiar_formulario()
    boton_alta.config(text='ALTA', command=alta)


def cargar_datos_en_treeview():
    registros = consulta_bd()
    for row in registros:
        tree.insert('', 'end', text=str(row[0]), values=row[1:])

#-------------------------------FIN CONTROLADOR------------------------------#

##############################################################################

#--------------------------------INICIO MODELO-------------------------------#

#-----ABMC-----#
def alta():
    global total_acumulado
    global mensaje_prompt
    
    var_fecha.set(cal_fecha.get_date().strftime("%Y-%m-%d"))
    if var_check_vencimiento.get():
        vencimiento_value = 'N/A'
    else:
        vencimiento_value = e_vencimiento.get_date().strftime("%Y-%m-%d")

    var_vencimiento.set(vencimiento_value)

    if not validar_campos():
        mensaje_prompt = "Todos los campos deben estar llenos."
        showinfo("Info", mensaje_prompt)
        actualizar_estado_bar()
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
            mensaje_prompt = "Todos los campos de alta deben tener contenido."
            showinfo("Info", mensaje_prompt)
            actualizar_estado_bar()
            return
        
    conn = conectar_base_de_datos()
    ultimo_id = alta_bd(conn, valores)

    subtotal_acumulado = valores['cantidad'] * valores['monto']
    total_acumulado += subtotal_acumulado
    var_total.set(f"{total_acumulado:.2f}")

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

    mensaje_prompt = "Se dio de alta el registro con ID: " + str(ultimo_id)
    actualizar_estado_bar()
    limpiar_formulario()


def baja():
    global total_acumulado
    global mensaje_prompt
    
    compra_id = tree.focus()
    if not compra_id:
        mensaje_prompt = "Debe seleccionar un registro para dar de Baja."
        showinfo("Info", mensaje_prompt)
        actualizar_estado_bar()
        return
    
    valores = tree.item(compra_id, 'values')

    subtotal_str = valores[4]

    if re.match(r'^\d+(\.\d+)?$', subtotal_str): # Enteros >= 0 y decimales >= 0
        subtotal_eliminar = float(subtotal_str)
    else:
        mensaje_prompt = "El subtotal no es un número válido."
        showinfo("Error", mensaje_prompt)
        actualizar_estado_bar()
        return

    id_bd_str = tree.item(compra_id, 'text')

    if re.match(r'^\d+$', id_bd_str): # Enteros >= 0
        id_bd = int(id_bd_str)
    else:
        mensaje_prompt = "El ID no es un número válido."
        showinfo("Error", mensaje_prompt)
        actualizar_estado_bar()
        return

    baja_bd(id_bd)

    total_acumulado -= subtotal_eliminar
    var_total.set(f"{total_acumulado:.2f}")
    
    tree.delete(compra_id)
    
    mensaje_prompt = "Se dio de baja el registro con ID: " + str(id_bd)
    actualizar_estado_bar()
    
    
def modificacion():
    global mensaje_prompt
    
    compra_id = tree.focus()
    if not compra_id:
        mensaje_prompt = "Debe seleccionar un registro para Modificar."
        showinfo("Info", mensaje_prompt)
        actualizar_estado_bar()
        return
    
    valores = tree.item(compra_id, 'values')
    id_bd = int(tree.item(compra_id, 'text'))
    
    var_producto.set(valores[0])
    var_cantidad.set(valores[1])
    var_monto.set(valores[2])
    var_fecha.set(valores[8])
    cb_responsable.set(valores[3])
    cb_rubro.set(valores[5])
    cb_medio_pago.set(valores[7])
    var_proveedor.set(valores[6])
    var_vencimiento.set(valores[9])
    
    boton_alta.config(text='MODIFICAR',
                      command=lambda: aplicar_modificacion(compra_id, id_bd))
    mensaje_prompt = "Modificando registro ID: " + str(id_bd)
    actualizar_estado_bar()


def consulta():
    global mensaje_prompt

    termino_busqueda = var_consulta.get()
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

    mensaje_prompt = f"Resultados de la búsqueda para: {termino_busqueda}"
    actualizar_estado_bar()
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

    subtotal = valores['cantidad'] * valores['monto']
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

    
def consulta_bd():
    conn = conectar_base_de_datos()
    cursor = conn.cursor()
    query = """SELECT * FROM gastos;"""
    cursor.execute(query)
    rows = cursor.fetchall()
    desconectar_base_de_datos(conn)
    return rows


conn = conectar_base_de_datos()
crear_tabla(conn)
#-----FIN BASE DE DATOS-----#

#---------------------------------FIN MODELO---------------------------------#

##############################################################################

#--------------------------------INICIO VISTA--------------------------------#

root = Tk()
root.grid_rowconfigure(10, weight=1)
root.title('Gestor de compras')
root.geometry('1024x768')
root.resizable(True, True)

#-----FRAMES-----#
frame_formulario = LabelFrame(root, text="Ingreso de datos", padx=10, pady=10)
frame_formulario.grid(row=2, column=0, columnspan=3, rowspan=6, padx=10,
                      pady=10, sticky="nsew")
frame_formulario.grid_columnconfigure(0, weight=1)
frame_formulario.grid_columnconfigure(1, weight=1)
frame_formulario.grid_columnconfigure(2, weight=1)

frame_estado = Frame(root, borderwidth=1, relief="solid")
frame_estado.grid(row=0, column=2, padx=0, pady=10, columnspan=3)

frame_treeview = Frame(root)
frame_treeview.grid(row=10, column=0, columnspan=11, padx=10, pady=10,
                    sticky='nsew')
frame_treeview.grid_rowconfigure(0, weight=1)
frame_treeview.grid_columnconfigure(0, weight=1)
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
imagen_original = Image.open("imgs/python_logo_tn.png")
imagen_resize = imagen_original.resize((50, 50))
foto = ImageTk.PhotoImage(imagen_resize)
img = Label(root, image=foto)
img.grid(row=0, column=0, sticky='ns', padx = 10, pady=5)

title = Label(root, text='GESTOR DE COMPRAS PYTHON',
              font = ('Arial', 20, 'bold'))
title.grid(row=0, column=1, sticky=W, pady=5)
#-----FIN HEADER-----#

#-----ESTADO-----#
estado = Label(frame_estado, text=mensaje_prompt, font=('Arial', 10),
               width=50, anchor=W)
estado.grid(row=0, column=2, sticky=W, padx=0, pady=0)
#-----FIN ESTADO-----#

#-----FORMULARIO-----#
l_producto = Label(frame_formulario, text='Producto:      ', width=15)
l_producto.grid(row=2, column=0, sticky=W, pady=5)
e_producto = Entry(frame_formulario, textvariable=var_producto, width=15)
e_producto.grid(row=3, column=0, sticky='nsew', pady=5)

l_cantidad = Label(frame_formulario, text='Cantidad:      ', width=15)
l_cantidad.grid(row=2, column=1, sticky=W, pady=5)
e_cantidad = Entry(frame_formulario, textvariable=var_cantidad, width=15)
e_cantidad.grid(row=3, column=1, sticky='nsew', pady=5)

l_monto = Label(frame_formulario, text='Monto:         ', width=15)
l_monto.grid(row=2, column=2, sticky=W, pady=5)
e_monto = Entry(frame_formulario, textvariable=var_monto, width=15)
e_monto.grid(row=3, column=2, sticky='nsew', pady=5)

l_responsable = Label(frame_formulario, text='Responsable:   ', width=15)
l_responsable.grid(row=4, column=0, sticky=W, pady=5)
cb_responsable = ttk.Combobox(frame_formulario, values=opciones_responsable,
                              width=13)
cb_responsable.grid(row=5, column=0, sticky='nsew', pady=5)

l_rubro = Label(frame_formulario, text='Rubro:         ', width=15)
l_rubro.grid(row=4, column=1, sticky=W, pady=5)
cb_rubro = ttk.Combobox(frame_formulario, values=opciones_rubro, width=13)
cb_rubro.grid(row=5, column=1, sticky='nsew', pady=5)

l_proveedor = Label(frame_formulario, text='Proveedor:     ', width=15)
l_proveedor.grid(row=4, column=2, sticky=W, pady=5)
e_proveedor = Entry(frame_formulario, textvariable=var_proveedor, width=15)
e_proveedor.grid(row=5, column=2, sticky='nsew', pady=5)

l_medio_pago = Label(frame_formulario, text='Medio de pago: ', width=15)
l_medio_pago.grid(row=6, column=0, sticky=W, pady=5)
cb_medio_pago = ttk.Combobox(frame_formulario, values=opciones_medio_pago,
                             width=13)
cb_medio_pago.grid(row=7, column=0, sticky='nsew', pady=5)

l_fecha = Label(frame_formulario, text='Fecha:         ', width=15)
l_fecha.grid(row=6, column=1, sticky=W, pady=5)
cal_fecha = DateEntry(frame_formulario, width=12, background='darkblue',
                      foreground='white', borderwidth=2)
cal_fecha.grid(row=7, column=1, sticky='nsew', pady=5)

l_vencimiento = Label(frame_formulario, text='Vencimiento:   ', width=15)
l_vencimiento.grid(row=6, column=2, sticky=W, pady=5)
e_vencimiento = DateEntry(frame_formulario, width=12, background='darkblue',
                          foreground='white', borderwidth=2)
e_vencimiento.grid(row=7, column=2, sticky='nsew', pady=5)

l_consulta = Label(root, text='Consulta: ', width=15)
l_consulta.grid(row=8, column=0, sticky=W, pady=5)
e_consulta = Entry (root, textvariable=var_consulta, width=25)
e_consulta.grid(row=9, column=0, sticky='nsew', padx=10, pady=5)

l_total = Label(root, text='Total acumulado', width=15)
l_total.grid(row=8, column=3, sticky=N, pady=5)
e_total = Entry(root, textvariable=var_total, width=20)
e_total.grid(row=9, column=3, sticky='nsew', padx=10, pady=5)
#-----FIN FORMULARIO-----#

#-----BOTONES-----#
boton_alta = Button(root, text='ALta', command=alta, width=15, bg='green',
                    fg='white')
boton_alta.grid(row=3, column=3, sticky=N)

boton_baja = Button(root, text='Baja', command=baja, width=15, bg='red',
                    fg='white')
boton_baja.grid(row=5, column=3, sticky=N)

boton_baja = Button(root, text='Modificacion', command=modificacion, width=15,
                    bg='blue', fg='white')
boton_baja.grid(row=7, column=3, sticky=N)

boton_baja = Button(root, text='Buscar', command=consulta, width=15,
                    bg='orange',fg='black')
boton_baja.grid(row=9, column=1, pady=5, sticky=W)

ch_vencimiento = Checkbutton(frame_formulario, text='N/A',
                             variable=var_check_vencimiento,
                             command=actualizar_estado_fecha)
ch_vencimiento.grid(row=6, column=2, sticky=E, padx=5, pady=6)
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
tree.column('col1', width=270, minwidth=50, stretch=NO) # Producto
tree.column('col2', width=100, minwidth=50, stretch=NO) # Cantidad
tree.column('col3', width=170, minwidth=50, stretch=NO) # Monto
tree.column('col4', width=170, minwidth=50, stretch=NO) # Responsable
tree.column('col5', width=170, minwidth=50, stretch=NO) # Subtotal
tree.column('col6', width=170, minwidth=50, stretch=NO) # Rubro
tree.column('col7', width=270, minwidth=50, stretch=NO) # Proveedor
tree.column('col8', width=170, minwidth=50, stretch=NO) # Medio de Pago
tree.column('col9', width=170, minwidth=50, stretch=NO) # Fecha
tree.column('col10', width=170, minwidth=50, stretch=NO) # Vencimiento

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

#-----FIN WIDGETS-----#

cargar_datos_en_treeview()
root.mainloop()
#---------------------------------FIN VISTA----------------------------------#
