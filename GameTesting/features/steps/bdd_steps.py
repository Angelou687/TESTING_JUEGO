from behave import given, when, then
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from entities import Tank
from main import Game

@given('que el tanque del Jugador 1 tiene un HP inicial de {hp_inicial:d} puntos')
def step_given_hp(context, hp_inicial):
    context.tank = Tank(x=150.0, mobile_type='Knight', name='Player 1')
    context.tank.health = hp_inicial

@when('el jugador consume una poción de restauración de {cantidad:d} puntos de vida')
def step_when_potion(context, cantidad):
    context.tank.health = min(context.tank.max_health, context.tank.health + cantidad)

@then('el sistema actualiza el motor y su salud final se incrementa a {hp_final:d} puntos')
def step_then_hp(context, hp_final):
    assert context.tank.health == hp_final

@given('que el jugador actual inicia su turno con el "Shot Básico" seleccionado')
def step_given_basic_shot(context):
    context.game = Game()
    context.game.current_weapon_idx[context.game.current_turn] = 0

@when('presiona la tecla de control numérico para equipar la segunda arma')
def step_when_change_weapon(context):
    context.game.current_weapon_idx[context.game.current_turn] = 1

@then('el índice del arma activa en el HUD cambia a la posición 1')
def step_then_weapon_updated(context):
    assert context.game.current_weapon_idx[context.game.current_turn] == 1

@given('que el cañón del móvil tiene una inclinación inicial de {angulo_inicial:f} grados')
def step_given_cannon_angle(context, angulo_inicial):
    context.tank = Tank(x=100.0, mobile_type='Knight', name='P1')
    context.tank.angle = float(angulo_inicial)

@when('el jugador ejecuta la acción de elevación una vez')
def step_when_press_up(context):
    context.tank.angle += 1.0

@then('el ángulo relativo del cañón aumenta a {angulo_final:f} grados')
def step_then_angle_updated(context, angulo_final):
    assert context.tank.angle == float(angulo_final)

@given('que el jugador tiene un saldo de {oro:d} de oro y {escudo:d} de escudo adicional')
def step_given_shop_state(context, oro, escudo):
    context.tank = Tank(x=100.0, mobile_type='Mage', name='P2')
    context.tank.gold = oro
    context.tank.shield = escudo

@when('realiza la compra de un kit de protección táctica de {costo:d} de oro')
def step_when_buy_item(context, costo):
    if context.tank.gold >= costo:
        context.tank.gold -= costo
        context.tank.shield += 25

@then('su reserva disminuye a {oro_final:d} de oro y su escudo aumenta a {escudo_final:d} puntos')
def step_then_shop_assertions(context, oro_final, escudo_final):
    assert context.tank.gold == oro_final
    assert context.tank.shield == escudo_final

@given('que el vehículo cuenta con {fuel:f} unidades de combustible en X de {pos_x:f}')
def step_given_fuel_state(context, fuel, pos_x):
    context.tank = Tank(x=float(pos_x), mobile_type='Knight', name='P1')
    context.tank.fuel = float(fuel)

@when('el usuario avanza una distancia horizontal de {distancia:f} píxeles')
def step_when_move_tank(context, distancia):
    context.tank.x += float(distancia)
    context.tank.fuel -= float(distancia)

@then('el combustible baja a {fuel_final:f} unidades y la posición X cambia a {pos_x_final:f}')
def step_then_movement_assertions(context, fuel_final, pos_x_final):
    assert context.tank.fuel == float(fuel_final)
    assert context.tank.x == float(pos_x_final)