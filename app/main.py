"""
main.py
    Este archivo es el punto de entrada para ejecutar la aplicación.
"""

from mvc.model import Model
from mvc.view import View
from mvc.controller import Controller


def main():
    """
    Función principal para ejecutar la aplicación.
    """
    
    model = Model()
    model.initialize_database()
    
    controller = Controller(model)
    view = View(controller)
    
    controller.set_view(view)
    view.create_view()


if __name__ == "__main__":
    main()
