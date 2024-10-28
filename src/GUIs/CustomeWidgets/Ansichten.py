from PyQt5.QtWidgets import QWidget, QVBoxLayout, QRadioButton, QButtonGroup
class Ansichten(QWidget):
    def __init__(self, elements=None):
        super().__init__()
        self.elements = elements or [{'name': 'Nothing defined', 'function': None}]
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout(self)
        
        # Create a button group to manage radio buttons
        self.button_group = QButtonGroup(self)
        
        # Create radio buttons and connect them properly
        for i, element in enumerate(self.elements):
            if element:
                button = QRadioButton(element.get('name', 'Nothing defined'))
                self.button_group.addButton(button, i)
                self.layout.addWidget(button)
        
        # Connect the button group's signal to handle switching
        self.button_group.buttonClicked.connect(self._handle_button_clicked)
        
        # Select the first button by default
        if self.elements and len(self.elements) > 0:
            first_button = self.button_group.button(0)
            if first_button:
                first_button.setChecked(True)

    def _handle_button_clicked(self, button):
        button_id = self.button_group.id(button)
        if 0 <= button_id < len(self.elements):
            function = self.elements[button_id].get('function')
            if function:
                function()