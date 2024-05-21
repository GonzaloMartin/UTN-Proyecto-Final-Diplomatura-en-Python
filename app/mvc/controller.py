"""
controller.py
    Este módulo contiene la clase Controller, que se encarga de manejar la lógica de la aplicación.
    Se vincula con la vista y el modelo para realizar las operaciones necesarias.
    También referencia a la clase Model para realizar las operaciones en la base de datos.
    Así mismo, referencia a la clase View para realizar las operaciones en la interfaz gráfica.
    De igual manera se encarga de manejar las operaciones de alta, baja, modificación y consulta de registros.
    Usa funciones reutilizables de utils.py para obtener el mes actual y reformatear fechas.
"""

import datetime
import locale
import re

from tkinter.messagebox import showinfo

from utils.utils import obtener_mes_actual, reformatear_fecha
from utils.validators import DataValidator


class Controller:


    def __init__(self, model):
        """
        Constructor de la clase Controller.
        
        :param self: Objeto Controller.
        :param model: Objeto Model.
        """

        self.model = model
        self.view = None


    def set_view(self, view):
        """
        Setea la vista para el controller.
        
        :param self: Objeto Controller.
        :param view: Vista a setear.
        """
        
        self.view = view


    def get_obtener_datos_grafico(self):
        """
        Obtiene los datos para el gráfico.
        Previamente se obtiene el mes actual desde el sistema.
        
        :param self: Objeto Controller.
        :return: Lista con los datos para el gráfico.
        """
        
        mes_actual = obtener_mes_actual()
        return self.model.obtener_datos_grafico(mes_actual)


    def get_consulta_bd(self, mes=None):
        """
        Obtiene los registros de la base de datos.
        
        :param self: Objeto Controller.
        :param mes: Mes a consultar (Valor opcional).
        :return: Registros de la base de datos.
        """
        return self.model.consulta_bd(mes)


    # ABMC
    def alta(self):
        """
        Da de alta un registro en la base de datos.
        Controla que todos los campos del formulario estén completos.
        El alta se aplica en la base de datos y en el Treeview.
        
        :param self: Objeto Controller.
        :return: None
        """
        
        self.view.var_fecha.set(self.view.cal_fecha.get_date().strftime("%Y-%m-%d"))
        
        if self.view.var_check_vencimiento.get():
            vencimiento_value = 'N/A'
        else:
            due_date = self.view.e_vencimiento.get_date()
            vencimiento_value = due_date.strftime("%Y-%m-%d")

        self.view.var_vencimiento.set(vencimiento_value)

        valores = {
            'monto': self.view.var_monto.get(),
            'producto': self.view.var_producto.get(),
            'rubro': self.view.cb_rubro.get(),
            'fecha': self.view.cal_fecha.get_date().strftime("%Y-%m-%d"),
            'proveedor': self.view.var_proveedor.get(),
            'medio_pago': self.view.cb_medio_pago.get(),
            'responsable': self.view.cb_responsable.get(),
            'cantidad': self.view.var_cantidad.get(),
            'vencimiento': vencimiento_value
        }

        # Validar campos requeridos y formatos
        resultado, mensaje = DataValidator.validar_campos_requeridos(**valores)
        if not resultado:
            self.view.actualizar_estado_bar(mensaje)
            showinfo("Error de Validación", mensaje)
            self.cancelar()
            return

        # Validar monto y cantidad como números positivos
        resultado, mensaje = DataValidator.validar_numero_positivo(valores['monto'])
        if not resultado:
            self.view.actualizar_estado_bar(mensaje)
            return

        resultado, mensaje = DataValidator.validar_numero_positivo(valores['cantidad'])
        if not resultado:
            self.view.actualizar_estado_bar(mensaje)
            return
        
        resultado, mensaje = DataValidator.validar_regex(nuevo_valor=valores)
        if not resultado:
            self.view.actualizar_estado_bar(mensaje)
            return

        # Convertir a tipos adecuados para evitar errores en la inserción
        valores['monto'] = float(valores['monto'])
        valores['cantidad'] = int(valores['cantidad'])

        # Insertar en la base de datos
        ultimo_id = self.model.alta_bd(valores)

        subtotal_acumulado = round(valores['cantidad'] * valores['monto'], 2)

        self.view.tree.insert('',
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

        self.view.cargar_total_acumulado()
        self.view.actualizar_estado_bar("Se dio de alta el registro con ID: " + str(ultimo_id))
        self.view.limpiar_formulario()
        self.confirmar()


    def baja(self):
        """
        Da de baja un registro en la base de datos.
        La baja se aplica en la base de datos y en el Treeview.
        
        :param self: Objeto Controller.
        :return: None
        """
        
        compra_id = self.view.tree.focus()
        if not compra_id:
            showinfo("Info", "Debe seleccionar un registro para dar de Baja.")
            self.view.actualizar_estado_bar("Debe seleccionar un registro para dar de Baja.")
            self.view.cancelar()
            return
        
        id_bd_str = self.view.tree.item(compra_id, 'text')

        # Validar que el ID es un número positivo
        resultado, mensaje = DataValidator.validar_numero_positivo(id_bd_str)
        if not resultado:
            showinfo("Error", mensaje)
            self.view.actualizar_estado_bar(mensaje)
            self.view.cancelar()
            return
        
        id_bd = int(id_bd_str)  # Convertir el ID a entero después de validar

        # Proceder con la baja en la base de datos
        self.model.baja_bd(id_bd)
        
        self.view.tree.delete(compra_id)
        self.view.cargar_total_acumulado()
        self.view.actualizar_estado_bar(f"Se dio de baja el registro con ID: {id_bd}")
        self.confirmar()


    def modificacion(self):
        """
        Prepara el formulario para la modificación de un registro.
        Una vez completado el formulario, se aplica la modificación.
        La modificación se aplica en la base de datos y en el Treeview.
        
        :param self: Objeto Controller.
        :return: None
        """
        
        compra_id = self.view.tree.focus()
        if not compra_id:
            showinfo("Info", "Debe seleccionar un registro para Modificar.")
            self.view.actualizar_estado_bar("Debe seleccionar un registro para Modificar.")
            self.cancelar()
            return

        id_bd_str = self.view.tree.item(compra_id, 'text')

        # Validar que el ID es un número positivo
        resultado, mensaje = DataValidator.validar_numero_positivo(id_bd_str)
        if not resultado:
            showinfo("Error", mensaje)
            self.view.actualizar_estado_bar(mensaje)
            self.cancelar()
            return

        id_bd = int(id_bd_str)  # Convertir el ID a entero después de validar

        valores = self.view.tree.item(compra_id, 'values')
        self.view.var_producto.set(valores[0])
        self.view.var_cantidad.set(valores[1])
        self.view.var_monto.set(valores[2])
        self.view.cal_fecha.set_date(reformatear_fecha(valores[8]))
        self.view.cb_responsable.set(valores[3])
        self.view.cb_rubro.set(valores[5])
        self.view.cb_medio_pago.set(valores[7])
        self.view.var_proveedor.set(valores[6])

        if valores[9] != 'N/A':
            self.view.var_check_vencimiento.set(False)
            self.view.e_vencimiento.set_date(reformatear_fecha(valores[9]))
            self.view.e_vencimiento.config(state='normal')
        else:
            self.view.var_check_vencimiento.set(True)
            self.view.e_vencimiento.config(state='disabled')
        
        self.view.actualizar_estado_bar("Modificando registro ID: " + str(id_bd))
        
        self.view.boton_confirmar.config(state='normal', command=lambda: self.aplicar_modificacion(compra_id, id_bd))
        self.view.boton_cancelar.config(state='normal')


    def consulta(self):
        """
        Realiza una consulta en la base de datos.
        Si el término de búsqueda es "*", se muestran todos los registros.
        Si el término de búsqueda es un string, se muestran los registros que contengan ese string.
        
        :param self: Objeto Controller.
        :return: None
        """
        
        termino_busqueda = self.view.var_consulta.get().strip()
        # Si término_busqueda contiene "*", se muestran todos los registros
        if "*" in termino_busqueda:
            termino_busqueda = ""
        
        registros = self.model.consulta_bd()

        if termino_busqueda:  # Solo compila la regex si hay un término a buscar
            # Crea objeto regex desde 'termino_busqueda' NO sensible a mayúsculas
            regex = re.compile(termino_busqueda, re.IGNORECASE)

            registros_filtrados = [row for row in registros if regex.search(' '.join(map(str, row)))]
        else:
            registros_filtrados = registros  # Mostrar todos los registros si no hay término de búsqueda

        # Limpiar el Treeview antes de insertar nuevos registros
        for i in self.view.tree.get_children():
            self.view.tree.delete(i)

        # Insertar registros filtrados en el Treeview
        for row in registros_filtrados:
            self.view.tree.insert('', 'end', text=str(row[0]), values=row[1:])

        # Actualizar la barra de estado con información relevante
        if not registros_filtrados:
            self.view.actualizar_estado_bar("No se encontraron registros que coincidan con la búsqueda.")
        elif termino_busqueda:
            self.view.actualizar_estado_bar(f"Resultados de la búsqueda para: {termino_busqueda}")
        else:
            self.view.actualizar_estado_bar("Se muestran todos los registros.")

        self.view.cargar_total_acumulado()
    # FIN ABMC


    def preparar_alta(self):
        """
        Prepara el formulario para el alta de un registro.
        
        :param self: Objeto Controller.
        :return: None
        """
        
        self.view.boton_confirmar.config(state='normal', command=self.alta)
        self.view.boton_cancelar.config(state='normal')


    def preparar_baja(self):
        """
        Prepara el formulario para la baja de un registro.
        
        :param self: Objeto Controller.
        :return: None
        """
        
        self.view.boton_confirmar.config(state='normal', command=self.baja)
        self.view.boton_cancelar.config(state='normal')


    def confirmar(self):
        """
        Confirma la acción realizada (alta, baja, modificación).
        Maneja el estado de los botones de confirmar y cancelar.
        Refresca el gráfico y el Treeview para mostrar los cambios.
        
        :param self: Objeto Controller.
        :return: None
        """

        self.view.boton_confirmar.config(state='disabled')
        self.view.boton_cancelar.config(state='disabled')
        
        for widget in self.view.frame_grafico.winfo_children():
            widget.destroy()  # Borrar graficos anteriores
            self.view.crear_grafico(self.view.frame_grafico)  # Grafico actualiazado


    def cancelar(self):
        """
        Cancela la acción realizada (alta, baja, modificación).
        Maneja el estado de los botones de confirmar y cancelar.
        
        :param self: Objeto Controller.
        :return: None
        """
        
        self.view.boton_confirmar.config(state='disabled', command=None)
        self.view.boton_cancelar.config(state='disabled')
        self.view.limpiar_formulario()


    def aplicar_modificacion(self, compra_id, id_bd):
        """
        Aplica la modificación de un registro en la base de datos.
        Controla que todos los campos del formulario estén completos.
        
        :param self: Objeto Controller.
        :param compra_id: ID del registro a modificar en the Treeview.
        :param id_bd: ID del registro a modificar en la base de datos.
        :return: None
        """
        
        nuevo_valor = {
            'producto': self.view.var_producto.get(),
            'cantidad': self.view.var_cantidad.get(),
            'monto': self.view.var_monto.get(),
            'responsable': self.view.cb_responsable.get(),
            'rubro': self.view.cb_rubro.get(),
            'proveedor': self.view.var_proveedor.get(),
            'medio_pago': self.view.cb_medio_pago.get(),
            'fecha': self.view.cal_fecha.get_date().strftime("%Y-%m-%d"),  # Ensure proper date formatting
            'vencimiento': self.view.e_vencimiento.get_date().strftime("%Y-%m-%d") if not self.view.var_check_vencimiento.get() else 'N/A'
        }
        
         # Validate each field using DataValidator
        error_messages = []
        """for field, value in nuevo_valor.items():
            if field in ['monto', 'cantidad'] and not DataValidator.validar_numero_positivo(value)[0]:
                error_messages.append(DataValidator.validar_numero_positivo(value)[1])"""
        
        if not DataValidator.validar_regex(nuevo_valor=nuevo_valor)[0]:
            error_messages.append(DataValidator.validar_regex(nuevo_valor=nuevo_valor)[1])


        if error_messages:
            error_message = "Error: " + ", ".join(error_messages)
            self.view.actualizar_estado_bar(error_message)
            showinfo("Errores de validación", error_message)
            self.cancelar()
            return
        
        self.model.modificacion_bd(id_bd, nuevo_valor)

        subtotal_acumulado = round(float(nuevo_valor['cantidad']) * float(nuevo_valor['monto']), 2)
        
        if self.view.tree.exists(compra_id):
            self.view.tree.item(compra_id, values=(
                nuevo_valor['producto'],
                nuevo_valor['cantidad'],
                nuevo_valor['monto'],
                nuevo_valor['responsable'],
                f"{subtotal_acumulado:.2f}",  # Subtotal
                nuevo_valor['rubro'],
                nuevo_valor['proveedor'],
                nuevo_valor['medio_pago'],
                nuevo_valor['fecha'],
                nuevo_valor['vencimiento']
            ))

        self.view.actualizar_estado_bar("Registro modificado con ID: " + str(id_bd))
        self.view.cargar_total_acumulado()
        self.view.limpiar_formulario()
        self.confirmar()


    def obtener_mes_palabra_actual(self):
        """
        Obtiene el mes actual en formato palabra.
        Para esta entrega se devuelve el mes en español.
        
        :param self: Objeto Controller.
        :return: Mes actual en formato palabra.
        """
        
        locale.setlocale(locale.LC_TIME, '')  # Devuelva el mes en español
        mes_actual = obtener_mes_actual()
        mes_actual_str = datetime.datetime.strptime(str(mes_actual), "%m").strftime("%B")
        return mes_actual_str.capitalize()


    def obtener_total_acumulado(self):
        """
        Obtiene el total acumulado del mes actual.
        El cálculo se realiza en base a los registros de la base de datos.
        
        :param self: Objeto Controller.
        :return: Total acumulado del mes actual.
        """
        
        mes_actual = obtener_mes_actual()
        registros = self.model.consulta_bd(mes=mes_actual)
        
        total_acumulado = 0
        for row in registros:
            total_acumulado += row[0]
            
        return total_acumulado
