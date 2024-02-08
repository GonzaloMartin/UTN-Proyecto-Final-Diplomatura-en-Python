import datetime
import locale
import re

from tkinter.messagebox import showinfo

from view import(cal_fecha,
                 boton_cancelar,
                 cb_rubro,
                 cb_medio_pago,
                 cb_responsable,
                 boton_confirmar,
                 crear_grafico,
                 e_vencimiento,
                 frame_grafico,
                 l_total,
                 root,
                 estado,
                 tree,
                 var_monto,
                 var_rubro,
                 var_check_vencimiento,
                 var_fecha,
                 var_vencimiento,
                 var_medio_pago,
                 var_producto,
                 var_cantidad,
                 var_responsable,
                 var_consulta,
                 var_proveedor,
                 var_total)

from model import(consulta_bd,
                  modificacion_bd,
                  conectar_base_de_datos,
                  alta_bd,
                  baja_bd)

#-----------------------------INICIO CONTROLADOR-----------------------------#

class ControllerClass:

    #-----ABMC-----#
    def alta():
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

            if valores['cantidad'] <= 0 or valores['monto'] <= 0:
                actualizar_estado_bar("Cantidad y monto deben ser números positivos.")
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
        compra_id = tree.focus()
        if not compra_id:
            showinfo("Info", "Debe seleccionar un registro para dar de Baja.")
            actualizar_estado_bar("Debe seleccionar un registro para dar de Baja.")
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
        
        tree.delete(compra_id)
        cargar_total_acumulado()
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
        
        for widget in frame_grafico.winfo_children():
            widget.destroy()  # Borrar graficos anteriores
            crear_grafico(frame_grafico)  # Grafico actualiazado
            

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


    def obtener_mes_actual():
        return datetime.datetime.now().month

    def obtener_mes_palabra_actual():
        locale.setlocale(locale.LC_TIME, '')  # Devuelva el mes en español
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

    
        
#-------------------------------FIN CONTROLADOR------------------------------#