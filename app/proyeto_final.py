from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk


root = Tk()
root.title('Ejercicio 5')

original_image = Image.open("Modulo 2/Unidad 1/Ejercicios resueltos U5/giphy.gif")
resized_image = original_image.resize((50, 50))
photo = ImageTk.PhotoImage(resized_image)

img = Label(root, image=photo)
img.grid(row=1, column=0, columnspan = 6, padx = 10, pady = 5)

title = Label(root, text = 'Gestor de compras Python', font = ('Arial', 16))
title.grid(row = 0, column = 0, columnspan = 6, padx = 10, pady = 5)

var_id = IntVar()
var_producto = StringVar()
var_cantidad = IntVar()
var_precio = StringVar()
var_cliente = StringVar()
var_subtotal = StringVar()
var_total = StringVar()

producto = Label(root, text = 'Producto: ')
producto.grid(row = 2, column = 0, sticky = W, padx = 10, pady = 5)
entry_producto = Entry(root, textvariable = var_producto)
entry_producto.grid(row = 3, column = 0, sticky = W, padx = 10, pady = 5)

cantidad = Label(root, text = 'Cantidad: ')
cantidad.grid(row = 2, column = 1, sticky = W, padx = 10, pady = 5)
entry_cantidad = Entry(root, textvariable = var_cantidad)
entry_cantidad.grid(row = 3, column = 1, sticky = W, padx = 10, pady = 5)

precio = Label(root, text = 'Precio: ')
precio.grid(row = 4, column = 0, sticky = W, padx = 10, pady = 5)
entry_precio = Entry(root, textvariable = var_precio)
entry_precio.grid(row = 5, column = 0, sticky = W, padx = 10, pady = 5)

cliente = Label(root, text = 'Cliente: ')
cliente.grid(row = 4, column = 1, sticky = W, padx = 10, pady = 5)
entry_cliente = Entry(root, textvariable = var_cliente)
entry_cliente.grid(row = 5, column = 1, sticky = W, padx = 10, pady = 5)

total = Label(root, text = 'Total: ')
total.grid(row = 4, column = 3, sticky = E, padx = 10, pady = 5)
entry_total = Entry(root, textvariable = var_total)
entry_total.grid(row = 4, column = 4, sticky = W, padx = 10, pady = 10)

total_acumulado = 0


def alta():
    
    global total_acumulado
    
    precio = float(var_precio.get())
    cantidad = int(var_cantidad.get())
    subtotal_acumulado = cantidad * precio

    total_acumulado += subtotal_acumulado
    var_total.set(f"{total_acumulado:.2f}")

    compra_id = tree.insert('', 
                            'end', 
                            values=(var_producto.get(),
                                    cantidad,
                                    precio,
                                    var_cliente.get(),
                                    f"{subtotal_acumulado:.2f}"))

    tree.item(compra_id, text=str(compra_id))

    var_id.set(compra_id)
    var_producto.set('')
    var_cantidad.set('')
    var_precio.set('')
    

def baja():
    
    global total_acumulado
    
    compra_id = tree.focus()
    if not compra_id:
        return
    
    valores = tree.item(compra_id, 'values')

    subtotal_eliminar = float(valores[-1])  
    
    total_acumulado -= subtotal_eliminar
    var_total.set(f"{total_acumulado:.2f}")
    
    tree.delete(compra_id)


boton_alta = Button(root, text = 'Ingresar', command = alta, width = 20)
boton_alta.grid(row = 3, column = 2, padx = 10, pady = 5)

boton_baja = Button(root, text = 'Borrar', command = baja, width = 20)
boton_baja.grid(row = 4, column = 2, padx = 10, pady = 5)

tree = ttk.Treeview(root)

tree['column'] = ('col1', 'col2', 'col3', 'col4', 'col5')
tree.column('#0', anchor = 'center')   # id
tree.column('col1', anchor = 'center') # Producto
tree.column('col2', anchor = 'center') # Cantidad
tree.column('col3', anchor = 'center') # Precio
tree.column('col4', anchor = 'center') # CLiente
tree.column('col5', anchor = 'center') # Subtotal

tree.heading('#0', text = 'Id')
tree.heading('col1', text = 'Producto')
tree.heading('col2', text = 'Cantidad')
tree.heading('col3', text = 'Pecio')
tree.heading('col4', text = 'Cliente')
tree.heading('col5', text = 'Subtotal')

tree.grid(row = 7, column = 0, columnspan = 5, padx = 10, pady = 5)

root.mainloop()
