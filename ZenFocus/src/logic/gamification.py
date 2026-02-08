import json
import os
import math

class GamificationEngine:
    def __init__(self, data_file="data/user_profile.json"):
        self.data_file = data_file
        
        # Estructura de datos por defecto (si es un usuario nuevo)
        self.profile = {
            "level": 1,
            "current_xp": 0,
            "total_xp_earned": 0,
            "total_minutes_focused": 0,
            "streak_days": 0,
            "unlocked_titles": ["Novato Distraído"]
        }
        
        # Intentar cargar datos existentes
        self.load_data()

    def calculate_xp_needed(self):
        """
        Fórmula de Curva de Dificultad RPG:
        Nivel 1 -> 100 XP
        Nivel 2 -> 200 XP
        Nivel 3 -> 300 XP
        ...
        Es una progresión lineal suave para no frustrar al usuario.
        """
        return self.profile["level"] * 100

    def add_session_xp(self, minutes_focused):
        """
        Procesa una sesión finalizada y devuelve un reporte.
        Regla: 1 minuto = 10 XP
        """
        xp_gained = int(minutes_focused * 10)
        
        # Actualizar estadísticas brutas
        self.profile["total_minutes_focused"] += minutes_focused
        self.profile["total_xp_earned"] += xp_gained
        self.profile["current_xp"] += xp_gained
        
        # Verificar Subida de Nivel
        leveled_up = False
        xp_needed = self.calculate_xp_needed()
        
        while self.profile["current_xp"] >= xp_needed:
            self.profile["current_xp"] -= xp_needed
            self.profile["level"] += 1
            leveled_up = True
            # Recalcular para el siguiente nivel (en caso de subir 2 niveles de golpe)
            xp_needed = self.calculate_xp_needed()
            
        # Guardar automáticamente
        self.save_data()
        
        return {
            "xp_gained": xp_gained,
            "leveled_up": leveled_up,
            "new_level": self.profile["level"],
            "current_xp": self.profile["current_xp"],
            "xp_needed": xp_needed
        }

    def get_progress_percent(self):
        """Para la barra de progreso de XP en la UI (0.0 a 1.0)"""
        xp_needed = self.calculate_xp_needed()
        if xp_needed == 0: return 0
        return self.profile["current_xp"] / xp_needed

    def save_data(self):
        # Asegurarse de que la carpeta 'data' exista
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.profile, f, indent=4)
        except Exception as e:
            print(f"Error guardando progreso: {e}")

    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    # Actualizamos el perfil con los datos cargados
                    # (usamos .update para mantener claves nuevas si actualizas la app)
                    self.profile.update(data)
            except Exception as e:
                print(f"Error cargando archivo, iniciando perfil nuevo: {e}")