# tests_bdd_atdd/test_bdd.py
import unittest
import sys
import os

# Puente de enrutamiento para subir un nivel e importar los módulos reales de la raíz
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from entities import Tank

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

if __name__ == '__main__':
    unittest.main()