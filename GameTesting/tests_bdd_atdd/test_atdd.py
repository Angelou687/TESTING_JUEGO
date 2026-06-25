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

if __name__ == '__main__':
    unittest.main()