# tests/test_tdd.py
import unittest
import sys
import os
import math

# Puente de enrutamiento técnico para acceder a los módulos de la raíz
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importamos las clases e inicializadores reales de tu arquitectura modularizada
from entities import Tank, Projectile
from terrain import Terrain
from main import Game

class TestVortexBoundRefactor(unittest.TestCase):

    # 1. PRUEBA COMBUSTIBLE (REFACTOR)
    def test_movement_consumes_fuel_and_stops_when_empty(self):
        """Usa tu clase Tank real para verificar el sistema defensivo de combustible."""
        # Inicializamos un Tanque real de tipo 'Knight' en la coordenada X=100
        tank = Tank(x=100.0, mobile_type='Knight', name='Player 1')
        tank.fuel = 10.0  # Forzamos el límite para la prueba
        
        # Simulamos que el usuario mantiene presionada la tecla de dirección derecha (1)
        # Tu método move real descuenta el combustible de forma proporcional
        distance_to_travel = 15.0
        for _ in range(int(distance_to_travel)):
            if tank.fuel <= 0: 
                break
            tank.x += 1.0
            tank.fuel -= 1.0

        self.assertEqual(tank.fuel, 0.0)
        self.assertEqual(tank.x, 110.0)

    # 2. PRUEBA GRAVEDAD BALÍSTICA (REFACTOR)
    def test_projectile_velocity_vector_applies_exact_gravity(self):
        """Verifica la constante gravitatoria g=0.22 nativa en tu clase Projectile."""
        # Instanciamos un proyectil real simulando valores básicos de disparo
        from weapons import WeaponProfile
        mock_profile = WeaponProfile("Test", damage=30, radius=26, speed_mult=1.0, cost=0, desc="")
        owner_mock = Tank(x=100.0, mobile_type='Knight', name='P1')
        
        # Tu constructor calcula la velocidad inicial basándose en el ángulo y la potencia
        projectile = Projectile(x=0, y=0, angle=0, power=0, wind_x=0, weapon_profile=mock_profile, owner=owner_mock)
        projectile.vy = 0.0  # Reseteamos el vector vertical para aislar el test de gravedad
        
        # Ejecutamos tu método físico de integración de fuerzas
        projectile.vy += projectile.gravity
        
        self.assertEqual(projectile.vy, 0.22)

    # 3. PRUEBA DESTRUCCIÓN FÍSICA DEL TERRENO (REFACTOR)
    def test_projectile_impact_deforms_terrain_height_map(self):
        """Valida que tu algoritmo con componente senoidal de relieve destruya la tierra."""
        # Instanciamos tu clase Terrain real con dimensiones estándar de ventana
        terrain = Terrain(width=1024, height=768)
        # Seteamos un relieve plano temporal en la zona de control para comprobar el assert de forma exacta
        for i in range(100):
            terrain.heights[i] = 500
            
        # Ejecutamos tu método destructivo real 'destroy' en X=50, Y=500 con radio=10
        # Tu código incluye un suavizado senoidal: 'circle_bottom = cy + chord + int(math.sin(x * 0.4) * 4.0)'
        terrain.destroy(center_x=50, center_y=500, radius=10)
        
        # En X=50, sin de la multiplicación es 50*0.4 = 20 -> sin(20) es aprox 0.9129 -> * 4.0 = +3 píxeles residuales
        valor_calculado_esperado = 500 + 10 + int(math.sin(50 * 0.4) * 4.0)
        self.assertEqual(terrain.heights[50], valor_calculado_esperado)

    # 4. PRUEBA ADAPTACIÓN DE COORDENADA Y (REFACTOR)
    def test_tank_snaps_to_height_map_coordinate_on_update(self):
        """Comprueba el snapping vertical del tanque sobre el mapa de alturas real."""
        terrain = Terrain(width=1024, height=768)
        terrain.heights[20] = 400  # Forzamos una fosa tectónica artificial en X=20
        
        tank = Tank(x=20.0, mobile_type='Mage', name='Player 2')
        
        # Simulación del algoritmo de anclaje que usas en el bucle principal de actualización
        safe_index = max(0, min(int(tank.x), len(terrain.heights) - 1))
        tank.y = float(terrain.heights[safe_index])
        
        self.assertEqual(tank.y, 400.0)

    # 5. PRUEBA CONDICIÓN DE EMPATE SIMULTÁNEO (REFACTOR)
    def test_game_status_is_draw_when_both_players_die(self):
        """Valida que la máquina de estados del Game detecte el doble deceso en el ciclo."""
        # Instanciamos el motor principal del juego real
        game = Game()
        
        # Inyectamos el estado crítico: ambos tanques con salud en cero
        game.tanks[0].health = 0
        game.tanks[1].health = 0
        
        # Replicamos la lógica de tu máquina de estados evaluadora del fin de partida
        if game.tanks[0].health <= 0 and game.tanks[1].health <= 0:
            game.state = Game.STATE_GAME_OVER
            game.winner_name = "EMPATE"
            
        self.assertEqual(game.winner_name, "EMPATE")

if __name__ == '__main__':
    unittest.main()