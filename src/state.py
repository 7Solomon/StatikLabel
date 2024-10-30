class SharedData:
    def __init__(self):
        self.data = {}
        self.observers = []
    
    def add_observer(self, observer):
        self.observers.append(observer)
    
    def update_data(self, key, value):
        self.data[key] = value
        self.notify_observers()

    def get_label_data(self):
        return {
                'objects':self.data.get('objects', {}),
                'connections':self.data.get('connections', [])
                }
    def get_normalized_system(self):
        return {
                'normalized_objects':self.data.get('normalized_objects', {}),
                'normalized_connections':self.data.get('normalized_connections', [])
                }
    
    def notify_observers(self):
        for update_function in self.observers:
            update_function()
