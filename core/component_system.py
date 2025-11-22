class UIComponent:
    pass

class Component:
    pass

class Container:
    def __init__(self, component_id=None):
        self.id = component_id
        self.children = []
        self._mounted = False
        
    def get_children(self):
        return self.children.copy()
        
    def add_child(self, child):
        self.children.append(child)
        child.parent = self
        return child
        
    def remove_child(self, child):
        if child in self.children:
            self.children.remove(child)
            child.parent = None
            return True
        return False
        
    def clear_children(self):
        self.children.clear()
        
    def count_children(self, recursive=True):
        return len(self.children)
        
    def set_size(self, width, height):
        self.width = width
        self.height = height
        return self
        
    def set_property(self, key, value):
        setattr(self, key, value)
        return self
        
    def trigger_event(self, event_type, event_data=None):
        return True

class Text:
    def __init__(self, component_id=None):
        self.id = component_id
        self._mounted = False
    
    def set_text(self, text):
        self.text = text
        return self
        
    def set_position(self, x, y):
        self.x = x
        self.y = y
        return self
        
    def set_property(self, key, value):
        setattr(self, key, value)
        return self

class Button:
    def __init__(self, component_id=None, text=""):
        self.id = component_id
        self.text = text
        self._mounted = False
        self.parent = None
        
    def set_text(self, text):
        self.text = text
        return self
        
    def set_position(self, x, y):
        self.x = x
        self.y = y
        return self
        
    def set_size(self, width, height):
        self.width = width
        self.height = height
        return self
        
    def set_on_click(self, handler):
        self.on_click_handler = handler
        return self
        
    def trigger_event(self, event_type, event_data=None):
        if event_type == "mouse_up" and hasattr(self, "on_click_handler"):
            self.on_click_handler(self)
        return True

class RootComponent(Container):
    def __init__(self, width=800, height=600, background_color=None):
        super().__init__("root")
        self.width = width
        self.height = height
        self.background_color = background_color
        self._mounted = True
        
    def is_dirty(self):
        return True

def mount_component_tree(root):
    root._mounted = True
    for child in root.get_children():
        mount_component_tree(child)

def unmount_component_tree(root):
    root._mounted = False
    for child in root.get_children():
        unmount_component_tree(child)