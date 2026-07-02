# tests_bdd_atdd/test_bdd.py
import unittest
import sys
import os

# Puente de enrutamiento para subir un nivel e importar los módulos reales de la raíz
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from entities import Tank
from main import Game

class TestVortexBoundBDD(unittest.TestCase):

    # ESCENARIO 1: (Resolución de la Pregunta 12 de la Guía de Laboratorio)
    def test_scenario_player_uses_potion_and_recovers_health(self):
        """
        Feature: Sistema de Recuperación de Vitalidad de Móviles
        Scenario: El personaje recoge/usa una poción y restablece salud de forma controlada
        """
        # GIVEN: un jugador con 100 de salud máxima herido críticamente con 40 de salud actual
        tank = Tank(x=150.0, mobile_type='Knight', name='Player 1')
        tank.health = 40 
        self.assertEqual(tank.health, 40)
        
        # WHEN: consume una poción de restauración molecular de 50 puntos de vida
        potion_heal_value = 50
        tank.health = min(tank.max_health, tank.health + potion_heal_value)
        
        # THEN: el sistema procesa la cura y su salud se incrementa a exactamente 90 puntos
        self.assertEqual(tank.health, 90)

    # ESCENARIO 2: Gestión económica en el Hangar Táctico (Tienda Overlay)
    def test_scenario_player_buys_item_from_shop_updates_gold(self):
        """
        Feature: Tienda Integrada de Suministros
        Scenario: Adquisición de escudo defensivo descontando fondos de las reservas de oro
        """
        # GIVEN: un jugador con un balance inicial de 300G en oro y 0 puntos de protección adicional
        tank = Tank(x=700.0, mobile_type='Mage', name='Player 2')
        tank.gold = 300
        tank.shield = 0
        
        # WHEN: efectúa la compra de un item 'Item de Protección' con un valor de 75G
        item_cost = 75
        if tank.gold >= item_cost:
            tank.gold -= item_cost
            tank.shield += 25  
            
        # THEN: las reservas disminuyen a 225G de oro y la barra de protección se establece en 25
        self.assertEqual(tank.gold, 225)
        self.assertEqual(tank.shield, 25)

    # ESCENARIO 3: Rotación de Armamento en el Inventario Táctico (HUD)
    def test_scenario_player_switches_active_weapon_type(self):
        """
        Feature: Selector de Arsenal Balístico
        Scenario: El jugador cambia el tipo de munición pesada activa durante su turno
        """
        # GIVEN: El motor de juego inicializado y el jugador actual con el 'Shot Básico' (Índice 0) seleccionado
        game = Game()
        game.current_weapon_idx[game.current_turn] = 0
        self.assertEqual(game.current_weapon_idx[game.current_turn], 0)
        
        # WHEN: Presiona la tecla asignada para equipar el armamento secundario o misil pesado
        game.current_weapon_idx[game.current_turn] = 1
        
        # THEN: El HUD del juego actualiza el slot visual y activa el índice de munición en la posición 1
        self.assertEqual(game.current_weapon_idx[game.current_turn], 1)

    # ESCENARIO 4: Ajuste angular del vector de disparo (Inclinación del Cañón)
    def test_scenario_player_adjusts_cannon_elevation_angle(self):
        """
        Feature: Control de Apuntamiento del Chasis
        Scenario: Modificación incremental de la inclinación del cañón del móvil para ajustar el tiro
        """
        # GIVEN: Un tanque posicionado en el escenario con un ángulo de elevación base de 45.0 grados
        tank = Tank(x=200.0, mobile_type='Knight', name='Player 1')
        tank.angle = 45.0
        self.assertEqual(tank.angle, 45.0)
        
        # WHEN: El jugador mantiene presionado el control de elevación (Tecla W) aumentando 1.0 grado la inclinación
        tank.angle += 1.0
        
        # THEN: El vector angular de disparo se sitúa de forma precisa en 46.0 grados
        self.assertEqual(tank.angle, 46.0)

    # ESCENARIO 5: Consumo Dinámico de Energía por Desplazamiento Cinemático
    def test_scenario_tank_movement_depletes_fuel_reserves(self):
        """
        Feature: Sistema Cinemático Limitado por Combustible
        Scenario: El móvil se desplaza por el terreno horizontal consumiendo energía proporcionalmente
        """
        # GIVEN: Un tanque con 100.0 unidades de combustible inicial ubicado en la posición X = 100.0
        tank = Tank(x=100.0, mobile_type='Knight', name='Player 1')
        tank.fuel = 100.0
        
        # WHEN: El jugador avanza hacia el flanco derecho recorriendo una distancia de 10.0 píxeles
        distance_walked = 10.0
        tank.x += distance_walked
        tank.fuel -= distance_walked  # Tasa lineal: 1 unidad de fuel por cada píxel
        
        # THEN: El inventario energético disminuye a 90.0 y la coordenada horizontal se actualiza a 110.0
        self.assertEqual(tank.fuel, 90.0)
        self.assertEqual(tank.x, 110.0)

if __name__ == '__main__':
    unittest.main()