import sys
import os
import customtkinter as ctk

# --- CONFIGURACIÓN DE RUTAS ---
# Esto permite importar módulos desde la carpeta 'src' sin errores
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.append(src_dir)

# Importar la ventana principal desde nuestra estructura modular
from ui.main_window import ZenFocusApp

if __name__ == "__main__":
    # Configuración global de estilo
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")
    
    # Iniciar la aplicación
    app = ZenFocusApp()
    app.mainloop()