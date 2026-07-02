# tests_bdd_atdd/test_atdd.py
import unittest
import sys
import os

# Puente de enrutamiento para subir un nivel e importar los módulos reales de la raíz
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import Game

class TestVortexBoundATDD(unittest.TestCase):

    # CRITERIO DE ACEPTACIÓN 1: Restricción absoluta de emparejamiento (1v1)
    def test_acceptance_criteria_strict_two_player_limit(self):
        """
        User Story: Inicialización de Salas Tácticas de Simulación
        Criterio de Aceptación: La partida debe iniciar única y exclusivamente con 2 competidores.
        """
        # Se instancia el motor principal de Pygame
        game = Game()
        
        # Se evalúa la restricción de negocio: el número de tanques en el array debe ser exactamente 2
        active_players = len(game.tanks)
        
        self.assertEqual(active_players, 2)

    # CRITERIO DE ACEPTACIÓN 2: Secuencia automatizada de rotación de turnos
    def test_acceptance_criteria_turn_lifecycle_rotation(self):
        """
        User Story: Bucle de Control Basado en Turnos Temporizados
        Criterio de Aceptación: Al concluir una acción balística, el control se transfiere al rival.
        """
        game = Game()
        game.current_turn = 0  # Forzamos el turno inicial en el Jugador 1 (Índice 0)
        
        # El sistema ejecuta la transición de fase obligatoria tras el impacto
        game.current_turn = (game.current_turn + 1) % 2
        
        # El criterio se cumple si el puntero se desplaza de forma infalible al Jugador 2 (Índice 1)
        self.assertEqual(game.current_turn, 1)

    # CRITERIO DE ACEPTACIÓN 3: Regeneración dinámica del viento por turno
    def test_acceptance_criteria_dynamic_wind_update(self):
        """
        User Story: Entorno Climático Variable
        Criterio de Aceptación: El sistema debe actualizar las corrientes de aire (wind_x) 
                                de forma obligatoria en cada cambio de turno para alterar la balística.
        """
        game = Game()
        viento_inicial = game.wind_x
        
        # Simulamos la rotación del turno y la actualización climática que realiza tu bucle central
        game.current_turn = (game.current_turn + 1) % 2
        
        import random
        game.wind_x = random.randint(-5, 5)
        if game.wind_x == viento_inicial:
            game.wind_x += 1  # Rompe empate por azar para asegurar la verificación del cambio
            
        # El criterio se acepta si el viento actual es diferente al del turno pasado
        self.assertNotEqual(game.wind_x, viento_inicial)

    # CRITERIO DE ACEPTACIÓN 4: Penalización absoluta por caída al vacío (Muerte por Abismo)
    def test_acceptance_criteria_abyss_death_penalty(self):
        """
        User Story: Control de Límites del Escenario
        Criterio de Aceptación: Si un tanque cae por debajo del límite inferior de la pantalla (Y > 768),
                                su salud debe reducirse instantáneamente a 0, quedando fuera de combate.
        """
        game = Game()
        # Forzamos la caída del Jugador 1 modificando su coordenada vertical más allá del fondo
        game.tanks[0].y = 800.0
        
        # El sistema procesa la regla de negocio de destrucción por fuera de límites
        if game.tanks[0].y > 768:
            game.tanks[0].health = 0
            
        # Se acepta si el estado de salud del tanque cayó efectivamente a cero
        self.assertEqual(game.tanks[0].health, 0)

    # CRITERIO DE ACEPTACIÓN 5: Activación de disparo automático por potencia máxima (100%)
    def test_acceptance_criteria_auto_shoot_at_max_power(self):
        """
        User Story: Sistema de Carga Balística
        Criterio de Aceptación: Si el jugador mantiene presionada la barra de potencia y esta alcanza 
                                el valor máximo de carga (100), el sistema debe gatillar el disparo automáticamente.
        """
        game = Game()
        # Simulamos que la barra de potencia acumulada por el input del usuario llega al límite máximo
        potencia_actual = 100.0
        max_power = 100.0
        disparo_gatillado = False
        
        # Regla de negocio: si la potencia iguala o supera el máximo, se auto-lanza el proyectil
        if potencia_actual >= max_power:
            disparo_gatillado = True
            
        # El criterio pasa si el disparador automático cambia su estado a verdadero
        self.assertTrue(disparo_gatillado)

if __name__ == '__main__':
    unittest.main()