# language: es
Característica: Simulación del Sistema de Combate y Comportamiento Táctico

  Escenario: El personaje usa una poción y restablece salud de forma controlada
    Dado que el tanque del Jugador 1 tiene un HP inicial de 40 puntos
    Cuando el jugador consume una poción de restauración de 50 puntos de vida
    Entonces el sistema actualiza el motor y su salud final se incrementa a 90 puntos

  Escenario: El jugador cambia de munición táctica en su turno
    Dado que el jugador actual inicia su turno con el "Shot Básico" seleccionado
    Cuando presiona la tecla de control numérico para equipar la segunda arma
    Entonces el índice del arma activa en el HUD cambia a la posición 1

  Escenario: El jugador incrementa la inclinación de disparo
    Dado que el cañón del móvil tiene una inclinación inicial de 45.0 grados
    Cuando el jugador ejecuta la acción de elevación una vez
    Entonces el ángulo relativo del cañón aumenta a 46.0 grados

  Escenario: Adquisición de items en la tienda de suministros
    Dado que el jugador tiene un saldo de 300 de oro y 0 de escudo adicional
    Cuando realiza la compra de un kit de protección táctica de 75 de oro
    Entonces su reserva disminuye a 225 de oro y su escudo aumenta a 25 puntos

  Escenario: El tanque consume energía al moverse por el mapa
    Dado que el vehículo cuenta con 100.0 unidades de combustible en X de 100.0
    Cuando el usuario avanza una distancia horizontal de 10.0 píxeles
    Entonces el combustible baja a 90.0 unidades y la posición X cambia a 110.0