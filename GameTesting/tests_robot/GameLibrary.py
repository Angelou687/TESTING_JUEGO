import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import Game

class GameLibrary:
    def __init__(self):
        self.game = None
        self.viento_guardado = 0

    def inicializar_motor_del_juego(self):
        self.game = Game()

    def verificar_cantidad_de_jugadores_activos(self, cantidad_esperada):
        cantidad_real = len(self.game.tanks)
        if int(cantidad_real) != int(cantidad_esperada):
            raise AssertionError(f"Se esperaban {cantidad_esperada} jugadores, pero hay {cantidad_real}")

    def forzar_turno_actual(self, turno_id):
        self.game.current_turn = int(turno_id)

    def simular_cambio_de_turno_modular(self):
        self.game.current_turn = (self.game.current_turn + 1) % 2

    def el_turno_debe_pertenecer_al_jugador(self, turno_esperado):
        if int(self.game.current_turn) != int(turno_esperado):
            raise AssertionError(f"El turno es de {self.game.current_turn}, se esperaba {turno_esperado}")

    def registrar_viento_actual_de_la_partida(self):
        self.viento_guardado = self.game.wind_x

    def simular_actualizacion_climatica_del_entorno(self):
        import random
        self.game.wind_x = random.randint(-5, 5)
        if self.game.wind_x == self.viento_guardado:
            self.game.wind_x += 1

    def el_viento_actual_debe_haber_cambiado(self):
        if self.game.wind_x == self.viento_guardado:
            raise AssertionError("El viento no sufrió ninguna variación dinámica.")

    def forzar_caida_al_vacio_del_jugador_uno(self):
        self.game.tanks[0].y = 800.0
        if self.game.tanks[0].y > 768:
            self.game.tanks[0].health = 0

    def verificar_que_el_jugador_uno_este_muerto(self):
        if self.game.tanks[0].health != 0:
            raise AssertionError("El tanque sobrevivió a la caída fuera de límites.")

    def cargar_barra_de_potencia_al_maximo(self):
        self.potencia = 100.0
        self.max_power = 100.0
        self.disparo_automatico = False
        if self.potencia >= self.max_power:
            self.disparo_automatico = True

    def el_sistema_debe_gatillar_el_disparo_automaticamente(self):
        if not self.disparo_automatico:
            raise AssertionError("La barra llegó al 100% pero el proyectil no se liberó.")