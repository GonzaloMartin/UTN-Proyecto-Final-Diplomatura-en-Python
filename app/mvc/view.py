import matplotlib.pyplot as plt

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from PIL import Image as PilImage, ImageTk

from tkinter import Tk
from tkinter import (BooleanVar,
                     Button,
                     Checkbutton,
                     Entry,
                     Frame,
                     IntVar,
                     Label,
                     LabelFrame)
from tkinter import (N,
                     E,
                     S,
                     W,
                     NO,
                     SE,
                     SW)
from tkinter import (Scrollbar,
                     StringVar)
from tkinter import ttk

from tkcalendar import DateEntry

from controller import (cancelar,
                        confirmar,
                        preparar_alta,
                        preparar_baja,
                        obtener_mes_palabra_actual,
                        cargar_total_acumulado,
                        cargar_datos_en_treeview,
                        actualizar_estado_fecha,
                        actualizar_label_total_acumulado)

from model import(obtener_datos_grafico,
                  modificacion,
                  consulta)

from .model import ModelClass

class ViewClass:
    
    opciones_rubro = ["Mantenimiento", "Impuestos", "Servicios",
                      "Mercado", "Limpieza", "Colegio", "Otros"]

    opciones_medio_pago = ["Efectivo", "Billetera virtual",
                           "Cheque", "Tarjeta de Crédito",
                           "Tarjeta de Débito", "Transferencia", "Otro"]

    opciones_responsable = ["Gonzalo", "Matías", "Juan"]
    
    def __init__(self, controller):
        self.model = ModelClass()
        self.controller = controller
        self.root = None
        self.tree = None
        self.estado = None
        self.var_monto = None
        self.var_producto = None
        self.var_cantidad = None
        self.var_fecha = 0
        self.var_proveedor = None
        self.var_responsable = None
        self.var_rubro = None
        self.cal_fecha = None
        self.var_medio_pago = None
        self.var_total = None
        self.cb_responsable = None
        self.cb_rubro = None
        self.l_total = None
        self.boton_confirmar = None
        self.var_vencimiento = None
        self.frame_grafico = None
        self.boton_cancelar = None
        self.var_consulta = None
        self.e_vencimiento = None
        self.var_check_vencimiento = None
        self.cb_medio_pago = None
    
    
    def cargar_total_acumulado(self):
        total_acumulado = self.controller.obtener_total_acumulado()
        self.var_total.set(f"$ {total_acumulado:.2f}")
        return total_acumulado

    def actualizar_label_total_acumulado(self):
        mes_actual_str = self.controller.obtener_mes_palabra_actual()
        self.l_total.config(text=f"Total {mes_actual_str}:")
    
    def limpiar_formulario(self):
        self.var_monto.set('')
        self.var_producto.set('')
        self.var_cantidad.set('')
        self.var_proveedor.set('')
        self.var_responsable.set('')
        self.var_rubro.set('')
        self.var_medio_pago.set('')
        self.cb_responsable.set('')
        self.cb_rubro.set('')
        self.cb_medio_pago.set('')
        
    def actualizar_estado_bar(self, mensaje): 
        self.estado.config(text=mensaje)  # Actualiza texto del label
        self.root.update_idletasks()  # Fuerza la actualización de la UI
    
    def actualizar_estado_fecha(self):
        if self.var_check_vencimiento.get():
            self.e_vencimiento.config(state='disabled')
        else:
            self.e_vencimiento.config(state='normal')
            
    def cargar_datos_en_treeview(self):
        registros = self.controller.consulta_bd()
        for row in registros:
            self.tree.insert('', 'end', text=str(row[0]), values=row[1:])

    # GRÁFICO            
    def crear_grafico(self, frame_grafico):
        data = self.controller.obtener_datos_grafico()
        mes_palabra = self.controller.obtener_mes_palabra_actual()
        rubros = []
        totales = []

        for row in data:
            rubros.append(row[0][:4])
            totales.append(row[1])
        
        for rubro_op in self.opciones_rubro:
            if rubro_op[:4] not in rubros:
                rubros.append(rubro_op[:4])
                totales.append(0)

        fig = Figure(figsize=(6, 4), dpi=75)
        plot = fig.add_subplot(1, 1, 1)
        
        colors = plt.colormaps['tab20'](range(len(rubros)))
        
        lista_colores = []
        for i in range(len(rubros)):
            lista_colores.append(colors[i])

        bars = plot.bar(rubros, totales, color=lista_colores)
        
        plot.set_xticks(range(len(rubros)))
        plot.set_xticklabels(rubros, ha='center', fontsize='small')
        
        for bar, total in zip(bars, totales):
            yval = bar.get_height()
            plot.text(bar.get_x() + bar.get_width()/2.0, yval, f'${total:.2f}', 
                      va='bottom', ha='center', fontsize='small')

        plot.set_yticks([])
        plot.set_title(f'Total de Gastos por Rubro en {mes_palabra}', fontsize=12)
        
        canvas = FigureCanvasTkAgg(fig, master=frame_grafico)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
    # FIN GRÁFICO
    # FIN MÉTODOS

    def create_view(self):
        self.root = Tk()
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=0)
        self.root.grid_columnconfigure(2, weight=1)
        self.root.grid_columnconfigure(3, weight=1)
        self.root.grid_rowconfigure(12, weight=1) # Expande el TreeView
        self.root.title('Gestor de Gastos Python')
        self.root.geometry('1600x900')     # Tamaño de la ventana standard notebook 14'

        #-----FRAMES-----#
        header_frame = Frame(self.root)
        header_frame.grid_columnconfigure(1, weight=1)
        # header_frame.grid(row=0, column=0, sticky='ew', padx=0, pady=5)
        
        version_frame = Frame(self.root, borderwidth=1, relief="solid")
        version_frame.grid(row=0, column=1, sticky='ew', padx=20, pady=10)
        
        version_frame.grid_columnconfigure(0, weight=1)
        version_frame.grid_columnconfigure(1, weight=0)
        version_frame.grid_columnconfigure(2, weight=1)

        frame_estado = Frame(self.root, borderwidth=1, relief="solid")
        frame_estado.grid(row=0, column=3, sticky='ew', padx=10, pady=0, columnspan=3)
        # frame_estado.grid(row=0, column=2, padx=0, pady=10, columnspan=3)
               
        self.frame_grafico = Frame(self.root, borderwidth=1, relief="solid")
        self.frame_grafico.grid(row=2, column=3, rowspan=9, padx=10, pady=0, sticky='nsew')


        frame_formulario = LabelFrame(self.root, text="Ingreso de datos", padx=10, pady=10)
        frame_formulario.grid(row=2, column=0, columnspan=2, rowspan=6, padx=10,
                            pady=10, sticky="we")

        frame_confirmacion = Frame(self.root)
        frame_confirmacion.grid(row=8, column=0, columnspan=2, padx=10, pady=10)
        frame_confirmacion.grid_rowconfigure(0, weight=1)
        frame_confirmacion.grid_columnconfigure(0, weight=1)
        frame_confirmacion.grid_columnconfigure(1, weight=1)
        
        frame_treeview = Frame(self.root)
        frame_treeview.grid(row=12, column=0, columnspan=11, padx=10, pady=10,
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

        self.variables_a_validar = [var_producto,
                                    var_cantidad,
                                    var_monto,
                                    var_responsable,
                                    var_proveedor,
                                    var_medio_pago,
                                    var_rubro, 
                                    var_fecha, 
                                    var_vencimiento]
        #-----WIDGETS-----#

        #-----HEADER-----#
        imagen_original = PilImage.open("app/rsc/tkinter_app_logo.png")
        imagen_resize = imagen_original.resize((50, 50))
        foto = ImageTk.PhotoImage(imagen_resize)

        img = Label(header_frame, image=foto)
        img.grid(row=0, column=0, padx=10, pady=5, sticky=W)

        title = Label(header_frame, text='GESTOR DE GASTOS PYTHON', font=('Arial', 20, 'bold'))
        title.grid(row=0, column=1, padx=0, sticky=W)
        #-----FIN HEADER-----#

        #-----ESTADO-----#
        self.estado = Label(frame_estado, text="Bienvenido.", font=('Arial', 10),
                            width=50, anchor=W)
        self.estado.grid(row=0, column=3, sticky=W, padx=0, pady=0)
        # self.estado.grid(row=0, column=0, sticky=W, padx=0, pady=0)
        #-----FIN ESTADO-----#
        
        # VERSION
        version = Label(version_frame, text="Version 1.0.0", font=('Arial', 10, 'bold'),
                        bg='grey', fg='white')
        version.grid(row=0, column=1, sticky='ew')  # Centra el label en el frame
        # END VERSION

        #-----FORMULARIO-----#
        we_ancho = 30
        wcb_ancho = we_ancho - 2
        l_producto = Label(frame_formulario, text='Producto:')
        l_producto.grid(row=2, column=0, sticky=W)
        e_producto = Entry(frame_formulario, textvariable=var_producto, width=we_ancho)
        e_producto.grid(row=3, column=0, sticky=W, pady=5)

        l_cantidad = Label(frame_formulario, text='Cantidad:')
        l_cantidad.grid(row=2, column=1, sticky=W, padx=10)
        e_cantidad = Entry(frame_formulario, textvariable=var_cantidad, width=we_ancho)
        e_cantidad.grid(row=3, column=1, sticky=W, padx=10, pady=5)

        l_monto = Label(frame_formulario, text='Monto:')
        l_monto.grid(row=2, column=2, sticky=SW)
        e_monto = Entry(frame_formulario, textvariable=var_monto, width=we_ancho)
        e_monto.grid(row=3, column=2, sticky=W, pady=5)

        l_responsable = Label(frame_formulario, text='Responsable:')
        l_responsable.grid(row=4, column=0, sticky=SW)
        cb_responsable = ttk.Combobox(frame_formulario, values=opciones_responsable,
                                    width=wcb_ancho)
        cb_responsable.grid(row=5, column=0, sticky=W, pady=5)

        l_rubro = Label(frame_formulario, text='Rubro:')
        l_rubro.grid(row=4, column=1, sticky=SW, padx=10)
        cb_rubro = ttk.Combobox(frame_formulario, values=opciones_rubro, width=wcb_ancho)
        cb_rubro.grid(row=5, column=1, sticky=W, padx=10, pady=5)

        l_proveedor = Label(frame_formulario, text='Proveedor:')
        l_proveedor.grid(row=4, column=2, sticky=SW)
        e_proveedor = Entry(frame_formulario, textvariable=var_proveedor, width=we_ancho)
        e_proveedor.grid(row=5, column=2, sticky=W, pady=5)

        l_medio_pago = Label(frame_formulario, text='Medio de pago:')
        l_medio_pago.grid(row=6, column=0, sticky=SW)
        cb_medio_pago = ttk.Combobox(frame_formulario, values=opciones_medio_pago,
                                    width=wcb_ancho)
        cb_medio_pago.grid(row=7, column=0, sticky=W, pady=5)

        l_fecha = Label(frame_formulario, text='Fecha:')
        l_fecha.grid(row=6, column=1, sticky=SW, padx=10)
        cal_fecha = DateEntry(frame_formulario, width=wcb_ancho, background='darkblue',
                            foreground='white', borderwidth=2)
        cal_fecha.grid(row=7, column=1, sticky=W, padx=10, pady=5)

        l_vencimiento = Label(frame_formulario, text='Vencimiento:')
        l_vencimiento.grid(row=6, column=2, sticky=SW)
        e_vencimiento = DateEntry(frame_formulario, width=wcb_ancho, background='darkblue',
                                foreground='white', borderwidth=2)
        e_vencimiento.grid(row=7, column=2, sticky=W, pady=5)

        l_consulta = Label(root, text='Consulta:')
        l_consulta.grid(row=9, column=0, sticky=W, padx=10, pady=5)
        e_consulta = Entry (root, textvariable=var_consulta, width=12)
        e_consulta.grid(row=10, column=0, sticky='nsew', padx=10, pady=5)

        l_total = Label(root, text='Total ', font=('Arial', 10, 'bold'))
        l_total.grid(row=8, column=2, sticky=S, pady=5)
        e_total = Entry(root, textvariable=var_total, width=20, 
                        font=('Arial', 10, 'bold'), justify='center', state='readonly')
        e_total.grid(row=9, column=2, sticky=W, padx=10, pady=5)
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

        boton_confirmar = Button(frame_confirmacion, text='Confirmar', state='disabled', command=confirmar, width=15,
                                bg='green',fg='white')
        boton_confirmar.grid(row=8, column=0, sticky=E)

        boton_cancelar = Button(frame_confirmacion, text='Cancelar', state='disabled', command=cancelar, width=15,
                                bg='red',fg='white')
        boton_cancelar.grid(row=8, column=1, sticky=W)

        ch_vencimiento = Checkbutton(frame_formulario, text='N/A',
                                    variable=var_check_vencimiento,
                                    command=actualizar_estado_fecha)
        ch_vencimiento.grid(row=6, column=2, sticky=SE, padx=5)

        grafico_temp = Button(frame_grafico, bg='white',
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
        tree.column('col7', width=180, minwidth=50, stretch=NO) # Proveedor
        tree.column('col8', width=120, minwidth=50, stretch=NO) # Medio de Pago
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
        #-----FIN GRAFICO-----#

        #-----FIN WIDGETS-----#

        actualizar_label_total_acumulado()
        cargar_total_acumulado()
        cargar_datos_en_treeview()
        root.mainloop()
        return