#                       █████          █████ █████                                     
#                      ░░███          ░░███ ░░███                                      
#  ██████   ██████   ███████   ██████  ░░███ ███    █████  █████ ████  ██████   ██████ 
# ███░░███ ███░░███ ███░░███  ███░░███  ░░█████    ███░░  ░░███ ░███  ███░░███ ███░░███
#░███ ░░░ ░███ ░███░███ ░███ ░███████    ███░███  ░░█████  ░███ ░███ ░███████ ░███████ 
#░███  ███░███ ░███░███ ░███ ░███░░░    ███ ░░███  ░░░░███ ░███ ░███ ░███░░░  ░███░░░  
#░░██████ ░░██████ ░░████████░░██████  █████ █████ ██████  ░░████████░░██████ ░░██████ 
# ░░░░░░   ░░░░░░   ░░░░░░░░  ░░░░░░  ░░░░░ ░░░░░ ░░░░░░    ░░░░░░░░  ░░░░░░   ░░░░░░             

import tkinter as tk
import random
import time
from collections import deque
from graphviz import Digraph
from PIL import Image, ImageTk

def crear_interfaz():
    ventana = tk.Tk()
    ventana.geometry("1200x700")
    ventana.resizable(False, False)
    ventana.overrideredirect(True)

    ancho_ventana, alto_ventana = 1200, 700
    ancho_pantalla, alto_pantalla = ventana.winfo_screenwidth(), ventana.winfo_screenheight()
    pos_x_ventana = (ancho_pantalla - ancho_ventana) // 2
    pos_y_ventana = (alto_pantalla - alto_ventana) // 2
    ventana.geometry(f"{ancho_ventana}x{alto_ventana}+{pos_x_ventana}+{pos_y_ventana}")

    fondo_mate = "#2B2B2B"
    contenedor_mate = "#3A3A3A"
    boton_mate = "#4F4F4F"
    texto_mate = "#D1D1D1"

    ventana.configure(bg=fondo_mate)

    cont_ancho, cont_alto = 450, 450
    pos_x_cont = (500 - cont_ancho) // 2
    pos_y_cont = (700 - cont_alto) - 25
    contenedor = tk.Frame(ventana, width=cont_ancho, height=cont_alto, bg=contenedor_mate)
    contenedor.place(x=pos_x_cont, y=pos_y_cont)

    orden_objetivo = [1, 2, 3, 8, None, 4, 7, 6, 5]
    orden = orden_objetivo[:]

    def es_resoluble(inicial, objetivo):
        def contar_inversiones(estado):
            estado_plano = [x for x in estado if x is not None]
            inversiones = 0
            for i in range(len(estado_plano)):
                for j in range(i + 1, len(estado_plano)):
                    if estado_plano[i] > estado_plano[j]:
                        inversiones += 1
            return inversiones

        inversiones_inicial = contar_inversiones(inicial)
        inversiones_objetivo = contar_inversiones(objetivo)
        return (inversiones_inicial % 2) == (inversiones_objetivo % 2)

    def actualizar_botones():
        while True:
            random.shuffle(orden)
            if orden != orden_objetivo and es_resoluble(orden, orden_objetivo):
                break
        mostrar_botones()
        mostrar_texto_consola("Los elementos se han desordenado.", "amarillo")

    def mostrar_botones():
        for widget in contenedor.winfo_children():
            widget.destroy()
        index = 0
        for fila in range(3):
            for col in range(3):
                celda = tk.Frame(contenedor, width=150, height=150, bg=contenedor_mate, highlightbackground=fondo_mate, highlightthickness=1)
                celda.grid(row=fila, column=col)
                celda.grid_propagate(False)
                valor = orden[index]
                if valor is not None:
                    boton = tk.Button(
                        celda, text=str(valor), font=("Arial", 24, "bold"),
                        bg=boton_mate, fg=texto_mate, relief="flat", bd=0
                    )
                    boton.place(relx=0, rely=0, relwidth=1, relheight=1)
                index += 1

    mostrar_botones()

    def encontrar_camino():
        inicial = tuple(orden)
        objetivo = tuple(orden_objetivo)

        if inicial == objetivo:
            mostrar_texto_consola("Error: los elementos ya están ordenados.", "rojo")
            return None, None

        def obtener_hijos(estado):
            hijos = []
            idx_vacio = estado.index(None)
            fila, col = idx_vacio // 3, idx_vacio % 3
            movimientos = [(-1, 0), (1, 0), (0, -1), (0, 1)]

            for dx, dy in movimientos:
                nueva_fila, nueva_col = fila + dx, col + dy
                if 0 <= nueva_fila < 3 and 0 <= nueva_col < 3:
                    nuevo_idx = nueva_fila * 3 + nueva_col
                    nuevo_estado = list(estado)
                    nuevo_estado[idx_vacio], nuevo_estado[nuevo_idx] = nuevo_estado[nuevo_idx], nuevo_estado[idx_vacio]
                    hijos.append(tuple(nuevo_estado))

            return hijos

        visitados = set()
        padres = {}
        cola = deque([(inicial, None)])
        visitados.add(inicial)

        camino = None
        while cola:
            estado, padre = cola.popleft()

            if estado == objetivo:
                camino = []
                estado_actual = estado
                while estado_actual is not None:
                    camino.append(estado_actual)
                    estado_actual = padres.get(estado_actual)
                camino.reverse()
                break

            for hijo in obtener_hijos(estado):
                if hijo not in visitados:
                    visitados.add(hijo)
                    padres[hijo] = estado
                    cola.append((hijo, estado))

        if camino is None:
            mostrar_texto_consola("No se encontró solución.", "rojo")
            return None, None

        return camino, padres

    def mostrar_texto_consola(mensaje, color):
        consola.insert(tk.END, mensaje + "\n", color)
        consola.yview(tk.END)

    def dibujar_arbol(proceso, padres):
        dot = Digraph(format='png', engine='dot')
        dot.attr(rankdir='TB')
        dot.attr(dpi='300')
        dot.attr('node', shape='box', style='filled', fillcolor='lightgray', fontname="Arial", fontsize="14")
        dot.attr('edge', penwidth="1.5")
        dot.attr('graph', splines='line', nodesep='0.5', ranksep='1.0')

        nodos = {}
        niveles = {}

        inicial = tuple(proceso[0])
        objetivo = tuple(orden_objetivo)

        for idx, estado in enumerate(proceso):
            niveles[estado] = idx

        sub_arbol_padres = {}
        estados_camino = set(proceso)

        for i in range(len(proceso) - 1):
            sub_arbol_padres[proceso[i + 1]] = proceso[i]

        def obtener_hijos(estado):
            hijos = []
            idx_vacio = estado.index(None)
            fila, col = idx_vacio // 3, idx_vacio % 3
            movimientos = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            for dx, dy in movimientos:
                nueva_fila, nueva_col = fila + dx, col + dy
                if 0 <= nueva_fila < 3 and 0 <= nueva_col < 3:
                    nuevo_idx = nueva_fila * 3 + nueva_col
                    nuevo_estado = list(estado)
                    nuevo_estado[idx_vacio], nuevo_estado[nuevo_idx] = nuevo_estado[nuevo_idx], nuevo_estado[idx_vacio]
                    hijos.append(tuple(nuevo_estado))
            return hijos

        for estado in proceso[:-1]:
            hijos = obtener_hijos(estado)
            for hijo in hijos:
                if hijo not in estados_camino:
                    sub_arbol_padres[hijo] = estado
                    niveles[hijo] = niveles[estado] + 1

        idx = 0
        estados_unicos = set(proceso).union(set(sub_arbol_padres.keys())).union(set(sub_arbol_padres.values()))
        for estado in estados_unicos:
            label = "\n".join([
                " ".join(["_" if x is None else str(x) for x in estado[i:i+3]])
                for i in range(0, 9, 3)
            ])
            nodo_id = f"n{idx}"
            nodos[estado] = nodo_id

            if estado == objetivo:
                dot.node(nodo_id, label=label, fillcolor="lightgreen", penwidth="2", color="red")
            elif estado in estados_camino:
                dot.node(nodo_id, label=label, fillcolor="lightblue")
            else:
                dot.node(nodo_id, label=label)

            idx += 1

        for hijo, padre in sub_arbol_padres.items():
            dot.edge(nodos[padre], nodos[hijo], constraint='true')

        max_nivel = max(niveles.values()) if niveles else 0
        for nivel in range(max_nivel + 1):
            nodos_en_nivel = [nodos[estado] for estado, niv in niveles.items() if niv == nivel]
            if nodos_en_nivel:
                with dot.subgraph() as s:
                    s.attr(rank='same')
                    for nodo in nodos_en_nivel:
                        s.node(nodo)

        try:
            dot.render(r'C:\Users\PC\Desktop\PROYECTOS\8 puzzle\arbol_busqueda', view=False, cleanup=False)
        except Exception as e:
            mostrar_texto_consola(f"Error al renderizar el árbol: {str(e)}", "rojo")
            return

        try:
            img = Image.open('arbol_busqueda.png')
            contenedor_width = 450
            aspect_ratio = img.height / img.width
            new_width = contenedor_width
            new_height = int(new_width * aspect_ratio)

            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)

            contenedor_arbol.delete("all")
            contenedor_arbol.create_image(0, 0, anchor="nw", image=img_tk)
            contenedor_arbol.config(scrollregion=(0, 0, new_width, new_height))
            contenedor_arbol.image = img_tk
        except Exception as e:
            mostrar_texto_consola(f"Error al mostrar el árbol: {str(e)}", "rojo")
            return

    def es_padre(estado_padre, estado_hijo):
        diferencia = sum(1 for a, b in zip(estado_padre, estado_hijo) if a != b)
        return diferencia == 1

    def imprimir_pasos(proceso, padres, idx=0):
        if idx < len(proceso):
            orden[:] = list(proceso[idx])
            mostrar_botones()
            imprimir_estado_en_consola(proceso[idx])
            dibujar_arbol(proceso[:idx+1], padres)
            ventana.after(300, imprimir_pasos, proceso, padres, idx + 1)
        else:
            mostrar_texto_consola("Elementos ordenados correctamente.", "blanco")
            dibujar_arbol(proceso, padres)

    def imprimir_estado_en_consola(estado):
        for i in range(0, 9, 3):
            fila = ""
            for j in range(3):
                valor = estado[i + j]
                fila += "[_] " if valor is None else f"[{valor}] "
            consola.insert(tk.END, fila + "\n")
        consola.insert(tk.END, "\n")
        consola.yview(tk.END)

    def ordenar():
        resultado = encontrar_camino()
        if not resultado:
            return
        proceso, padres = resultado
        mostrar_texto_consola("Ordenando...", "azul")
        imprimir_pasos(proceso, padres)

    ventana.bind("<B1-Motion>", lambda evento: None)

    boton_cerrar = tk.Button(ventana, text="X", font=("Arial", 15, "bold"), command=ventana.destroy, bg="#B22222", fg="white", bd=0, relief="flat", highlightthickness=0)
    boton_cerrar.place(x=3, y=3)
    boton_cerrar.lift()

    titulo = tk.Label(ventana, text="8_PUZZLE", font=("Arial", 50, "bold"), bg=fondo_mate, fg=texto_mate)
    titulo.place(x=140, y=30)

    frame_botonera = tk.Frame(ventana, bg=fondo_mate)
    frame_botonera.place(x=35, y=150, width=500, height=50)

    boton_desordenar = tk.Button(frame_botonera, text="Desordenar", font=("Arial", 12, "bold"), bg=boton_mate, fg=texto_mate, width=20, relief="flat", bd=0, command=actualizar_botones)
    boton_desordenar.grid(row=0, column=0, padx=13)

    boton_ordenar = tk.Button(frame_botonera, text="Ordenar", font=("Arial", 12, "bold"), bg=boton_mate, fg=texto_mate, width=20, relief="flat", bd=0, command=ordenar)
    boton_ordenar.grid(row=0, column=1, padx=10)

    consola = tk.Text(ventana, width=20, height=40, bg="#1E1E1E", fg="green", font=("Courier", 12), relief="flat", bd=2, insertbackground="white")
    consola.place(x=500, y=25, width=200, height=650)

    contenedor_arbol = tk.Canvas(ventana, bg="#dcdcdc", width=450, height=645)
    contenedor_arbol.place(x=725, y=25)

    scroll_y = tk.Scrollbar(ventana, orient="vertical", command=contenedor_arbol.yview, bg=fondo_mate, troughcolor=fondo_mate, bd=0, highlightthickness=0)
    contenedor_arbol.configure(yscrollcommand=scroll_y.set)
    scroll_y.place(x=1175, y=25, height=645)

    consola.tag_config("amarillo", foreground="yellow")
    consola.tag_config("rojo", foreground="red")
    consola.tag_config("blanco", foreground="white")
    consola.tag_config("azul", foreground="blue")

    ventana.mainloop()

if __name__ == '__main__':
    crear_interfaz()

#                       █████          █████ █████                                     
#                      ░░███          ░░███ ░░███                                      
#  ██████   ██████   ███████   ██████  ░░███ ███    █████  █████ ████  ██████   ██████ 
# ███░░███ ███░░███ ███░░███  ███░░███  ░░█████    ███░░  ░░███ ░███  ███░░███ ███░░███
#░███ ░░░ ░███ ░███░███ ░███ ░███████    ███░███  ░░█████  ░███ ░███ ░███████ ░███████ 
#░███  ███░███ ░███░███ ░███ ░███░░░    ███ ░░███  ░░░░███ ░███ ░███ ░███░░░  ░███░░░  
#░░██████ ░░██████ ░░████████░░██████  █████ █████ ██████  ░░████████░░██████ ░░██████ 
# ░░░░░░   ░░░░░░   ░░░░░░░░  ░░░░░░  ░░░░░ ░░░░░ ░░░░░░    ░░░░░░░░  ░░░░░░   ░░░░░░        