# Interfaz gráfica del analizador de Swift (Tkinter)
# Proyecto de Lenguajes de Programación 2026-II - ESPOL
# Integrantes: Kevin Morales, Kenny Chung, Miguel Medina
#
# Uso:
#   python interfaz.py
#
# Permite escribir o abrir un archivo .swift y ejecutar el análisis léxico,
# sintáctico y semántico. Muestra los tokens, el árbol sintáctico, la tabla
# de símbolos y los errores de cada fase con su línea. Cada análisis genera
# el log de su fase en logs/, con el nombre del desarrollador elegido.

import bisect
import os
import re
import tkinter as tk
import tkinter.font as tkfont
from tkinter import filedialog, messagebox, ttk

import ply.lex as lex

import lexer as lexer_module
import parser as parser_module
import semantico as semantico_module

CARPETA_PROYECTO = os.path.dirname(os.path.abspath(__file__))
CARPETA_ALGORITMOS = os.path.join(CARPETA_PROYECTO, 'algoritmos')

# Nombre que lleva el log léxico y usuario de Git que llevan los otros dos.
DESARROLLADORES = {
    'Kevin Morales': ('KevinMorales', 'kevin-moralesc'),
    'Kenny Chung': ('KennyChung', 'Kenny28-176'),
    'Miguel Medina': ('MiguelMedina', 'Miguelmml16'),
}

# Cada fase conserva el mismo color en su botón, en sus errores y en la
# barra de estado.
LEXICO, SINTACTICO, SEMANTICO = 'LÉXICO', 'SINTÁCTICO', 'SEMÁNTICO'
FASES = (LEXICO, SINTACTICO, SEMANTICO)
COLORES = {LEXICO: '#18794e', SINTACTICO: '#1d5fc4', SEMANTICO: '#7a3db8'}
COLOR_COMPLETO = '#d9480f'
NOMBRES = {LEXICO: 'Léxico', SINTACTICO: 'Sintáctico', SEMANTICO: 'Semántico'}

FUENTE = ('Segoe UI', 10)
FUENTE_NEGRITA = ('Segoe UI', 10, 'bold')
FUENTE_CODIGO = ('Consolas', 11)

# Colores del código en el editor.
COLORES_CODIGO = {
    'reservada': '#a626a4',
    'tipo': '#0b7285',
    'funcion': '#2f6fd0',
    'cadena': '#b3421f',
    'numero': '#986801',
    'comentario': '#6a737d',
}

PATRON_RESALTADO = re.compile(
    r'(?P<comentario>//[^\n]*|/\*.*?\*/)'
    r'|(?P<cadena>"(?:[^"\n\\]|\\.)*")'
    r'|(?P<numero>\b\d+(?:\.\d+)?\b)'
    r'|(?P<palabra>\b[A-Za-z_][A-Za-z0-9_]*\b)',
    re.S
)

# Etiqueta de color de cada palabra reservada, según su token en el lexer.
ETIQUETA_PALABRA = {}
for palabra, token in lexer_module.reserved.items():
    if token.startswith('TYPE_'):
        ETIQUETA_PALABRA[palabra] = 'tipo'
    elif token in ('PRINT', 'READLINE'):
        ETIQUETA_PALABRA[palabra] = 'funcion'
    else:
        ETIQUETA_PALABRA[palabra] = 'reservada'


# ---------------------------------------------------------------------------
# Análisis
# ---------------------------------------------------------------------------
# Ejecuta las fases en orden hasta la que se pida y devuelve los resultados
# en un diccionario. De cada fase queda su lista de errores, o None si no se
# ejecutó. El análisis semántico solo se ejecuta si no hubo errores léxicos
# ni sintácticos, igual que en semantico.py.
def analizar_codigo(codigo, hasta):
    resultado = {
        'tokens': [], 'arbol': None, 'simbolos': [],
        LEXICO: [], SINTACTICO: None, SEMANTICO: None,
    }

    resultado['tokens'], resultado[LEXICO] = lexer_module.analizar(codigo)
    if hasta == LEXICO:
        return resultado

    parser_module.codigo_actual = codigo
    parser_module.errores_sintacticos.clear()

    lexer_base = lex.lex(module=lexer_module)
    lexer_base.errores = []

    resultado['arbol'] = parser_module.parser.parse(
        codigo,
        lexer=parser_module.LexerConSeparadores(lexer_base),
        tracking=True
    )
    resultado[SINTACTICO] = list(parser_module.errores_sintacticos)
    if hasta == SINTACTICO:
        return resultado

    sin_errores = not resultado[LEXICO] and not resultado[SINTACTICO]
    if sin_errores and resultado['arbol'] is not None:
        resultado[SEMANTICO] = list(
            semantico_module.analizar(resultado['arbol'])
        )
        resultado['simbolos'] = list(semantico_module.tabla.historial)

    return resultado


