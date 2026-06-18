import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.entities import Tank

class TestTankCore(unittest.TestCase):
    
    def test_tank_initial_health_by_type(self):
        """TDD: Validar la correcta asignación de HP inicial según el perfil."""
        tank_heavy = Tank(200, 'Heavy', "Player Test")
        tank_normal = Tank(200, 'Knight', "Player Test")
        
        self.assertEqual(tank_heavy.max_health, 135)
        self.assertEqual(tank_normal.max_health, 100)

    def test_tank_health_cannot_be_negative(self):
        """TDD: Mitigación perimetral contra valores de salud negativos."""
        tank = Tank(100, 'Knight', "Player Test")
        tank.health = 20
        
        tank.take_damage(150)
        
        self.assertEqual(tank.health, 0)
        
    def test_tank_shield_absorbs_damage_completely(self):
        """TDD: Validar que el escudo absorba el impacto antes que la salud estructural."""
        tank = Tank(100, 'Knight', "Player Test")
        tank.health = 100
        tank.shield = 25
        
        tank.take_damage(20)
        
        self.assertEqual(tank.shield, 5)
        self.assertEqual(tank.health, 100)