"""
TRABAJO AUTONOMO TERCER BIMESTRE - Matematica Aplicada

"Simulacion 3D y Telemetria Analitica de Renderizado y Fisica
de un Dron de Entregas mediante Calculo Diferencial e Integral"

Este script:

1. Define las funciones analiticas h(t), h'(t), h''(t), T(t) y D(t)
   obtenidas en las Fases 1, 2 y 3 del enunciado.

2. Renderiza un modelo 3D de un dron utilizando VPython.

3. El dron se mueve en el espacio tridimensional (x, y, z),
   siguiendo la funcion matematica de altitud h(t).

4. Muestra telemetria en tiempo real:
   - Tiempo
   - Altitud h(t)
   - Velocidad instantanea h'(t)
   - Datos acumulados mediante integracion numerica

5. Al finalizar los 10 segundos de simulacion, genera una ventana
   de Matplotlib con tres graficas:
   - Altitud h(t)
   - Velocidad v(t) con recta tangente
   - Transferencia de datos D(t) con el area sombreada entre t=1 y t=4

Librerias requeridas:
    pip install -r requirements.txt
"""

import numpy as np
import matplotlib.pyplot as plt

from vpython import (
    canvas,
    box,
    sphere,
    cylinder,
    vector,
    color,
    rate,
    wtext,
    curve
)


# =============================================================================
# 1. FUNCIONES ANALITICAS
# =============================================================================

def h(t):
    """
    Altitud del dron h(t) en metros.

    h(t) = -0.1t^4 + 1.6t^3 - 7.2t^2 + 10t + 5
    """
    return (
        -0.1 * t**4
        + 1.6 * t**3
        - 7.2 * t**2
        + 10 * t
        + 5
    )


def v(t):
    """
    Velocidad vertical instantanea v(t) = h'(t).

    v(t) = -0.4t^3 + 4.8t^2 - 14.4t + 10
    """
    return (
        -0.4 * t**3
        + 4.8 * t**2
        - 14.4 * t
        + 10
    )


def a(t):
    """
    Aceleracion vertical a(t) = h''(t).

    Se utiliza para aplicar el criterio de la segunda derivada
    y para determinar la pendiente de la recta tangente.
    """
    return (
        -1.2 * t**2
        + 9.6 * t
        - 14.4
    )


def T(t, C=22.0):
    """
    Temperatura del motor T(t).

    T'(t) = 0.6t^2 - 2t + 4

    Antiderivada:

    T(t) = 0.2t^3 - t^2 + 4t + C

    Como T(0) = 22, entonces C = 22.
    """
    return (
        0.2 * t**3
        - t**2
        + 4 * t
        + C
    )


def D(t):
    """
    Consumo/transferencia de datos de la camara 4K.

    D(t) = 3t^2 + 2t + 5

    Unidad: MB/s
    """
    return 3 * t**2 + 2 * t + 5


def F(t):
    """
    Antiderivada de D(t).

    F(t) = t^3 + t^2 + 5t
    """
    return t**3 + t**2 + 5 * t


# =============================================================================
# 2. VALORES ANALITICOS CLAVE
# =============================================================================

V2 = v(2)
V6 = v(6)

# Integral definida entre t=1 y t=4
DATOS_TOTALES_1_4 = F(4) - F(1)

# Punto donde la velocidad tiene un maximo local:
# v'(t) = h''(t) = 0
T_MAX_VELOCIDAD = 6.0


print("=" * 65)
print("VALORES ANALITICOS PRECALCULADOS")
print("=" * 65)

print(f"v(2) = {V2:.4f} m/s")
print(f"v(6) = {V6:.4f} m/s")

print()
print("Funcion de temperatura:")
print("T(t) = 0.2t^3 - t^2 + 4t + 22")
print("Constante de integracion: C = 22")

print()
print(
    "Datos totales entre t=1 y t=4 "
    f"= {DATOS_TOTALES_1_4:.4f} MB"
)

print()
print("Puntos criticos de h(t): t = 1, 4 y 6 s")
print(f"h(1) = {h(1):.2f} m")
print(f"h(4) = {h(4):.2f} m")
print(f"h(6) = {h(6):.2f} m")

print()
print(f"Altura maxima durante el vuelo = {h(6):.2f} m")
print("=" * 65)


# =============================================================================
# 3. ESCENA 3D CON VPYTHON
# =============================================================================

scene = canvas(
    title=(
        "Simulacion 3D - Dron de Entregas "
        "(Calculo Diferencial e Integral)"
    ),
    width=1000,
    height=650,
    center=vector(0, 6, 0),
    background=color.gray(0.15)
)


