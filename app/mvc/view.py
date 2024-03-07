"""
view.py
    Contiene la clase View, que se encarga de la interfaz gráfica de la aplicación.
    Se usa la librería tkinter para la creación de la interfaz gráfica.
    Se vincula con el controlador y el modelo para realizar las operaciones necesarias.
    Se usa también la librería matplotlib para la creación de gráficos.
    El gráfico se muestra en un Frame de la interfaz gráfica, el cual se actualiza con los datos de la base de datos.
    La lista treeview se actualiza con los datos de la base de datos.
"""

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

from .model import Model

from utils.utils import obtener_fecha_actual

class View:
    
    opciones_rubro = ["Mantenimiento", "Impuestos", "Servicios",
                      "Mercado", "Limpieza", "Colegio", "Otros"]

    opciones_medio_pago = ["Efectivo", "Billetera virtual",
                           "Cheque", "Tarjeta de Crédito",
                           "Tarjeta de Débito", "Transferencia", "Otro"]

    opciones_responsable = ["Gonzalo", "Matías", "Juan"]
    
    def __init__(self, controller):
        """
        Constructor de la clase View.
        Se inicializan las variables de la vista y se crea la instancia del modelo.
        
        :param controller: objeto Controller
        :return: None
        """
        
        self.model = Model()
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
        """
        Carga el total acumulado en el Entry correspondiente.
        Total Acumulado se obtiene del controlador.
        
        :param self: objeto View
        :return: Total Acumulado
        """
        
        total_acumulado = self.controller.obtener_total_acumulado()
        self.var_total.set(f"$ {total_acumulado:.2f}")
        return total_acumulado

    def actualizar_label_total_acumulado(self):
        """
        Actualiza el label que indica el mes actual.
        El mes actual se obtiene del controlador.
        
        :param self: objeto View
        :return: None
        """
        
        mes_actual_str = self.controller.obtener_mes_palabra_actual()
        self.l_total.config(text=f"Total {mes_actual_str}:")
    
    def limpiar_formulario(self):
        """
        Limpia los campos del formulario.
        Para fecha y vencimiento se establece la fecha actual.
        
        :param self: objeto View
        :return: None
        """
        
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
        self.cal_fecha.set_date(obtener_fecha_actual())
        self.var_check_vencimiento.set(False)
        self.e_vencimiento.config(state='normal')
        self.e_vencimiento.set_date(obtener_fecha_actual())
        
    def actualizar_estado_bar(self, mensaje): 
        """
        Actualiza el estado de la barra de estado.
        Fuerza la actualización de la UI.
        
        :param self: objeto View
        :param mensaje: mensaje a mostrar.
        :return: None
        """
        
        self.estado.config(text=mensaje)  # Actualiza texto del label
        self.root.update_idletasks()  # Fuerza la actualización de la UI
    
    def actualizar_estado_fecha(self):
        """
        Actualiza el estado del campo de fecha.
        Si el checkbutton está seleccionado, deshabilita el campo de fecha.
        Si no, habilita el campo de fecha.
        
        :param self: objeto View
        :return: None
        """
        
        if self.var_check_vencimiento.get():
            self.e_vencimiento.config(state='disabled')
        else:
            self.e_vencimiento.config(state='normal')
            
    def cargar_datos_en_treeview(self):
        """
        Carga los datos de la base de datos en el TreeView.
        Los datos se obtienen del controlador.
        
        :param self: objeto View
        :return: None
        """
        
        registros = self.controller.get_consulta_bd()
        for row in registros:
            self.tree.insert('', 'end', text=str(row[0]), values=row[1:])

    # GRÁFICO            
    def crear_grafico(self, frame_grafico):
        """
        Crea un gráfico de barras con los datos obtenidos de la base de datos.
        El gráfico sólo muestra los rubros que tienen gastos en el mes actual.
        Si el mes en curso no tiene gastos en un rubro, se muestra un gráfico vacío.
        
        :param self: objeto View
        :param frame_grafico: Frame donde se ubicará el gráfico.
        :return: None
        """
        
        data = self.controller.get_obtener_datos_grafico()
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

    # VIEW
    def create_view(self):
        """
        Crea la vista principal de la aplicación.
        Se establece una resolución por defecto de 1600x900.
        La interfaz gráfica se compone de varios frames, labels, entrys, 
        comboboxes, botones y un TreeView.
        La vista puede variar según la resolución de la pantalla y el sistema operativo.
        
        :param self: objeto View
        :return: None
        """
        
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
        ## header_frame.grid_columnconfigure(1, weight=1)
        header_frame.grid(row=0, column=0, sticky='ew', padx=0, pady=5)
        
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

        self.var_id = IntVar()
        self.var_producto = StringVar()
        # var_cantidad StringVar en lugar de IntVar porque se valida en validar_campos()
        self.var_cantidad = StringVar()
        self.var_monto = StringVar()
        self.var_responsable = StringVar()
        self.var_subtotal = StringVar()
        self.var_total = StringVar()
        self.var_rubro = StringVar()
        self.var_proveedor = StringVar()
        self.var_medio_pago = StringVar()
        self.var_fecha = StringVar()
        self.var_vencimiento = StringVar()
        self.var_check_vencimiento = BooleanVar()
        self.var_consulta = StringVar()

        self.variables_a_validar = [self.var_producto,
                                    self.var_cantidad,
                                    self.var_monto,
                                    self.var_responsable,
                                    self.var_proveedor,
                                    self.var_medio_pago,
                                    self.var_rubro, 
                                    self.var_fecha, 
                                    self.var_vencimiento]
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
        we_ancho = 30               # Widget Entry Ancho
        wcb_ancho = we_ancho - 2    # Widget Combobox Ancho
        self.l_producto = Label(frame_formulario, text='Producto:')
        self.l_producto.grid(row=2, column=0, sticky=W)
        self.e_producto = Entry(frame_formulario, textvariable=self.var_producto, width=we_ancho)
        self.e_producto.grid(row=3, column=0, sticky=W, pady=5)

        self.l_cantidad = Label(frame_formulario, text='Cantidad:')
        self.l_cantidad.grid(row=2, column=1, sticky=W, padx=10)
        self.e_cantidad = Entry(frame_formulario, textvariable=self.var_cantidad, width=we_ancho)
        self.e_cantidad.grid(row=3, column=1, sticky=W, padx=10, pady=5)
        
        self.l_monto = Label(frame_formulario, text='Monto:')
        self.l_monto.grid(row=2, column=2, sticky=SW)
        self.e_monto = Entry(frame_formulario, textvariable=self.var_monto, width=we_ancho)
        self.e_monto.grid(row=3, column=2, sticky=W, pady=5)
        
        self.l_responsable = Label(frame_formulario, text='Responsable:')
        self.l_responsable.grid(row=4, column=0, sticky=SW)
        self.cb_responsable = ttk.Combobox(frame_formulario, values=self.opciones_responsable,
                                           width=wcb_ancho)
        self.cb_responsable.grid(row=5, column=0, sticky=W, pady=5)

        self.l_rubro = Label(frame_formulario, text='Rubro:')
        self.l_rubro.grid(row=4, column=1, sticky=SW, padx=10)
        self.cb_rubro = ttk.Combobox(frame_formulario, values=self.opciones_rubro, width=wcb_ancho)
        self.cb_rubro.grid(row=5, column=1, sticky=W, padx=10, pady=5)

        self.l_proveedor = Label(frame_formulario, text='Proveedor:')
        self.l_proveedor.grid(row=4, column=2, sticky=SW)
        self.e_proveedor = Entry(frame_formulario, textvariable=self.var_proveedor, width=we_ancho)
        self.e_proveedor.grid(row=5, column=2, sticky=W, pady=5)

        self.l_medio_pago = Label(frame_formulario, text='Medio de pago:')
        self.l_medio_pago.grid(row=6, column=0, sticky=SW)
        self.cb_medio_pago = ttk.Combobox(frame_formulario, values=self.opciones_medio_pago,
                                    width=wcb_ancho)
        self.cb_medio_pago.grid(row=7, column=0, sticky=W, pady=5)

        self.l_fecha = Label(frame_formulario, text='Fecha:')
        self.l_fecha.grid(row=6, column=1, sticky=SW, padx=10)
        self.cal_fecha = DateEntry(frame_formulario, width=wcb_ancho, background='darkblue',
                            foreground='white', borderwidth=2)
        self.cal_fecha.grid(row=7, column=1, sticky=W, padx=10, pady=5)       

        self.l_vencimiento = Label(frame_formulario, text='Vencimiento:')
        self.l_vencimiento.grid(row=6, column=2, sticky=SW)
        self.e_vencimiento = DateEntry(frame_formulario, width=wcb_ancho, background='darkblue',
                                foreground='white', borderwidth=2)
        self.e_vencimiento.grid(row=7, column=2, sticky=W, pady=5)
        
        self.l_consulta = Label(self.root, text='Consulta:')
        self.l_consulta.grid(row=9, column=0, sticky=W, padx=10, pady=5)
        self.e_consulta = Entry (self.root, textvariable=self.var_consulta, width=12)
        self.e_consulta.grid(row=10, column=0, sticky='nsew', padx=10, pady=5)

        self.l_total = Label(self.root, text='Total ', font=('Arial', 10, 'bold'))
        self.l_total.grid(row=8, column=2, sticky=S, pady=5)
        self.e_total = Entry(self.root, textvariable=self.var_total, width=20, 
                             font=('Arial', 10, 'bold'), justify='center', state='readonly')
        self.e_total.grid(row=9, column=2, sticky=W, padx=10, pady=5)        
        #-----FIN FORMULARIO-----#

        #-----BOTONES-----#
        self.boton_alta = Button(self.root, text='Alta', command=self.controller.preparar_alta, 
                                 bg='grey',fg='white', width=15)
        self.boton_alta.grid(row=3, column=2, sticky=N)

        self.boton_baja = Button(self.root, text='Baja', command=self.controller.preparar_baja, 
                                 bg='grey',fg='white', width=15)
        self.boton_baja.grid(row=5, column=2, sticky=N)
        
        self.boton_modificacion = Button(self.root, text='Modificacion', command=self.controller.modificacion, 
                                         bg='grey',fg='white', width=15)
        self.boton_modificacion.grid(row=7, column=2, sticky=N)

        self.boton_buscar = Button(self.root, text='Buscar', command=self.controller.consulta, 
                                   bg='grey',fg='white',width=15)
        self.boton_buscar.grid(row=10, column=1, sticky=W)

        self.boton_confirmar = Button(frame_confirmacion, text='Confirmar', state='disabled', 
                                      command=self.controller.confirmar, width=15, bg='green',
                                      fg='white')
        self.boton_confirmar.grid(row=8, column=0, sticky=E)
        
        self.boton_cancelar = Button(frame_confirmacion, text='Cancelar', state='disabled', 
                                     command=self.controller.cancelar, width=15, bg='red',
                                     fg='white')
        self.boton_cancelar.grid(row=8, column=1, sticky=W)

        self.ch_vencimiento = Checkbutton(frame_formulario, text='N/A', 
                                          variable=self.var_check_vencimiento,
                                          command=self.actualizar_estado_fecha)
        self.ch_vencimiento.grid(row=6, column=2, sticky=SE, padx=5)

        self.grafico_temp = Button(self.frame_grafico, bg='white',
                                   width=57, pady=118, state='disabled')
        self.grafico_temp.grid(row=0, column=0, padx=0, pady=0, sticky='e')
        #-----FIN BOTONES-----#

        #-----TREEVIEW-----#
        self.tree = ttk.Treeview(frame_treeview)
        self.tree.grid(row=0, column=0, sticky='nsew')

        tree_scroll_vertical = Scrollbar(frame_treeview, orient="vertical",
                                         command=self.tree.yview)
        tree_scroll_vertical.grid(row=0, column=1, sticky='ns')

        self.tree.configure(yscrollcommand=tree_scroll_vertical.set)
        
        estilo = ttk.Style(frame_treeview)
        estilo.theme_use("default")
        estilo.configure("Treeview.Heading", 
                         font=('Calibri', 10, 'bold'), 
                         background='black', 
                         foreground='white')

        self.tree['column'] = ('col1', 'col2', 'col3', 'col4', 'col5', 
                               'col6', 'col7', 'col8', 'col9', 'col10')

        self.tree.column('#0', width=50, minwidth=50, stretch=NO) # id
        self.tree.column('col1', width=190, minwidth=50, stretch=NO) # Producto
        self.tree.column('col2', width=70, minwidth=50, stretch=NO) # Cantidad
        self.tree.column('col3', width=90, minwidth=50, stretch=NO) # Monto
        self.tree.column('col4', width=105, minwidth=50, stretch=NO) # Responsable
        self.tree.column('col5', width=125, minwidth=50, stretch=NO) # Subtotal
        self.tree.column('col6', width=115, minwidth=50, stretch=NO) # Rubro
        self.tree.column('col7', width=180, minwidth=50, stretch=NO) # Proveedor
        self.tree.column('col8', width=120, minwidth=50, stretch=NO) # Medio de Pago
        self.tree.column('col9', width=90, minwidth=50, stretch=NO) # Fecha
        self.tree.column('col10', width=100, minwidth=50, stretch=NO) # Vencimiento

        self.tree.heading('#0', text='Id')
        self.tree.heading('col1', text='Producto')
        self.tree.heading('col2', text='Cantidad')
        self.tree.heading('col3', text='Monto')
        self.tree.heading('col4', text='Responsable')
        self.tree.heading('col5', text='Subtotal')
        self.tree.heading('col6', text='Rubro')
        self.tree.heading('col7', text='Proveedor')
        self.tree.heading('col8', text='Medio de pago')
        self.tree.heading('col9', text='Fecha')
        self.tree.heading('col10', text='Vencimiento')
        #-----FIN TREEVIEW-----#
        #-----FIN WIDGETS-----#
        
        self.grafico_temp.destroy()
        self.crear_grafico(self.frame_grafico)
        self.actualizar_label_total_acumulado()
        self.cargar_total_acumulado()
        self.cargar_datos_en_treeview()
        self.root.mainloop()
