from mvc.model import Model
from mvc.view import View
from mvc.controller import Controller

def main():
    model = Model()
    controller = Controller(model)
    view = View(controller)
    
    controller.set_view(view)
    view.create_view()

if __name__ == "__main__":
    main()
