*** Settings ***
Library    GameLibrary.py

*** Test Cases ***
Criterio Aceptacion 1: Restriccion Estricta Modalidad 1v1
    [Documentation]    Valida que la partida inicialice estrictamente con 2 competidores operacionales.
    Inicializar Motor Del Juego
    Verificar Cantidad De Jugadores Activos    2

Criterio Aceptacion 2: Rotacion Ciclica Obligatoria de Turnos
    [Documentation]    Verifica que al concluir un evento, el control se transfiera de forma infalible al rival.
    Inicializar Motor Del Juego
    Forzar Turno Actual    0
    Simular Cambio De Turno Modular
    El Turno Debe Pertenecer Al Jugador    1

Criterio Aceptacion 3: Regeneracion Dinamica del Viento por Turno
    [Documentation]    Valida la regla de negocio de que el viento cambie de intensidad al rotar el control.
    Inicializar Motor Del Juego
    Registrar Viento Actual De La Partida
    Simular Actualizacion Climatica Del Entorno
    El Viento Actual Debe Haber Cambiado

Criterio Aceptacion 4: Penalizacion Absoluta por Caida al Vacio
    [Documentation]    Verifica el criterio de aceptación de muerte instantánea al salir de los límites inferiores.
    Inicializar Motor Del Juego
    Forzar Caida Al Vacio Del Jugador Uno
    Verificar Que El Jugador Uno Este Muerto

Criterio Aceptacion 5: Gatillado Automatico por Potencia Maxima
    [Documentation]    Asegura que el juego dispare inmediatamente al alcanzar el 100% de fuerza.
    Inicializar Motor Del Juego
    Cargar Barra De Potencia Al Maximo
    El Sistema Debe Gatillar El Disparo Automaticamente