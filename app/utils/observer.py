"""
observer.py
    Este módulo contiene las clases Observer y Observable que implementan el patrón de diseño Observer.
    La clase Observer define un método update que se llama cuando el estado de un objeto Observable cambia.
    La clase Observable mantiene una lista de observadores y notifica a todos los observadores cuando cambia su estado.
"""

class Observer:
    def update(self, observable, *args, **kwargs):
        """
        Método que se llama cuando el estado de un objeto Observable cambia.
        
        :param observable: objeto Observable que ha cambiado.
        :param args: argumentos adicionales.
        :param kwargs: argumentos con nombre.
        :return: None
        """
        
        pass

class Observable:
    def __init__(self):
        """
        Inicializa la lista de observadores.
        
        :return: None
        """
        
        self._observers = []

    def add_observer(self, observer):
        """
        Agrega un observador a la lista de observadores.
        
        :param observer: observador a agregar.
        :return: None
        """
        
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer):
        """
        Elimina un observador de la lista de observadores.
        
        :param observer: observador a eliminar.
        :return: None
        """
        
        try:
            self._observers.remove(observer)
        except ValueError:
            pass

    def notify_observers(self, *args, **kwargs):
        """
        Notifica a todos los observadores que el estado del objeto ha cambiado.
        
        :param args: argumentos adicionales.
        :param kwargs: argumentos con nombre.
        :return: None
        """
        
        for observer in self._observers:
            observer.update(self, *args, **kwargs)
