import customtkinter as ctk
import pygame
import os
from logic.gamification import GamificationEngine
from ui.components.breathing_halo import BreathingHalo # Asumiendo que guardaste el halo en ui/components

class ZenFocusApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- CONFIGURACIÓN VENTANA ---
        self.title("ZenFocus - Ultimate Productivity")
        self.geometry("500x750")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1) # El panel de sonido se expande

        # --- MOTORES LÓGICOS ---
        self.rpg_engine = GamificationEngine() # Tu cerebro RPG
        pygame.mixer.init() # Motor de Audio
        
        # Variables de Estado
        self.modo = "pomodoro" 
        self.tiempo_total = 25 * 60
        self.tiempo_actual = self.tiempo_total
        self.corriendo = False
        self.timer_id = None
        self.sonidos_cargados = {}

        # --- INTERFAZ DE USUARIO (UI) ---
        self.crear_header_rpg()  # Barra de nivel superior
        self.crear_area_timer()  # El Halo y el reloj
        self.crear_mixer()       # Panel de sonidos

    def crear_header_rpg(self):
        """Barra superior con Nivel y XP"""
        self.frame_rpg = ctk.CTkFrame(self, height=60, fg_color="transparent")
        self.frame_rpg.grid(row=0, column=0, sticky="ew", padx=20, pady=(10, 0))
        
        # Etiqueta de Nivel
        lvl = self.rpg_engine.profile["level"]
        self.lbl_nivel = ctk.CTkLabel(self.frame_rpg, text=f"NIVEL {lvl}", font=("Arial", 12, "bold"), text_color="#1f6aa5")
        self.lbl_nivel.pack(anchor="w")

        # Barra de XP
        self.xp_bar = ctk.CTkProgressBar(self.frame_rpg, height=10, progress_color="#1f6aa5")
        self.xp_bar.set(self.rpg_engine.get_progress_percent())
        self.xp_bar.pack(fill="x", pady=5)
        
        self.lbl_xp_detalles = ctk.CTkLabel(self.frame_rpg, text="0 / 100 XP", font=("Arial", 10), text_color="gray")
        self.lbl_xp_detalles.pack(anchor="e")
        self.actualizar_ui_rpg() # Cargar datos iniciales

    def crear_area_timer(self):
        """Zona central con el Halo y controles"""
        self.frame_timer = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_timer.grid(row=1, column=0, pady=20)

        # 1. Selector de Modo
        self.seg_modo = ctk.CTkSegmentedButton(self.frame_timer, values=["Pomodoro", "Flowtime"], command=self.cambiar_modo)
        self.seg_modo.set("Pomodoro")
        self.seg_modo.pack(pady=10)

        # 2. El Halo que Respira (Contenedor visual)
        # Importante: width/height define el tamaño del canvas
        self.halo = BreathingHalo(self.frame_timer, width=260, height=260, bg_color="#242424") 
        self.halo.pack(pady=10)

        # 3. El Texto del Tiempo (Superpuesto en el Halo)
        self.lbl_tiempo = ctk.CTkLabel(self.frame_timer, text="25:00", font=("Roboto", 50, "bold"))
        # Usamos place relativo al frame_timer, calculando el centro manual o ajustando con place sobre el halo
        self.lbl_tiempo.place(in_=self.halo, relx=0.5, rely=0.5, anchor="center")

        # 4. Botón Principal
        self.btn_accion = ctk.CTkButton(self.frame_timer, text="INICIAR ENFOQUE", width=200, height=40, command=self.toggle_timer, font=("Arial", 14, "bold"))
        self.btn_accion.pack(pady=20)
        
        # 5. Sugerencia (Para Flowtime)
        self.lbl_sugerencia = ctk.CTkLabel(self.frame_timer, text="", text_color="gray")
        self.lbl_sugerencia.pack()

    def crear_mixer(self):
        """Panel inferior scrolleable para sonidos"""
        self.frame_mixer = ctk.CTkScrollableFrame(self, label_text="Ambiente Sonoro")
        self.frame_mixer.grid(row=2, column=0, sticky="nsew", padx=20, pady=20)
        
        # Lista de sonidos (Asegúrate de tener estos archivos en assets/sounds o la app no sonará)
        sonidos = ["Lluvia", "Fuego", "Cafe", "Viento"]
        
        for i, sonido in enumerate(sonidos):
            lbl = ctk.CTkLabel(self.frame_mixer, text=sonido, width=80, anchor="w")
            lbl.grid(row=i, column=0, padx=10, pady=10)
            
            slider = ctk.CTkSlider(self.frame_mixer, from_=0, to=1, command=lambda val, s=sonido: self.ajustar_volumen(s, val))
            slider.set(0)
            slider.grid(row=i, column=1, padx=10, sticky="ew")
            
            # Cargar sonido dummy si no existe el archivo (para que no crashee)
            try:
                path = f"assets/sounds/{sonido.lower()}.mp3"
                if os.path.exists(path):
                    sound_obj = pygame.mixer.Sound(path)
                    sound_obj.play(loops=-1)
                    sound_obj.set_volume(0)
                    self.sonidos_cargados[sonido] = sound_obj
                else:
                    print(f"Advertencia: No se encontró {path}")
            except Exception as e:
                print(f"Error cargando audio: {e}")

    # --- LÓGICA ---

    def ajustar_volumen(self, nombre, valor):
        if nombre in self.sonidos_cargados:
            self.sonidos_cargados[nombre].set_volume(valor)

    def cambiar_modo(self, nuevo_modo):
        self.modo = nuevo_modo.lower()
        self.detener_timer()
        
        if self.modo == "pomodoro":
            self.tiempo_actual = 25 * 60
            self.lbl_tiempo.configure(text="25:00")
            self.lbl_sugerencia.configure(text="")
        else: # Flowtime
            self.tiempo_actual = 0
            self.lbl_tiempo.configure(text="00:00")
            self.lbl_sugerencia.configure(text="Descanso sugerido: 0 min")

    def toggle_timer(self):
        if self.corriendo:
            self.detener_timer()
        else:
            self.iniciar_timer()

    def iniciar_timer(self):
        self.corriendo = True
        self.btn_accion.configure(text="PAUSAR", fg_color="#D32F2F", hover_color="#B71C1C")
        self.actualizar_reloj()

    def detener_timer(self):
        self.corriendo = False
        self.btn_accion.configure(text="REANUDAR", fg_color="#1f6aa5", hover_color="#144870")
        if self.timer_id:
            self.after_cancel(self.timer_id)

    def actualizar_reloj(self):
        if not self.corriendo: return

        if self.modo == "pomodoro":
            if self.tiempo_actual > 0:
                self.tiempo_actual -= 1
                mins, segs = divmod(self.tiempo_actual, 60)
                self.lbl_tiempo.configure(text=f"{mins:02}:{segs:02}")
            else:
                self.finalizar_sesion(25) # Pomodoro completado
                return
        
        elif self.modo == "flowtime":
            self.tiempo_actual += 1
            mins, segs = divmod(self.tiempo_actual, 60)
            self.lbl_tiempo.configure(text=f"{mins:02}:{segs:02}")
            # Lógica de sugerencia de descanso
            descanso = 5
            if mins > 25: descanso = 8
            if mins > 50: descanso = 15
            self.lbl_sugerencia.configure(text=f"Descanso sugerido: {descanso} min")

        self.timer_id = self.after(1000, self.actualizar_reloj)

    def finalizar_sesion(self, minutos):
        self.detener_timer()
        self.btn_accion.configure(text="INICIAR ENFOQUE", fg_color="#1f6aa5")
        
        # --- INTEGRACIÓN RPG ---
        # Calculamos XP y mostramos resultado
        resultado = self.rpg_engine.add_session_xp(minutos)
        self.actualizar_ui_rpg()
        
        mensaje = f"¡Sesión terminada! +{resultado['xp_gained']} XP"
        if resultado['leveled_up']:
            mensaje += f"\n¡SUBISTE A NIVEL {resultado['new_level']}!"
            # Aquí podrías lanzar un popup festivo
        
        self.lbl_sugerencia.configure(text=mensaje, text_color="#1f6aa5")
        
        # Reiniciar Pomodoro
        if self.modo == "pomodoro":
            self.tiempo_actual = 25 * 60
            self.lbl_tiempo.configure(text="25:00")

    def actualizar_ui_rpg(self):
        p = self.rpg_engine.profile
        xp_needed = self.rpg_engine.calculate_xp_needed()
        self.lbl_nivel.configure(text=f"NIVEL {p['level']}")
        self.xp_bar.set(self.rpg_engine.get_progress_percent())
        self.lbl_xp_detalles.configure(text=f"{p['current_xp']} / {xp_needed} XP")