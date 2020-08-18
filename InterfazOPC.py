from opcua import Client
from opcua import ua
import OpenOPC
import pywintypes
import csv
import time
import matplotlib.pyplot as plt
import tkinter as tk

# Linea necesaria para que funcione la comunicacion con OPC-DA
pywintypes.datetime = pywintypes.TimeType

# Ventana gráfica
root = tk.Tk()
root.title("MPC Reactor Híbrido")
canvas1 = tk.Canvas(root, width=300, height=300)
canvas1.pack()
button1 = tk.Button(root, text='Cerrar Aplicación', command=exit)
canvas1.create_window(150, 280, window=button1)
label = tk.Label(text="Controlador en ejecución...")
label.place(x=0, y=0)

# Iniciliazacion del programa
Controlador = False         # Activa el controlador luego de recoger datos
PeriodosEjecucion = 0
t_Sample = 30


def conexion_OPC():
    # Conexion con el servidor del controlador
    MPC = Client("opc.tcp://Labo6:16700/")    # Creacion objeto OPC-UA
    MPC.connect()                             # Conexion Controlador
    MPC.load_type_definitions()

    # Conexión con el servidor RTO
    RTO = Client("opc.tcp://Labo6:16701/")    # Creacion objeto OPC-UA
    RTO.connect()                             # Conexion Controlador
    RTO.load_type_definitions()
    # Conexion con los demas servidores
    SCADA = OpenOPC.client()                  # Creacion objeto OPC-DA
    PID1 = OpenOPC.client()                   # Creacion objeto OPC-DA
    PID2 = OpenOPC.client()                   # Creacion objeto OPC-DA

    SCADA.connect("LecturaOPC.1.0")
    PID1.connect("OPC.PID ISA (CreaOPC).1")
    PID2.connect("OPC.PID ISA 2 (CreaOPC).1")

    return [MPC, SCADA, PID1, PID2, RTO]


def lectura_SCADA():
    # Lectura de las variables de la planta y los parametros del controlador
    q = SCADA.read("Deck Variables.q")[0]
    qc = SCADA.read("Deck Variables.qc")[0]
    T0 = SCADA.read("Deck Variables.T0")[0]
    Tc0 = SCADA.read("Deck Variables.Tc0")[0]
    T = SCADA.read("Deck Variables.T")[0]
    Tc = SCADA.read("Deck Variables.Tc")[0]
    Ca = SCADA.read("Deck Variables.Ca")[0]
    T_sp = SCADA.read("Deck Variables.T_sp")[0]
    Ca_sp = SCADA.read("Deck Variables.Ca_sp")[0]
    gamma1 = SCADA.read("Deck Variables.gamma1")[0]
    gamma2 = SCADA.read("Deck Variables.gamma2")[0]
    beta1 = SCADA.read("Deck Variables.beta1")[0]
    beta2 = SCADA.read("Deck Variables.beta2")[0]

    return [q, qc, T0, Tc0, T, Tc, Ca, T_sp, Ca_sp, gamma1, gamma2, beta1, beta2]


def configuracion_MPC(T_sp, Ca_sp, gamma1, gamma2, beta1, beta2):
    MPC.get_node("ns=4;s=T_sp").set_value(
        ua.Variant(T_sp, ua.VariantType.Double))
    MPC.get_node("ns=4;s=Ca_sp").set_value(
        ua.Variant(Ca_sp, ua.VariantType.Double))
    MPC.get_node("ns=4;s=gamma[1]").set_value(
        ua.Variant(gamma1, ua.VariantType.Double))
    MPC.get_node("ns=4;s=gamma[2]").set_value(
        ua.Variant(gamma2, ua.VariantType.Double))
    MPC.get_node("ns=4;s=beta[1]").set_value(
        ua.Variant(beta1, ua.VariantType.Double))
    MPC.get_node("ns=4;s=beta[2]").set_value(
        ua.Variant(beta2, ua.VariantType.Double))

    return 0


def ComunicacionRTO():
    costos = [0]*5

    # Lectura de costos del Bloque Lectura
    costos[1] = SCADA.read("Deck Variables.CostoA")[0]
    costos[2] = SCADA.read("Deck Variables.CostoB")[0]
    costos[3] = SCADA.read("Deck Variables.CostoC")[0]
    costos[4] = SCADA.read("Deck Variables.CostoD")[0]
    costos[5] = SCADA.read("Deck Variables.CostoRef")[0]

    # Escritura de los costos al bloque RTO
    RTO.get_node("ns=4;s=CostoA").set_value(
        ua.Variant(costos[1], ua.VariantType.Double))
    RTO.get_node("ns=4;s=CostoB").set_value(
        ua.Variant(costos[2], ua.VariantType.Double))
    RTO.get_node("ns=4;s=CostoC").set_value(
        ua.Variant(costos[3], ua.VariantType.Double))
    RTO.get_node("ns=4;s=CostoD").set_value(
        ua.Variant(costos[4], ua.VariantType.Double))
    RTO.get_node("ns=4;s=CostoRef").set_value(
        ua.Variant(costos[5], ua.VariantType.Double))

    # Ejecución del RTO
    RTO.get_node("ns=2;s=server_methods").call_method(
        "5:method_run", ua.Variant("A String", ua.VariantType.String))

    # Leer set-points del RTO
    T_sp = RTO.get_node("ns=4;s=T").get_value()
    Ca_sp = RTO.get_node("ns=4;s=Ca").get_value()

    # Enviar set-points al SCADA
    SCADA.write(("Deck Variables.T_sp", T_sp))
    SCADA.write(("Deck Variables.Ca_sp", Ca_sp))
    return [T_sp, Ca_sp]