# Saca la línea y la columna del mensaje de error. Los errores semánticos no
# tienen columna, y el de fin de archivo inesperado no tiene línea: se ubica
# en la última línea del código.
def ubicar_error(mensaje, total_lineas):
    posicion = re.search(r'en la línea (\d+), columna (\d+)', mensaje)
    if posicion:
        return int(posicion.group(1)), int(posicion.group(2))

    posicion = re.search(r'\(línea (\d+)\)', mensaje)
    if posicion:
        return int(posicion.group(1)), None

    return total_lineas, None


def cuantos(cantidad, singular, plural):
    return f"{cantidad} {singular if cantidad == 1 else plural}"


# ---------------------------------------------------------------------------
# Ventana principal
# ---------------------------------------------------------------------------
class Interfaz(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Analizador de Swift - Léxico, Sintáctico y Semántico (PLY)')

        # Factor para que los tamaños en píxeles se vean igual en pantallas
        # con escala de 125 % o 150 %.
        self.escala = self.winfo_fpixels('1i') / 96
        ancho = min(self.px(1320), self.winfo_screenwidth() - 60)
        alto = min(self.px(780), self.winfo_screenheight() - 110)
        self.geometry(f'{ancho}x{alto}')
        self.minsize(self.px(900), self.px(520))

        self.ruta = None              # archivo abierto en el editor
        self.salto_linea = '\n'       # fin de línea del archivo abierto
        self.hay_cambios = False
        self.errores_por_linea = {}   # línea -> color de la fase del error
        self.tarea_resaltado = None

        estilo = ttk.Style(self)
        estilo.configure('Treeview', font=FUENTE, rowheight=self.px(22))
        estilo.configure('Treeview.Heading', font=FUENTE_NEGRITA)
        estilo.configure('TNotebook.Tab', font=FUENTE, padding=(10, 3))

        self.crear_barra_superior()
        self.crear_barra_estado()
        self.crear_paneles()

        self.bind('<Control-o>', lambda evento: self.abrir())
        self.bind('<Control-s>', lambda evento: self.guardar())
        self.bind('<F5>', lambda evento: self.analizar(SEMANTICO, True))
        self.protocol('WM_DELETE_WINDOW', self.cerrar)

        self.limpiar_resultados()
        self.actualizar_nombre()

    def px(self, valor):
        return int(valor * self.escala)

    # ---------------------------- Construcción ----------------------------
    def crear_barra_superior(self):
        barra = tk.Frame(self, padx=10, pady=8)
        barra.pack(fill='x')

        for texto, accion in (('Abrir .swift', self.abrir),
                              ('Guardar', self.guardar),
                              ('Limpiar', self.limpiar)):
            ttk.Button(barra, text=texto, command=accion).pack(
                side='left', padx=(0, 6))

        ttk.Separator(barra, orient='vertical').pack(
            side='left', fill='y', padx=8)

        botones = (
            ('▶ Léxico', COLORES[LEXICO], lambda: self.analizar(LEXICO)),
            ('▶ Sintáctico', COLORES[SINTACTICO],
             lambda: self.analizar(SINTACTICO)),
            ('▶ Semántico', COLORES[SEMANTICO],
             lambda: self.analizar(SEMANTICO)),
            ('▶ Análisis completo', COLOR_COMPLETO,
             lambda: self.analizar(SEMANTICO, True)),
        )
        for texto, color, accion in botones:
            tk.Button(
                barra, text=texto, command=accion, font=FUENTE_NEGRITA,
                bg=color, fg='white', activebackground=color,
                activeforeground='white', relief='flat', cursor='hand2',
                padx=12, pady=3
            ).pack(side='left', padx=(0, 6))

        # El desarrollador elegido da nombre a los logs de la prueba.
        self.desarrollador = tk.StringVar()
        ttk.Combobox(
            barra, textvariable=self.desarrollador, state='readonly',
            values=list(DESARROLLADORES), width=16, font=FUENTE
        ).pack(side='right')
        tk.Label(barra, text='Desarrollador:', font=FUENTE).pack(
            side='right', padx=(14, 6))

        self.generar_log = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            barra, text='Generar log', variable=self.generar_log
        ).pack(side='right')

    def crear_barra_estado(self):
        fondo = '#e4e7eb'
        barra = tk.Frame(self, bg=fondo, padx=10, pady=4)
        barra.pack(fill='x', side='bottom')

        self.estado = {}
        for fase in FASES:
            etiqueta = tk.Label(barra, bg=fondo, fg=COLORES[fase],
                                font=FUENTE_NEGRITA)
            etiqueta.pack(side='left', padx=(0, 20))
            self.estado[fase] = etiqueta

        self.estado_log = tk.Label(barra, bg=fondo, font=FUENTE)
        self.estado_log.pack(side='left')

        self.estado_cursor = tk.Label(barra, bg=fondo, font=FUENTE,
                                      text='Ln 1, Col 1')
        self.estado_cursor.pack(side='right')

    def crear_paneles(self):
        division = ttk.PanedWindow(self, orient='horizontal')
        division.pack(fill='both', expand=True, padx=10, pady=(0, 8))

        izquierda = ttk.Frame(division)
        derecha = ttk.PanedWindow(division, orient='vertical')
        division.add(izquierda, weight=5)
        division.add(derecha, weight=6)

        self.crear_editor(izquierda)
        self.crear_resultados(derecha)
        self.crear_panel_errores(derecha)

        # Al abrir, el editor ocupa un poco menos de la mitad de la ventana.
        # Se espera a que la ventana tenga su tamaño real para ubicar la
        # división.
        def ubicar_division(evento):
            if evento.width > 1:
                division.unbind('<Configure>')
                division.sashpos(0, int(evento.width * 0.45))

        division.bind('<Configure>', ubicar_division)

    def crear_editor(self, marco):
        self.nombre_archivo = tk.Label(marco, font=FUENTE_NEGRITA, anchor='w')
        self.nombre_archivo.pack(fill='x', pady=(0, 4))

        caja = tk.Frame(marco, bd=1, relief='solid')
        caja.pack(fill='both', expand=True)
        caja.rowconfigure(0, weight=1)
        caja.columnconfigure(1, weight=1)

        fuente = tkfont.Font(font=FUENTE_CODIGO)
        self.ancho_margen = fuente.measure('0000') + self.px(18)

        # Margen con los números de línea y la marca de las líneas con error.
        self.margen = tk.Canvas(caja, width=self.ancho_margen, bg='#f1f3f5',
                                highlightthickness=0)
        self.margen.grid(row=0, column=0, sticky='ns')

        self.editor = tk.Text(
            caja, wrap='none', undo=True, font=FUENTE_CODIGO, relief='flat',
            bg='white', fg='#1f2328', insertbackground='#1f2328',
            padx=8, pady=6, tabs=fuente.measure('    ')
        )
        self.editor.grid(row=0, column=1, sticky='nsew')

        barra_v = ttk.Scrollbar(caja, orient='vertical',
                                command=self.editor.yview)
        barra_v.grid(row=0, column=2, sticky='ns')
        barra_h = ttk.Scrollbar(caja, orient='horizontal',
                                command=self.editor.xview)
        barra_h.grid(row=1, column=1, sticky='ew')

        # Cada vez que el editor se desplaza se vuelven a dibujar los números.
        def al_desplazar(inicio, fin):
            barra_v.set(inicio, fin)
            self.dibujar_margen()

        self.editor.configure(yscrollcommand=al_desplazar,
                              xscrollcommand=barra_h.set)

        for etiqueta, color in COLORES_CODIGO.items():
            self.editor.tag_configure(etiqueta, foreground=color)
        self.editor.tag_configure('linea_error', background='#ffecec')
        self.editor.tag_configure('error_actual', background='#ffd6d6',
                                  underline=True)
        self.editor.tag_raise('sel')

        self.editor.bind('<<Modified>>', self.al_modificar)
        self.editor.bind('<KeyRelease>', self.actualizar_cursor)
        self.editor.bind('<ButtonRelease-1>', self.actualizar_cursor)

    # Tabla con barra de desplazamiento. Cada columna llega como
    # (identificador, título, ancho, alineación).
    def crear_tabla(self, marco, columnas, horizontal=False):
        marco.rowconfigure(0, weight=1)
        marco.columnconfigure(0, weight=1)

        tabla = ttk.Treeview(marco, show='headings', selectmode='browse',
                             columns=[columna[0] for columna in columnas])
        for identificador, titulo, ancho, alineacion in columnas:
            tabla.heading(identificador, text=titulo, anchor=alineacion)
            tabla.column(identificador, width=self.px(ancho),
                         anchor=alineacion, stretch=False)
        if not horizontal:
            tabla.column(columnas[-1][0], stretch=True)
        tabla.grid(row=0, column=0, sticky='nsew')

        barra = ttk.Scrollbar(marco, orient='vertical', command=tabla.yview)
        barra.grid(row=0, column=1, sticky='ns')
        tabla.configure(yscrollcommand=barra.set)

        if horizontal:
            barra_h = ttk.Scrollbar(marco, orient='horizontal',
                                    command=tabla.xview)
            barra_h.grid(row=1, column=0, sticky='ew')
            tabla.configure(xscrollcommand=barra_h.set)

        return tabla

    def crear_resultados(self, division):
        self.pestanas = ttk.Notebook(division)
        division.add(self.pestanas, weight=3)

        # Tokens
        marco = ttk.Frame(self.pestanas)
        self.tabla_tokens = self.crear_tabla(marco, (
            ('numero', '#', 55, 'e'),
            ('linea', 'Línea', 60, 'e'),
            ('columna', 'Columna', 75, 'e'),
            ('token', 'Token', 170, 'w'),
            ('lexema', 'Lexema', 300, 'w'),
        ))
        self.pestanas.add(marco, text='Tokens')

        # Árbol sintáctico
        marco = ttk.Frame(self.pestanas)
        acciones = tk.Frame(marco)
        acciones.pack(fill='x', pady=4)
        ttk.Button(acciones, text='Expandir todo',
                   command=lambda: self.abrir_nodos(True)).pack(
                       side='left', padx=(4, 6))
        ttk.Button(acciones, text='Contraer todo',
                   command=lambda: self.abrir_nodos(False)).pack(side='left')

        caja = ttk.Frame(marco)
        caja.pack(fill='both', expand=True)
        caja.rowconfigure(0, weight=1)
        caja.columnconfigure(0, weight=1)
        self.arbol = ttk.Treeview(caja, show='tree', selectmode='browse')
        self.arbol.grid(row=0, column=0, sticky='nsew')
        barra = ttk.Scrollbar(caja, orient='vertical',
                              command=self.arbol.yview)
        barra.grid(row=0, column=1, sticky='ns')
        self.arbol.configure(yscrollcommand=barra.set)
        self.pestanas.add(marco, text='Árbol sintáctico')

        # Tabla de símbolos
        marco = ttk.Frame(self.pestanas)
        self.tabla_simbolos = self.crear_tabla(marco, (
            ('nombre', 'Nombre', 170, 'w'),
            ('categoria', 'Categoría', 100, 'w'),
            ('tipo', 'Tipo', 230, 'w'),
            ('linea', 'Línea', 60, 'e'),
            ('ambito', 'Ámbito', 120, 'w'),
        ))
        self.pestanas.add(marco, text='Tabla de símbolos')

        # Log
        marco = ttk.Frame(self.pestanas)
        marco.rowconfigure(0, weight=1)
        marco.columnconfigure(0, weight=1)
        self.texto_log = tk.Text(marco, wrap='none', font=('Consolas', 10),
                                 relief='flat', bg='#fbfbfc', padx=8, pady=6,
                                 state='disabled')
        self.texto_log.grid(row=0, column=0, sticky='nsew')
        barra = ttk.Scrollbar(marco, orient='vertical',
                              command=self.texto_log.yview)
        barra.grid(row=0, column=1, sticky='ns')
        barra_h = ttk.Scrollbar(marco, orient='horizontal',
                                command=self.texto_log.xview)
        barra_h.grid(row=1, column=0, sticky='ew')
        self.texto_log.configure(yscrollcommand=barra.set,
                                 xscrollcommand=barra_h.set)
        self.pestanas.add(marco, text='Log')

    def crear_panel_errores(self, division):
        marco = ttk.Frame(division)
        division.add(marco, weight=2)

        self.titulo_errores = tk.Label(marco, font=FUENTE_NEGRITA, anchor='w')
        self.titulo_errores.pack(fill='x', pady=(8, 4))

        caja = ttk.Frame(marco)
        caja.pack(fill='both', expand=True)
        self.tabla_errores = self.crear_tabla(caja, (
            ('fase', 'Fase', 100, 'w'),
            ('linea', 'Línea', 55, 'e'),
            ('columna', 'Columna', 70, 'e'),
            ('mensaje', 'Mensaje', 900, 'w'),
        ), horizontal=True)

        # La fase se distingue por el texto de la columna y por el color.
        for fase, color in COLORES.items():
            self.tabla_errores.tag_configure(fase, foreground=color)
        self.tabla_errores.bind('<<TreeviewSelect>>', self.ir_al_error)

    # ------------------------------ Editor --------------------------------
    def dibujar_margen(self):
        self.margen.delete('all')
        ultima = int(self.editor.index('end-1c').split('.')[0])
        linea = int(self.editor.index('@0,0').split('.')[0])

        while linea <= ultima:
            posicion = self.editor.dlineinfo(f'{linea}.0')
            if posicion is None:
                break
            y = posicion[1]
            alto = posicion[3]

            if linea in self.errores_por_linea:
                radio = self.px(4)
                centro = y + alto // 2
                self.margen.create_oval(
                    self.px(5), centro - radio,
                    self.px(5) + 2 * radio, centro + radio,
                    fill=self.errores_por_linea[linea], outline=''
                )
            self.margen.create_text(
                self.ancho_margen - self.px(6), y, anchor='ne',
                text=str(linea), font=FUENTE_CODIGO, fill='#8a8f98'
            )
            linea += 1

    def al_modificar(self, evento=None):
        if not self.editor.edit_modified():
            return
        self.editor.edit_modified(False)

        self.hay_cambios = True
        self.actualizar_nombre()

        # Las marcas de error ya no corresponden al código que cambió.
        self.quitar_marcas_de_error()

        # El resaltado espera a que se deje de escribir.
        if self.tarea_resaltado is not None:
            self.after_cancel(self.tarea_resaltado)
        self.tarea_resaltado = self.after(200, self.resaltar)

    def resaltar(self):
        self.tarea_resaltado = None
        codigo = self.editor.get('1.0', 'end-1c')

        for etiqueta in COLORES_CODIGO:
            self.editor.tag_remove(etiqueta, '1.0', 'end')

        # Posición donde empieza cada línea, para pasar de la posición en el
        # texto al índice línea.columna del editor.
        inicios = [0] + [salto.end() for salto in re.finditer('\n', codigo)]

        def indice(posicion):
            linea = bisect.bisect_right(inicios, posicion)
            return f'{linea}.{posicion - inicios[linea - 1]}'

        for coincidencia in PATRON_RESALTADO.finditer(codigo):
            etiqueta = coincidencia.lastgroup
            if etiqueta == 'palabra':
                etiqueta = ETIQUETA_PALABRA.get(coincidencia.group())
                if etiqueta is None:
                    continue
            self.editor.tag_add(etiqueta, indice(coincidencia.start()),
                                indice(coincidencia.end()))

    def actualizar_cursor(self, evento=None):
        linea, columna = self.editor.index('insert').split('.')
        self.estado_cursor.configure(text=f'Ln {linea}, Col {int(columna) + 1}')

    def actualizar_nombre(self):
        if self.ruta is None:
            nombre = 'Sin título'
        else:
            nombre = os.path.basename(self.ruta)
        if self.hay_cambios:
            nombre += '  (sin guardar)'
        self.nombre_archivo.configure(text=nombre)

    def poner_codigo(self, codigo):
        self.editor.delete('1.0', 'end')
        self.editor.insert('1.0', codigo)
        self.editor.edit_reset()
        self.editor.edit_modified(False)
        self.editor.mark_set('insert', '1.0')

        self.hay_cambios = False
        self.limpiar_resultados()
        self.resaltar()
        self.actualizar_nombre()
        self.actualizar_cursor()
        self.dibujar_margen()

    # ----------------------------- Archivos -------------------------------
    def descartar_cambios(self):
        if not self.hay_cambios:
            return True
        return messagebox.askyesno(
            'Cambios sin guardar',
            'El código tiene cambios sin guardar. ¿Desea descartarlos?'
        )

    def abrir(self):
        if not self.descartar_cambios():
            return
        ruta = filedialog.askopenfilename(
            title='Abrir archivo Swift', initialdir=CARPETA_ALGORITMOS,
            filetypes=[('Código Swift', '*.swift'),
                       ('Todos los archivos', '*.*')]
        )
        if ruta:
            self.cargar_archivo(ruta)

    def cargar_archivo(self, ruta):
        try:
            with open(ruta, encoding='utf-8', newline='') as archivo:
                codigo = archivo.read()
        except (OSError, UnicodeDecodeError) as error:
            messagebox.showerror(
                'Abrir archivo', f'No se pudo abrir el archivo:\n{error}')
            return

        # Se recuerda el fin de línea del archivo para guardarlo igual.
        self.salto_linea = '\r\n' if '\r\n' in codigo else '\n'
        self.ruta = ruta
        self.poner_codigo(codigo.replace('\r\n', '\n'))

    def guardar(self):
        if self.ruta is None:
            ruta = filedialog.asksaveasfilename(
                title='Guardar archivo Swift', initialdir=CARPETA_ALGORITMOS,
                defaultextension='.swift',
                filetypes=[('Código Swift', '*.swift')]
            )
            if not ruta:
                return
            self.ruta = ruta

        try:
            with open(self.ruta, 'w', encoding='utf-8',
                      newline=self.salto_linea) as archivo:
                archivo.write(self.editor.get('1.0', 'end-1c'))
        except OSError as error:
            messagebox.showerror(
                'Guardar archivo', f'No se pudo guardar el archivo:\n{error}')
            return

        self.hay_cambios = False
        self.actualizar_nombre()

    def limpiar(self):
        if not self.descartar_cambios():
            return
        self.ruta = None
        self.salto_linea = '\n'
        self.poner_codigo('')

    def cerrar(self):
        if self.descartar_cambios():
            self.destroy()

    # Nombre del archivo como queda escrito en el log.
    def nombre_para_log(self):
        if self.ruta is None:
            return 'código escrito en la interfaz (sin guardar)'

        nombre = self.ruta
        try:
            relativa = os.path.relpath(self.ruta, CARPETA_PROYECTO)
            if not relativa.startswith('..'):
                nombre = relativa
        except ValueError:
            pass   # el archivo está en otra unidad de disco

        nombre = nombre.replace('\\', '/')
        if self.hay_cambios:
            nombre += ' (con cambios sin guardar)'
        return nombre

    # ------------------------------ Análisis ------------------------------
    # 'hasta' es la última fase que se ejecuta. Con el análisis completo se
    # genera el log de las tres fases; con los demás botones, solo el de la
    # fase del botón.
    def analizar(self, hasta, completo=False):
        codigo = self.editor.get('1.0', 'end-1c')

        if not codigo.strip():
            messagebox.showinfo(
                'Analizador de Swift',
                'Escriba código o abra un archivo .swift antes de analizar.')
            return
        if self.generar_log.get() and not self.desarrollador.get():
            messagebox.showwarning(
                'Analizador de Swift',
                'Elija el desarrollador para nombrar el log de la prueba.')
            return

        try:
            resultado = analizar_codigo(codigo, hasta)
        except Exception as error:
            messagebox.showerror(
                'Analizador de Swift',
                f'El análisis se interrumpió por un error inesperado:\n{error}')
            return

        self.limpiar_resultados()
        self.mostrar_tokens(resultado['tokens'])
        self.mostrar_arbol(resultado['arbol'])
        self.mostrar_simbolos(resultado['simbolos'])
        self.mostrar_errores(resultado, hasta)
        self.mostrar_estado(resultado, hasta)
        self.escribir_logs(resultado, FASES if completo else (hasta,))

        # Se abre la pestaña de la fase del botón. Si esa fase no llegó a
        # ejecutarse, o si fue el análisis completo, se deja la de tokens.
        if completo or resultado[hasta] is None:
            self.pestanas.select(0)
        else:
            self.pestanas.select(FASES.index(hasta))

    def limpiar_resultados(self):
        for tabla in (self.tabla_tokens, self.arbol, self.tabla_simbolos,
                      self.tabla_errores):
            tabla.delete(*tabla.get_children())

        self.quitar_marcas_de_error()
        self.mostrar_log('')

        self.pestanas.tab(0, text='Tokens')
        self.titulo_errores.configure(text='Errores encontrados',
                                      fg='#1f2328')
        for fase in FASES:
            self.estado[fase].configure(text=f'{NOMBRES[fase]}: —')
        self.estado_log.configure(text='Log: —')

    def quitar_marcas_de_error(self):
        self.errores_por_linea = {}
        self.editor.tag_remove('linea_error', '1.0', 'end')
        self.editor.tag_remove('error_actual', '1.0', 'end')
        self.dibujar_margen()

    def mostrar_tokens(self, encontrados):
        for numero, (tipo, valor, linea, columna) in enumerate(encontrados, 1):
            self.tabla_tokens.insert(
                '', 'end', values=(numero, linea, columna, tipo, valor))
        self.pestanas.tab(0, text=f'Tokens ({len(encontrados)})')

    # Pasa el árbol del parser a la vista. Cada nodo del árbol es una tupla
    # que empieza con su nombre, y las sentencias llegan en listas de pares
    # (línea, sentencia).
    def insertar_nodo(self, padre, valor, linea=None):
        if isinstance(valor, tuple) and valor and isinstance(valor[0], str):
            if valor[0].startswith('tipo_'):
                self.arbol.insert(
                    padre, 'end',
                    text='tipo: ' + semantico_module.nombre_tipo(valor))
                return

            texto = valor[0]
            if linea is not None:
                texto += f'   (línea {linea})'
            nodo = self.arbol.insert(padre, 'end', text=texto)
            for hijo in valor[1:]:
                self.insertar_nodo(nodo, hijo)

        elif isinstance(valor, list):
            if not valor:
                return
            padre = self.arbol.insert(
                padre, 'end', text=f'lista ({len(valor)})')
            for elemento in valor:
                es_sentencia = (
                    isinstance(elemento, tuple) and len(elemento) == 2
                    and isinstance(elemento[0], int)
                    and isinstance(elemento[1], tuple)
                )
                if es_sentencia:
                    self.insertar_nodo(padre, elemento[1], elemento[0])
                else:
                    self.insertar_nodo(padre, elemento)

        elif valor is not None:
            self.arbol.insert(padre, 'end', text=str(valor))

    def mostrar_arbol(self, arbol):
        if arbol is None:
            return
        raiz = self.arbol.insert('', 'end', text=arbol[0], open=True)
        for linea, sentencia in arbol[1]:
            self.insertar_nodo(raiz, sentencia, linea)

    def abrir_nodos(self, abrir, nodo=''):
        for hijo in self.arbol.get_children(nodo):
            # La raíz siempre queda abierta para que se vean las sentencias.
            self.arbol.item(hijo, open=abrir or nodo == '')
            self.abrir_nodos(abrir, hijo)

    def mostrar_simbolos(self, simbolos):
        vistos = set()
        for nombre, tipo, categoria, linea, nivel in simbolos:
            # Las funciones globales se registran dos veces: antes de
            # recorrer el programa y al llegar a su declaración.
            if (nombre, linea, nivel) in vistos:
                continue
            vistos.add((nombre, linea, nivel))

            ambito = 'global' if nivel == 0 else f'local (nivel {nivel})'
            self.tabla_simbolos.insert('', 'end', values=(
                nombre, categoria, semantico_module.nombre_tipo(tipo),
                linea, ambito
            ))

    def mostrar_errores(self, resultado, hasta):
        total_lineas = int(self.editor.index('end-1c').split('.')[0])
        cantidad = 0

        for fase in FASES:
            for mensaje in resultado[fase] or []:
                linea, columna = ubicar_error(mensaje, total_lineas)
                self.tabla_errores.insert(
                    '', 'end', tags=(fase,),
                    values=(fase, linea, columna or '—', mensaje))
                self.errores_por_linea.setdefault(linea, COLORES[fase])
                self.editor.tag_add('linea_error', f'{linea}.0',
                                    f'{linea + 1}.0')
                cantidad += 1

        if cantidad == 0:
            self.titulo_errores.configure(
                text='Sin errores en las fases ejecutadas', fg='#18794e')
        else:
            titulo = f'Errores encontrados ({cantidad})'
            if hasta == SEMANTICO and resultado[SEMANTICO] is None:
                titulo += ('  ·  El análisis semántico no se ejecutó: '
                           'corrija primero estos errores.')
            self.titulo_errores.configure(text=titulo, fg='#b42318')

        self.dibujar_margen()

    # Al elegir un error, el cursor va a su línea y la línea queda subrayada.
    def ir_al_error(self, evento=None):
        seleccion = self.tabla_errores.selection()
        if not seleccion:
            return

        linea = int(self.tabla_errores.set(seleccion[0], 'linea'))
        columna = str(self.tabla_errores.set(seleccion[0], 'columna'))
        columna = int(columna) - 1 if columna.isdigit() else 0

        # El subrayado empieza en el primer carácter que no es espacio.
        texto = self.editor.get(f'{linea}.0', f'{linea}.end')
        sangria = len(texto) - len(texto.lstrip())

        self.editor.tag_remove('error_actual', '1.0', 'end')
        self.editor.tag_add('error_actual', f'{linea}.{sangria}',
                            f'{linea}.end')
        self.editor.mark_set('insert', f'{linea}.{columna}')
        self.editor.see(f'{linea}.0')
        self.editor.focus_set()
        self.actualizar_cursor()

    def mostrar_estado(self, resultado, hasta):
        self.estado[LEXICO].configure(
            text=f"Léxico: {cuantos(len(resultado['tokens']), 'token', 'tokens')}, "
                 f"{cuantos(len(resultado[LEXICO]), 'error', 'errores')}")

        if resultado[SINTACTICO] is not None:
            self.estado[SINTACTICO].configure(
                text="Sintáctico: "
                     + cuantos(len(resultado[SINTACTICO]), 'error', 'errores'))

        if resultado[SEMANTICO] is not None:
            self.estado[SEMANTICO].configure(
                text="Semántico: "
                     + cuantos(len(resultado[SEMANTICO]), 'error', 'errores'))
        elif hasta == SEMANTICO:
            self.estado[SEMANTICO].configure(
                text='Semántico: no ejecutado (hay errores previos)')

    # ------------------------------- Logs ---------------------------------
    def escribir_logs(self, resultado, fases):
        if not self.generar_log.get():
            self.mostrar_log('No se generó el log de esta prueba: la opción '
                             '"Generar log" está desactivada.')
            self.estado_log.configure(text='Log: no generado')
            return

        nombre, usuario_git = DESARROLLADORES[self.desarrollador.get()]
        archivo = self.nombre_para_log()
        rutas = []

        if LEXICO in fases:
            rutas.append(lexer_module.escribir_log(
                nombre, archivo, resultado['tokens'], resultado[LEXICO]))

        if SINTACTICO in fases:
            rutas.append(parser_module.escribir_log_sintactico(
                usuario_git, archivo, resultado[SINTACTICO]))

        if SEMANTICO in fases:
            errores_previos = (
                len(resultado[LEXICO]) + len(resultado[SINTACTICO])
            )
            rutas.append(semantico_module.escribir_log_semantico(
                usuario_git, archivo, resultado[SEMANTICO] or [],
                errores_previos))

        partes = []
        for ruta in rutas:
            with open(ruta, encoding='utf-8') as archivo_log:
                partes.append(f'===== logs/{os.path.basename(ruta)} =====\n'
                              + archivo_log.read())
        self.mostrar_log('\n'.join(partes))

        texto = 'Log: logs/' + os.path.basename(rutas[-1])
        if len(rutas) > 1:
            texto += f'  (y {len(rutas) - 1} más)'
        self.estado_log.configure(text=texto)

    def mostrar_log(self, texto):
        self.texto_log.configure(state='normal')
        self.texto_log.delete('1.0', 'end')
        self.texto_log.insert('1.0', texto)
        self.texto_log.configure(state='disabled')


if __name__ == '__main__':
    # En Windows evita que la ventana se vea borrosa cuando la pantalla
    # tiene una escala distinta de 100 %.
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    Interfaz().mainloop()
