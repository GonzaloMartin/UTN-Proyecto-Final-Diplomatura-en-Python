"""
main.py
    Este archivo es el punto de entrada para ejecutar la aplicación.
"""

from mvc.model import Model
from mvc.view import View, ThemeManager
from mvc.controller import Controller


def main():
    """
    Función principal para ejecutar la aplicación.
    """
    
    model = Model()
    model.initialize_database()
    
    controller = Controller(model)
    view = View(controller)  # View initializes with controller

    # Create and configure ThemeManager
    theme_manager = ThemeManager()
    theme_manager.add_observer(view)  # Add view as an observer to theme changes
    view.set_theme_manager(theme_manager)  # Set theme manager to view

    controller.set_view(view)
    view.create_view()  # This should setup the root and other UI components


if __name__ == "__main__":
    main()
