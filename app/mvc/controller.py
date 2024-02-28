import datetime
import locale
import re

from tkinter.messagebox import showinfo

from utils.utils import obtener_mes_actual

#-----------------------------INICIO CONTROLADOR-----------------------------#

class Controller:
    
    def __init__(self, model):
        self.model = model
        self.view = None
    
    def set_view(self, view):
        self.view = view
    
    def get_obtener_datos_grafico(self):
        mes_actual = obtener_mes_actual()
        return self.model.obtener_datos_grafico(mes_actual)
    
    def get_consulta_bd(self, mes=None):
        return self.model.consulta_bd(mes)
    
        
    #-----ABMC-----#
    def alta(self):
        self.view.var_fecha.set(self.view.cal_fecha.get_date().strftime("%Y-%m-%d"))
        
        if self.view.var_check_vencimiento.get():
            vencimiento_value = 'N/A'
        else:
            due_date = self.view.e_vencimiento.get_date()
            vencimiento_value = due_date.strftime("%Y-%m-%d")

        self.view.var_vencimiento.set(vencimiento_value)        

        if (not self.view.var_producto.get() or
                not self.view.var_cantidad.get() or
                not self.view.var_monto.get() or
                not self.view.cb_responsable.get()):
            self.view.actualizar_estado_bar("Se deben completar todos los campos de ingreso")
            showinfo("Info", "Se deben completar todos los campos de ingreso")
            self.cancelar()
            return

        valores = {
            'monto': float(self.view.var_monto.get()),
            'producto': self.view.var_producto.get(),
            'rubro': self.view.cb_rubro.get(),
            'fecha': self.view.cal_fecha.get_date().strftime("%Y-%m-%d"),
            'proveedor': self.view.var_proveedor.get(),
            'medio_pago': self.view.cb_medio_pago.get(),
            'responsable': self.view.cb_responsable.get(),
            'cantidad': int(self.view.var_cantidad.get()),
            'vencimiento': vencimiento_value
        }

        for valor in valores.values():
            if not valor:
                showinfo("Info", "Todos los campos de alta deben tener contenido.")
                self.view.actualizar_estado_bar("Todos los campos de alta deben tener contenido.")
                self.view.cancelar()
                return

        if valores['cantidad'] <= 0 or valores['monto'] <= 0:
            self.view.actualizar_estado_bar("Cantidad y monto deben ser números positivos.")
            return
        
        ultimo_id = self.model.alta_bd(valores)
        # ultimo_id = alta_bd(conn, valores)

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
        compra_id = self.view.tree.focus()
        if not compra_id:
            showinfo("Info", "Debe seleccionar un registro para dar de Baja.")
            self.view.actualizar_estado_bar("Debe seleccionar un registro para dar de Baja.")
            self.view.cancelar()
            return
        
        id_bd_str = self.view.tree.item(compra_id, 'text')

        if re.match(r'^\d+$', id_bd_str): # Enteros >= 0
            id_bd = int(id_bd_str)
        else:
            showinfo("Error",  "El ID no es un número válido.")
            self.view.actualizar_estado_bar("El ID no es un número válido.")
            self.view.cancelar()
            return

        self.model.baja_bd(id_bd)
        
        self.view.tree.delete(compra_id)
        self.view.cargar_total_acumulado()
        self.view.actualizar_estado_bar("Se dio de baja el registro con ID: " + str(id_bd))
        self.confirmar()
        
        
    def modificacion(self):
        compra_id = self.view.tree.focus()
        if not compra_id:
            showinfo("Info", "Debe seleccionar un registro para Modificar.")
            self.view.actualizar_estado_bar("Debe seleccionar un registro para Modificar.")
            self.cancelar()
            return
        
        id_bd = int(self.view.tree.item(compra_id, 'text'))
        
        valores = self.view.tree.item(compra_id, 'values')
        self.view.var_producto.set(valores[0])
        self.view.var_cantidad.set(valores[1])
        self.view.var_monto.set(valores[2])
        self.view.var_fecha.set(valores[8])
        self.view.cb_responsable.set(valores[3])
        self.view.cb_rubro.set(valores[5])
        self.view.cb_medio_pago.set(valores[7])
        self.view.var_proveedor.set(valores[6])
        self.view.var_vencimiento.set(valores[9])
        
        self.view.actualizar_estado_bar("Modificando registro ID: " + str(id_bd))
        
        self.view.boton_confirmar.config(state='normal', command=lambda: self.aplicar_modificacion(compra_id, id_bd))
        self.view.boton_cancelar.config(state='normal')


    def consulta(self):
        termino_busqueda = self.view.var_consulta.get()
        # Si término_busqueda contiene "*", se muestran todos los registros
        if "*" in termino_busqueda: termino_busqueda = ""
        
        registros = self.model.consulta_bd()

        # Crea objeto regex desde 'termino_busqueda' NO sensible a mayúsculas
        regex = re.compile(termino_busqueda, re.IGNORECASE) 

        registros_filtrados = []
        for row in registros:
            row_str = ' '.join(map(str, row))  # Registro -> cadena
            if regex.search(row_str):
                registros_filtrados.append(row)

        for i in self.view.tree.get_children():
            self.view.tree.delete(i)

        for row in registros_filtrados:
            self.view.tree.insert('', 'end', text=str(row[0]), values=row[1:])

        if termino_busqueda == "": # Si no se especifica un término de búsqueda
            self.view.actualizar_estado_bar(f"Se muestran todos los registros.")
        else:
            self.view.actualizar_estado_bar(f"Resultados de la búsqueda para: {termino_busqueda}")

        self.view.cargar_total_acumulado()
    #-----FIN ABMC-----#

    def validar_campos(self):
        """
        Valida que todos los campos del formulario estén completos.
        :return: True si todos los campos están completos, False en caso contrario.        
        """
        
        campos_var = [self.view.var_producto,
                      self.view.var_cantidad,
                      self.view.var_monto,
                      self.view.var_proveedor,
                      self.view.var_fecha,
                      self.view.var_vencimiento]
        campos_cb = [self.view.cb_responsable,
                     self.view.cb_rubro,
                     self.view.cb_medio_pago]
        
        for var in campos_var:
            # if (type(var) == str or type(var) == int) and not var:
            if isinstance(var, (str, int)) and not var:
                return False

        for cb in campos_cb:
            if not cb:
                return False

        return True
        
    def preparar_alta(self):
        self.view.boton_confirmar.config(state='normal', command=self.alta)
        self.view.boton_cancelar.config(state='normal')


    def preparar_baja(self):
        self.view.boton_confirmar.config(state='normal', command=self.baja)
        self.view.boton_cancelar.config(state='normal')


    def confirmar(self):
        # La acción se define en cada caso (alta, baja, modificacion)
        self.view.boton_confirmar.config(state='disabled')
        self.view.boton_cancelar.config(state='disabled')
        
        for widget in self.view.frame_grafico.winfo_children():
            widget.destroy()  # Borrar graficos anteriores
            self.view.crear_grafico(self.view.frame_grafico)  # Grafico actualiazado
            
    def cancelar(self):
        self.view.boton_confirmar.config(state='disabled', command=None)
        self.view.boton_cancelar.config(state='disabled')
        self.view.limpiar_formulario()
        
    def aplicar_modificacion(self, compra_id, id_bd):
        """
        Aplica la modificación de un registro en la base de datos.
        :param compra_id: ID del registro a modificar en el Treeview.
        :param id_bd: ID del registro a modificar en la base de datos.
        :return: None
        """
        
        if not self.validar_campos():
            self.view.actualizar_estado_bar("Todos los campos deben estar llenos.")
            showinfo("Info", "Todos los campos deben estar llenos.")
            self.cancelar()
            return

        nuevo_valor = {
            'producto': self.view.var_producto.get(),
            'cantidad': int(self.view.var_cantidad.get()),
            'monto': float(self.view.var_monto.get()),
            'responsable': self.view.cb_responsable.get(),
            'rubro': self.view.cb_rubro.get(),
            'proveedor': self.view.var_proveedor.get(),
            'medio_pago': self.view.cb_medio_pago.get(),
            'fecha': self.view.var_fecha.get(),
            'vencimiento': self.view.var_vencimiento.get()
        }

        self.model.modificacion_bd(id_bd, nuevo_valor)

        if self.view.tree.exists(compra_id):
            self.view.tree.item(compra_id, values=(
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

        self.view.actualizar_estado_bar("Registro modificado con ID: " + str(id_bd))
        self.view.cargar_total_acumulado()
        self.view.limpiar_formulario()
        self.confirmar()

    def obtener_mes_palabra_actual(self):
        locale.setlocale(locale.LC_TIME, '')  # Devuelva el mes en español
        mes_actual = obtener_mes_actual()
        mes_actual_str = datetime.datetime.strptime(str(mes_actual), "%m").strftime("%B")
        return mes_actual_str.capitalize()

    def obtener_total_acumulado(self):
        mes_actual = obtener_mes_actual()
        registros = self.model.consulta_bd(mes=mes_actual)
        
        total_acumulado = 0
        for row in registros:
            total_acumulado += row[0]
            
        return total_acumulado



#-------------------------------FIN CONTROLADOR------------------------------#