def Datos_MPC(q, qc, T0, Tc0, T, Tc, Ca):
    MPC.get_node("ns=4;s=uqant").set_value(
        ua.Variant(q, ua.VariantType.Double))
    MPC.get_node("ns=4;s=uqcant").set_value(
        ua.Variant(qc, ua.VariantType.Double))
    MPC.get_node("ns=4;s=q").set_value(
        ua.Variant(q, ua.VariantType.Double))
    MPC.get_node("ns=4;s=qc").set_value(
        ua.Variant(qc, ua.VariantType.Double))
    MPC.get_node("ns=4;s=T0").set_value(
        ua.Variant(T0, ua.VariantType.Double))
    MPC.get_node("ns=4;s=Tc0").set_value(
        ua.Variant(Tc0, ua.VariantType.Double))
    MPC.get_node("ns=4;s=T").set_value(
        ua.Variant(T, ua.VariantType.Double))
    MPC.get_node("ns=4;s=Tc").set_value(
        ua.Variant(Tc, ua.VariantType.Double))
    MPC.get_node("ns=4;s=Ca").set_value(
        ua.Variant(Ca, ua.VariantType.Double))
    return 0


def ejecutar_MPC():
    MPC.get_node("ns=2;s=server_methods").call_method(
        "5:method_run", ua.Variant("A String", ua.VariantType.String))
    return 0


def actualizar_PID():
    # Lectura set-point de las acciones de control
    q_sp = MPC.get_node("ns=4;s=q").get_value()
    qc_sp = MPC.get_node("ns=4;s=qc").get_value()

    # Escritura set-points al SCADA
    PID1.write(("EscrituraLectura.SP", q_sp))
    PID2.write(("EscrituraLectura.SP", qc_sp))

    return [q_sp, qc_sp]


def reportar(q, qc):
    print("\n" + time.strftime("%H:%M:%S") + ": Ejecucion terminada\n")
    print(f"\t  q  = {q:.2f} L/min")
    print(f"\t  qc = {qc:.2f} L/min")

    return 0


try:
    # Conexion a los servidores OPC
    [MPC, SCADA, PID1, PID2] = conexion_OPC()

    while True:
        tiempo_inicio = time.time()             # Contador de tiempo

        # Verificar si se ha activado/desactivado el controlardor desde el SCADA
        Auto_MPC = SCADA.read("Deck Variables.AutoMPC")[0]
        Auto_RTO = SCADA.read("Deck Variables.AutoRTO")[0]

        if Auto_MPC == 1:
            Controlador = False
            MPC.get_node("ns=4;s=FlagControlador").set_value(
                ua.Variant(0, ua.VariantType.Int32))
            # Actualizacion del periodo de ejecución
            PeriodosEjecucion += 1
            if PeriodosEjecucion > 6:
                Controlador = True
                MPC.get_node("ns=4;s=FlagControlador").set_value(
                    ua.Variant(1, ua.VariantType.Int32))

            # Lectura variables de la planta y parametros del controlador
            [q, qc, T0, Tc0, T, Tc, Ca, T_sp, Ca_sp, gamma1,
                gamma2, beta1, beta2] = lectura_SCADA()

            # Ejecutar RTO
            if Auto_RTO == 1:
                [T_sp, Ca_sp] = ComunicacionRTO()

            # Escritura de los parametros del controlador
            configuracion_MPC(T_sp, Ca_sp, gamma1, gamma2, beta1, beta2)

            # Escritura de los datos de la planta al controlador
            Datos_MPC(q, qc, T0, Tc0, T, Tc, Ca)

            # Ejecucion controlador, solo se soluciona el MHE y MPC si FlagControlador = 1
            ejecutar_MPC()

            if Controlador == True:
                # Obtener acciones de control y actualizar set-poit de los PID
                [q_sp, qc_sp] = actualizar_PID()
                # Reportar en pantallas las acciones de control
                reportar(q_sp, qc_sp)
            else:
                print("\n" + time.strftime("%H:%M:%S") +
                      ": Controlador activo, recolectando datos para MHE")

            a = (time.time() - tiempo_inicio)
            root.update()
            time.sleep(t_Sample - (time.time() - tiempo_inicio))

        elif Auto_MPC == 0:
            MPC.get_node("ns=4;s=FlagControlador").set_value(
                ua.Variant(0, ua.VariantType.Int32))
            Controlador = False
            PeriodosEjecucion = 0
            print("\n" + time.strftime("%H:%M:%S") +
                  ": Controlador desactivado")
            time.sleep(t_Sample)

except KeyboardInterrupt:

    SCADA.close()
    MPC.disconnect()
    PID1.disconnect()
    PID2.disconnect()

    print("\nSe han desconectado los servidores \n")
    exit()

finally:

    SCADA.close()
    MPC.disconnect()
    PID1.disconnect()
    PID2.disconnect()

    print("\nSe han desconectado los servidores \n")
    exit()
