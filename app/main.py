"""
main.py
    Este archivo es el punto de entrada para ejecutar la aplicación.
"""

from mvc.model import Model
from mvc.view import View, GestorTema
from mvc.controller import Controller


def main():
    """
    Función principal para ejecutar la aplicación.
    """
    
    model = Model()
    model.initialize_database()
    
    controller = Controller(model)
    view = View(controller)  # La vista se inicia con el controlador.

    # Creacion y configuracion del gestor de temas.
    gestor_tema = GestorTema()
    gestor_tema.add_observer(view)  # Agrega a la vista como observador a los cambios de tema.
    view.setear_gestor_tema(gestor_tema)  # Setea al gestor de temas a la vista.

    controller.set_view(view)
    view.create_view()


if __name__ == "__main__":
    main()
