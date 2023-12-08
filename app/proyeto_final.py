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

    for var in [var_producto, var_cantidad,
                var_monto, var_proveedor,
                var_fecha, var_vencimiento]:
        if isinstance(var, (StringVar, IntVar)) and not var.get():
            return False

    for cb in [cb_responsable, cb_rubro, cb_medio_pago]:
        if not cb.get():
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
    
    
def aplicar_modificacion(compra_id):
    
    global mensaje_prompt
    
    responsable_actual = cb_responsable.get()
    rubro_actual = cb_rubro.get()
    medio_pago_actual = cb_medio_pago.get()

    vencimiento_value = 'N/A' if var_check_vencimiento.get() else e_vencimiento.get_date().strftime("%Y-%m-%d")

    nuevo_valor = {
        'producto': var_producto.get(),
        'cantidad': int(var_cantidad.get()),
        'monto': float(var_monto.get()),
        'responsable': responsable_actual,
        'rubro': rubro_actual,
        'proveedor': var_proveedor.get(),
        'medio_pago': medio_pago_actual,
        'fecha': var_fecha.get(),
        'vencimiento': vencimiento_value
    }
    
    nuevo_subtotal = nuevo_valor['monto'] * nuevo_valor['cantidad']
    var_total.set(f"{nuevo_subtotal:.2f}")
    
    if tree.exists(compra_id):
        tree.item(compra_id, values=(
            nuevo_valor['producto'],
            nuevo_valor['cantidad'],
            nuevo_valor['monto'],
            nuevo_valor['responsable'],
            f"{nuevo_subtotal:.2f}",
            nuevo_valor['rubro'],
            nuevo_valor['proveedor'],
            nuevo_valor['medio_pago'],
            nuevo_valor['fecha'],
            nuevo_valor['vencimiento']
        ))
    
    boton_alta.config(text='ALTA', command=alta)
    
    mensaje_prompt = "Modificación del registro con ID: " + str(compra_id)
    actualizar_estado_bar()
    limpiar_formulario()

#-----BASE DE DATOS-----#

#-----FIN BASE DE DATOS-----#

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
        e_vencimiento.config(state='disabled')
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

    subtotal_acumulado = valores['cantidad'] * valores['monto']
    total_acumulado += subtotal_acumulado

    var_total.set(f"{total_acumulado:.2f}")

    compra_id = tree.insert('',
                            'end',
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

    tree.item(compra_id, text=str(compra_id))

    var_id.set(compra_id)
    mensaje_prompt = "Se dio de alta el registro con ID: " + str(compra_id)
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
    
    try:
        subtotal_eliminar = float(valores[4])  
    except ValueError:
        mensaje_prompt = "Subtotal para el registro seleccionado."
        showinfo("Error", mensaje_prompt)
        actualizar_estado_bar()
        return
    
    total_acumulado -= subtotal_eliminar
    var_total.set(f"{total_acumulado:.2f}")
    
    tree.delete(compra_id)
    
    mensaje_prompt = "Se dio de baja el registro con ID: " + str(compra_id)
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
                      command=lambda: aplicar_modificacion(compra_id))
    mensaje_prompt = "Mostrando datos para modificar..."
    actualizar_estado_bar()


def consulta():
    pass
#-----FIN ABMC-----#

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

#-----VALIDACIONES-----#
variables_a_validar = [var_producto, var_cantidad, var_monto, var_responsable,
                       var_proveedor, var_medio_pago, var_rubro, var_fecha, 
                       var_vencimiento]

opciones_rubro = ["Mantenimiento", "Impuestos", "Servicios",
                  "Mercado", "Limpieza", "Colegio", "Otros"]

opciones_medio_pago = ["Efectivo", "Billetera virtual",
                       "Cheque", "Tarjeta de Crédito",
                       "Tarjeta de Débito", "Transferencia", "Otro"]

opciones_responsable = ["Gonzalo", "Matías", "Juan"]
#-----FIN VALIDACIONES-----#

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

root.mainloop()
#---------------------------------FIN VISTA----------------------------------#