# Escala visual de la altura
# Los valores mostrados en el HUD mantienen las unidades reales.
ESCALA_Y = 0.6

# Radio de la trayectoria horizontal
RADIO_TRAYECTORIA = 4.0


# =============================================================================
# 4. SUELO
# =============================================================================

suelo = box(
    pos=vector(0, -0.1, 0),
    size=vector(20, 0.2, 20),
    color=color.green,
    opacity=0.35
)


# =============================================================================
# 5. POSTE DE REFERENCIA DE ALTITUD
# =============================================================================

poste = cylinder(
    pos=vector(RADIO_TRAYECTORIA + 2, 0, 0),
    axis=vector(0, 22, 0),
    radius=0.05,
    color=color.white,
    opacity=0.3
)


# =============================================================================
# 6. MODELO 3D DEL DRON
# =============================================================================

cuerpo = box(
    pos=vector(
        RADIO_TRAYECTORIA,
        h(0) * ESCALA_Y,
        0
    ),
    size=vector(1.2, 0.25, 1.2),
    color=color.orange
)


# Motores del dron
motores = []

offsets = [
    vector(0.7, 0, 0.7),
    vector(-0.7, 0, 0.7),
    vector(0.7, 0, -0.7),
    vector(-0.7, 0, -0.7)
]


for off in offsets:
    motor = sphere(
        pos=cuerpo.pos + off,
        radius=0.18,
        color=color.red
    )

    motores.append(motor)


# =============================================================================
# 7. ESTELA DE LA TRAYECTORIA
# =============================================================================

estela = curve(
    color=color.cyan,
    radius=0.02
)


# =============================================================================
# 8. HUD DE TELEMETRIA
# =============================================================================

scene.append_to_caption(
    "\n\n--- TELEMETRIA EN TIEMPO REAL ---\n"
)

hud_tiempo = wtext(
    text="t = 0.00 s"
)

scene.append_to_caption("\n")

hud_altitud = wtext(
    text="Altitud h(t) = 0.00 m"
)

scene.append_to_caption("\n")

hud_velocidad = wtext(
    text="Velocidad h'(t) = 0.00 m/s"
)

scene.append_to_caption("\n")

hud_datos = wtext(
    text="Datos acumulados = 0.00 MB"
)

scene.append_to_caption("\n")

hud_temperatura = wtext(
    text="Temperatura T(t) = 22.00 °C"
)

scene.append_to_caption("\n")

hud_estado = wtext(
    text="Estado: vuelo en progreso"
)


# =============================================================================
# 9. PARAMETROS DE SIMULACION
# =============================================================================

FPS = 60
DT = 1.0 / FPS
T_FINAL = 10.0

t_actual = 0.0


# Integral numerica dinamica
datos_acumulados = 0.0

D_anterior = D(0.0)


# Historial para las graficas
hist_t = []
hist_h = []
hist_v = []
hist_D = []
hist_datos_acum = []
hist_T = []


# =============================================================================
# 10. BUCLE PRINCIPAL DE SIMULACION
# =============================================================================

while t_actual <= T_FINAL:

    rate(FPS)

    # -------------------------------------------------------------------------
    # POSICION 3D
    # -------------------------------------------------------------------------

    angulo = t_actual * 0.6

    x = RADIO_TRAYECTORIA * np.cos(angulo)
    z = RADIO_TRAYECTORIA * np.sin(angulo)

    y = h(t_actual) * ESCALA_Y


    # Actualizar posicion del cuerpo
    cuerpo.pos = vector(x, y, z)


    # Actualizar motores
    for motor, off in zip(motores, offsets):
        motor.pos = cuerpo.pos + off


    # Agregar punto a la estela
    estela.append(cuerpo.pos)


    # -------------------------------------------------------------------------
    # INTEGRACION NUMERICA DE D(t)
    # Regla del trapecio
    # -------------------------------------------------------------------------

    D_actual = D(t_actual)

    datos_acumulados += (
        (D_actual + D_anterior) / 2.0
    ) * DT

    D_anterior = D_actual


    # -------------------------------------------------------------------------
    # ACTUALIZAR HUD
    # -------------------------------------------------------------------------

    hud_tiempo.text = (
        f"t = {t_actual:5.2f} s"
    )

    hud_altitud.text = (
        f"Altitud h(t) = {h(t_actual):7.3f} m"
    )

    hud_velocidad.text = (
        f"Velocidad h'(t) = {v(t_actual):7.3f} m/s"
    )

    hud_datos.text = (
        f"Datos acumulados = "
        f"{datos_acumulados:7.3f} MB"
    )

    hud_temperatura.text = (
        f"Temperatura T(t) = "
        f"{T(t_actual):7.3f} °C"
    )


    # -------------------------------------------------------------------------
    # GUARDAR HISTORIAL
    # -------------------------------------------------------------------------

    hist_t.append(t_actual)
    hist_h.append(h(t_actual))
    hist_v.append(v(t_actual))
    hist_D.append(D_actual)
    hist_datos_acum.append(datos_acumulados)
    hist_T.append(T(t_actual))


    # Avanzar tiempo
    t_actual += DT


