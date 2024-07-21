import ttkbootstrap as ttkb
import tkintermapview as mp

class Interface:

    window = ttkb.Window(themename="darkly")
    map_widget = mp.TkinterMapView(window, width=760, height=450, corner_radius=20)
    style = ttkb.Style()

    @classmethod
    def create_input(cls, text, labx=None, laby=None, inpx=None, inpy=None):
        cls.style.configure("TLabel", font=("Arial", 12), background="#202020", foreground="White")
        label = ttkb.Label(cls.window, text=text, style="TLabel")
        entry = ttkb.Entry(cls.window)
        label.place(x=labx, y=laby), entry.place(x=inpx, y=inpy)
        entry.bind('<FocusIn>', cls.on_entry_click), entry.bind('<FocusOut>', cls.on_focusout)
        return entry
    
    @classmethod
    def create_combobox(cls, options, label_text, labx=None, laby=None, comx=None, comy=None):
        cls.style.configure('TCombobox', font=("Arial", 12), background="#202020", foreground="White")
        label = ttkb.Label(cls.window, text=label_text, style="TLabel")
        combobox = ttkb.Combobox(cls.window, values=options, style="TCombobox", bootstyle="info")
        label.place(x=labx, y=laby), combobox.place(x=comx, y=comy)
        return combobox

    @classmethod
    def create_window(cls, main):
        # cls.window.configure(background="#202020")
        cls.window.title("Optimizador de rutas")
        cls.window.geometry("810x850")
        window_width = cls.window.winfo_reqwidth()
        position_right = int(cls.window.winfo_screenwidth()/2 - window_width/2 - 200)
        cls.window.geometry("+{}+50".format(position_right))

        country = cls.create_input("Pais a visitar:", labx=60, laby=30, inpx=60, inpy=60)
        state = cls.create_input("Estado a visitar:", labx=340, laby=30, inpx=340, inpy=60)
        city = cls.create_input("Ciudad a visitar:", labx=600, laby=30, inpx=600, inpy=60)
        days = cls.create_input("¿Cuantos dias estaras \n de visita?", labx=10, laby=140, inpx=60, inpy=200)
        max_places = cls.create_input("¿Cuantos lugares te gustaria \n visitar?", labx=265, laby=140, inpx=340, inpy=200)

        types = ["park", "museum", "restaurant", "bar", "cafe", "hotel", "hospital", 'landmarks', 'tourist attractions', 'famous places', 'historical sites']
        poi_type = cls.create_combobox(types, "¿Que tipo de lugar te gustaria \n visitar?", labx=545, laby=140, comx=600, comy=200)

        cls.style.configure("TButton", font=("Arial", 12))
        button = ttkb.Button(cls.window, text="Iniciar", width=10, bootstyle='success-outline',
                           command=lambda: main(country.get(), state.get(), city.get(), int(days.get()), int(max_places.get()), poi_type.get()),
                           )
        button.place(x=350, y=270)
        button.bind("<Enter>", cls.on_enter), button.bind("<Leave>", cls.on_leave)

        cls.map_widget.place(relx=0.5, rely=0.7, anchor='center')
        cls.map_widget.set_zoom(15)
        cls.map_widget.set_position(19.4326, -99.1332)

        cls.window.mainloop()
    
    @classmethod
    def on_entry_click(cls, event):
        event.widget.config(bootstyle='info')  # Cambia el estilo al hacer clic

    @classmethod
    def on_focusout(cls, event):
        event.widget.config(bootstyle='')  # Restablece el estilo cuando el foco se pierde
    
    @classmethod
    def on_enter(cls, event):
        event.widget.config(bootstyle='success')  # Cambia el estilo al pasar el ratón

    @classmethod
    def on_leave(cls, event):
        event.widget.config(bootstyle='success-outline')  # Restablece el estilo original al salir el ratón

    @classmethod
    def create_path(cls, route):
        cls.map_widget.delete_all_path()
        markers = []
        
        for i, place in enumerate(route):
            marker = cls.map_widget.set_marker(
                place[1], place[2], 
                text=f"{i+1}. {place[0]}", 
                text_color='black', 
                font='Candara 11 bold', 
                marker_color_outside='red', 
                marker_color_circle='brown'
            )
            markers.append((place[1], place[2]))
        
        # Crear la ruta conectando los puntos en orden
        cls.map_widget.set_path(markers, name="Tour_Route", color='blue', width=2)