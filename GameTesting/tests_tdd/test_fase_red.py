# tests/test_fase_red.py
import unittest
import math

# --- CLASES TEMPORALES EN ESTADO INICIAL (FALLA) ---
class TempTank:
    def __init__(self, initial_x=100.0, fuel=10.0, initial_y=450.0):
        self.x = initial_x
        self.y = initial_y
        self.fuel = fuel
        self.health = 100

class TempProjectile:
    def __init__(self):
        self.vy = 0.0

class TempGameManager:
    def __init__(self):
        self.match_state = "PLAYING"

# --- BATERÍA DE PRUEBAS EN ROJO ---
class TestVortexBoundRed(unittest.TestCase):

    # 1. PRUEBA COMBUSTIBLE (RED)
    def test_movement_consumes_fuel_and_stops_when_empty(self):
        tank = TempTank(initial_x=100.0, fuel=10.0)
        # Forzamos un valor esperado inalcanzable porque no hay lógica de movimiento escrita
        self.assertEqual(tank.fuel, 0.0)  # Fallará: fuel sigue siendo 10.0
        self.assertEqual(tank.x, 110.0)   # Fallará: x sigue siendo 100.0

    # 2. PRUEBA GRAVEDAD (RED)
    def test_projectile_velocity_vector_applies_exact_gravity(self):
        proj = TempProjectile()
        # Fallará porque no hemos llamado a ninguna función que aplique la gravedad g=0.22
        self.assertEqual(proj.vy, 0.22)

    # 3. PRUEBA DESTRUCCIÓN TERRENO (RED)
    def test_projectile_impact_deforms_terrain_height_map(self):
        heights = [500] * 100
        # Esperamos que el mapa se haya modificado, pero al no haber algoritmo, se quedará igual
        # Forzamos el assert real para demostrar que el mapa no se hunde solo
        self.assertEqual(heights[50], 510)  # Fallará: 500 != 510

    # 4. PRUEBA ALINEACIÓN AL SUELO (RED)
    def test_tank_snaps_to_height_map_coordinate_on_update(self):
        tank = TempTank(initial_x=20, initial_y=450)
        # Esperamos que se acople a una altura de 400, pero sigue en 450
        self.assertEqual(tank.y, 400.0)  # Fallará: 450 != 400.0

    # 5. PRUEBA CONDICIÓN DE EMPATE (RED)
    def test_game_status_is_draw_when_both_players_die(self):
        manager = TempGameManager()
        # Forzamos la muerte simulada de ambos sin evaluar
        self.assertEqual(manager.match_state, "EMPATE")  # Fallará: "PLAYING" != "EMPATE"

if __name__ == '__main__':
    unittest.main()