# =============================================================================
# 11. FINALIZACION
# =============================================================================

hud_estado.text = "Estado: simulacion finalizada"


print()
print(
    "Simulacion terminada."
)

print(
    "Datos acumulados totales "
    f"(0 a 10 s, numerico) = "
    f"{datos_acumulados:.3f} MB"
)

print(
    "Verificacion analitica exacta "
    "entre t=1 y t=4 = "
    f"{DATOS_TOTALES_1_4:.3f} MB"
)


# =============================================================================
# 12. GRAFICAS DE RESUMEN
# =============================================================================

def graficar_resumen():

    hist_t_np = np.array(hist_t)
    hist_h_np = np.array(hist_h)
    hist_v_np = np.array(hist_v)
    hist_D_np = np.array(hist_D)


    # -------------------------------------------------------------------------
    # CREAR FIGURA
    # -------------------------------------------------------------------------

    fig, (ax1, ax2, ax3) = plt.subplots(
        3,
        1,
        figsize=(9, 11)
    )

    fig.suptitle(
        "Telemetria Analitica del Dron - "
        "Resumen de Vuelo (0 a 10 s)",
        fontsize=13,
        fontweight="bold"
    )


    # =========================================================================
    # GRAFICA 1 - ALTITUD
    # =========================================================================

    ax1.plot(
        hist_t_np,
        hist_h_np,
        color="darkorange",
        linewidth=2,
        label="h(t)"
    )

    ax1.set_title(
        "Grafica 1: Altitud h(t)"
    )

    ax1.set_xlabel("t (s)")
    ax1.set_ylabel("Altitud (m)")

    ax1.grid(alpha=0.3)
    ax1.legend()


    # =========================================================================
    # GRAFICA 2 - VELOCIDAD Y TANGENTE
    # =========================================================================

    ax2.plot(
        hist_t_np,
        hist_v_np,
        color="royalblue",
        linewidth=2,
        label="v(t) = h'(t)"
    )


    t_tan = T_MAX_VELOCIDAD

    v_tan = v(t_tan)

    pendiente = a(t_tan)


    t_recta = np.linspace(
        t_tan - 1.5,
        t_tan + 1.5,
        10
    )


    recta_tangente = (
        v_tan
        + pendiente * (t_recta - t_tan)
    )


    ax2.plot(
        t_recta,
        recta_tangente,
        color="red",
        linestyle="--",
        linewidth=2,
        label=(
            f"Tangente en t={t_tan:.0f}s "
            f"(pendiente={pendiente:.2f})"
        )
    )


    ax2.scatter(
        [t_tan],
        [v_tan],
        color="red",
        zorder=5
    )


    ax2.set_title(
        "Grafica 2: Velocidad v(t) con "
        "recta tangente en el maximo"
    )

    ax2.set_xlabel("t (s)")
    ax2.set_ylabel("Velocidad (m/s)")

    ax2.grid(alpha=0.3)
    ax2.legend()


    # =========================================================================
    # GRAFICA 3 - TRANSFERENCIA DE DATOS
    # =========================================================================

    ax3.plot(
        hist_t_np,
        hist_D_np,
        color="seagreen",
        linewidth=2,
        label="D(t)"
    )


    mascara = (
        (hist_t_np >= 1)
        & (hist_t_np <= 4)
    )


    ax3.fill_between(
        hist_t_np[mascara],
        hist_D_np[mascara],
        color="seagreen",
        alpha=0.35,
        label=(
            f"Area = "
            f"{DATOS_TOTALES_1_4:.1f} MB "
            f"(t=1 a t=4)"
        )
    )


    ax3.set_title(
        "Grafica 3: Transferencia de datos D(t) "
        "- area bajo la curva"
    )

    ax3.set_xlabel("t (s)")
    ax3.set_ylabel("Datos (MB/s)")

    ax3.grid(alpha=0.3)
    ax3.legend()


    # Ajustar distribucion
    plt.tight_layout(
        rect=[0, 0, 1, 0.96]
    )

    plt.show()


# Ejecutar graficas
graficar_resumen()