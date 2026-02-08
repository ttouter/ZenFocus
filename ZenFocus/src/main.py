import customtkinter as ctk
import config  # Importa tus colores y tiempos desde src/config.py
import math

class ZenFocusApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Configuración de la Ventana ---
        self.title("ZenFocus")
        self.geometry("400x500")
        self.resizable(False, False)
        
        # Color de fondo definido en config.py
        self.configure(fg_color=config.COLOR_BACKGROUND)

        # Configurar el grid para centrar los elementos
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)

        # --- Variables de Estado ---
        self.time_left = config.POMODORO_TIME
        self.timer_running = False
        self.timer_id = None

        # --- Crear Interfaz ---
        self.crear_widgets()
        self.actualizar_reloj()  # Mostrar el tiempo inicial

    def crear_widgets(self):
        # 1. Título
        self.label_titulo = ctk.CTkLabel(
            self, 
            text="ZenFocus", 
            font=("Roboto", 24, "bold"),
            text_color=config.COLOR_PRIMARY
        )
        self.label_titulo.grid(row=0, column=0, pady=(20, 10))

        # 2. Selector de Modo (Enfoque / Descanso)
        self.selector_modo = ctk.CTkSegmentedButton(
            self,
            values=["Enfoque", "Descanso"],
            command=self.cambiar_modo,
            selected_color=config.COLOR_PRIMARY,
            selected_hover_color="#155a8a",  # Tono más oscuro
            font=("Roboto", 14)
        )
        self.selector_modo.set("Enfoque")  # Valor por defecto
        self.selector_modo.grid(row=1, column=0, pady=10)

        # 3. El Reloj (Texto grande)
        self.label_tiempo = ctk.CTkLabel(
            self,
            text="00:00",
            font=("Roboto", 80, "bold"),
            text_color="white"
        )
        self.label_tiempo.grid(row=2, column=0, pady=20)

        # 4. Botón Iniciar/Pausar
        self.boton_start = ctk.CTkButton(
            self,
            text="Iniciar",
            command=self.toggle_timer,
            fg_color=config.COLOR_PRIMARY,
            hover_color="#155a8a",
            width=140,
            height=40,
            font=("Roboto", 16, "bold")
        )
        self.boton_start.grid(row=3, column=0, pady=10)

        # 5. Botón Reiniciar
        self.boton_reset = ctk.CTkButton(
            self,
            text="Reiniciar",
            command=self.reset_timer,
            fg_color="transparent",
            border_width=2,
            border_color=config.COLOR_ACCENT,
            text_color=config.COLOR_ACCENT,
            hover_color=config.COLOR_BACKGROUND,
            width=140,
            height=40,
            font=("Roboto", 14)
        )
        self.boton_reset.grid(row=4, column=0, pady=(0, 20))

    def cambiar_modo(self, valor):
        """Se ejecuta al cambiar entre Enfoque y Descanso en el selector"""
        # Detenemos y reseteamos el temporizador según el nuevo modo
        self.reset_timer()

    def toggle_timer(self):
        """Inicia o pausa el temporizador"""
        if self.timer_running:
            # PAUSAR
            self.timer_running = False
            self.boton_start.configure(text="Continuar")
            if self.timer_id:
                self.after_cancel(self.timer_id)
        else:
            # INICIAR
            self.timer_running = True
            self.boton_start.configure(text="Pausar")
            self.contar()

    def contar(self):
        """Lógica recursiva del conteo"""
        if self.time_left > 0 and self.timer_running:
            self.time_left -= 1
            self.actualizar_reloj()
            # Se llama a sí misma en 1000 ms (1 segundo)
            self.timer_id = self.after(1000, self.contar)
        elif self.time_left == 0:
            self.timer_running = False
            self.boton_start.configure(text="Iniciar")
            # Opcional: Sonido de alarma aquí
            self.time_left = config.POMODORO_TIME if self.selector_modo.get() == "Enfoque" else config.SHORT_BREAK
            self.actualizar_reloj()

    def reset_timer(self):
        """Reinicia el tiempo según el modo seleccionado"""
        self.timer_running = False
        if self.timer_id:
            self.after_cancel(self.timer_id)
        
        modo_actual = self.selector_modo.get()
        
        if modo_actual == "Enfoque":
            self.time_left = config.POMODORO_TIME
            nuevo_color = config.COLOR_PRIMARY
            self.boton_start.configure(fg_color=config.COLOR_PRIMARY, hover_color="#155a8a")
            self.selector_modo.configure(selected_color=config.COLOR_PRIMARY, selected_hover_color="#155a8a")
        else:
            self.time_left = config.SHORT_BREAK
            nuevo_color = "#4CAF50" # Verde para descanso
            self.boton_start.configure(fg_color=nuevo_color, hover_color="#388E3C")
            self.selector_modo.configure(selected_color=nuevo_color, selected_hover_color="#388E3C")
            
        self.boton_start.configure(text="Iniciar")
        self.actualizar_reloj()

    def actualizar_reloj(self):
        """Actualiza el texto del label con formato MM:SS"""
        minutos = math.floor(self.time_left / 60)
        segundos = self.time_left % 60
        self.label_tiempo.configure(text=f"{minutos:02d}:{segundos:02d}")

if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    app = ZenFocusApp()
    app.mainloop()