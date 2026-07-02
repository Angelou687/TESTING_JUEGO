# tests/test_fase_green.py
import unittest
import math

# --- IMPLEMENTACIÓN MÍNIMA REQUERIDA (GREEN) ---
class GreenTank:
    def __init__(self, initial_x, fuel, initial_y=450.0):
        self.x = float(initial_x)
        self.y = float(initial_y)
        self.fuel = float(fuel)

    def move_tank(self, direction, distance):
        # Código mínimo paso a paso para quemar el combustible justo
        for _ in range(int(distance)):
            if self.fuel <= 0: break
            self.x += direction * 1.0
            self.fuel -= 1.0

    def update_ground_alignment(self, heights_list):
        idx = int(self.x)
        self.y = float(heights_list[idx])

class GreenProjectile:
    def __init__(self):
        self.vy = 0.0
        self.gravity = 0.22

    def apply_physics(self):
        self.vy += self.gravity

class GreenGameManager:
    def __init__(self):
        self.match_state = "PLAYING"

    def check_match_status(self, p1_hp, p2_hp):
        if p1_hp <= 0 and p2_hp <= 0:
            self.match_state = "EMPATE"

# --- BATERÍA DE PRUEBAS EN VERDE ---
class TestVortexBoundGreen(unittest.TestCase):

    # 1. PRUEBA COMBUSTIBLE (GREEN)
    def test_movement_consumes_fuel_and_stops_when_empty(self):
        tank = GreenTank(initial_x=100.0, fuel=10.0)
        tank.move_tank(direction=1, distance=15.0)
        self.assertEqual(tank.fuel, 0.0)
        self.assertEqual(tank.x, 110.0)

    # 2. PRUEBA GRAVEDAD (GREEN)
    def test_projectile_velocity_vector_applies_exact_gravity(self):
        proj = GreenProjectile()
        proj.apply_physics()
        self.assertEqual(proj.vy, 0.22)

    # 3. PRUEBA DESTRUCCIÓN TERRENO (GREEN)
    def test_projectile_impact_deforms_terrain_height_map(self):
        heights = [500] * 100
        impact_x, impact_y, radius = 50, 500, 10
        
        # Algoritmo mínimo de excavación circular pura por cuerdas
        start_x = max(0, impact_x - radius)
        end_x = min(100, impact_x + radius + 1)
        for x in range(start_x, end_x):
            chord = math.sqrt(radius**2 - (x - impact_x)**2)
            crater_floor = impact_y + chord
            if heights[x] < crater_floor:
                heights[x] = int(crater_floor)

        self.assertEqual(heights[50], 510)

    # 4. PRUEBA ALINEACIÓN AL SUELO (GREEN)
    def test_tank_snaps_to_height_map_coordinate_on_update(self):
        heights_mock = [450] * 100
        heights_mock[20] = 400
        tank = GreenTank(initial_x=20, fuel=100, initial_y=450)
        tank.update_ground_alignment(heights_mock)
        self.assertEqual(tank.y, 400.0)

    # 5. PRUEBA CONDICIÓN DE EMPATE (GREEN)
    def test_game_status_is_draw_when_both_players_die(self):
        manager = GreenGameManager()
        manager.check_match_status(p1_hp=0, p2_hp=0)
        self.assertEqual(manager.match_state, "EMPATE")

if __name__ == '__main__':
    unittest.main()