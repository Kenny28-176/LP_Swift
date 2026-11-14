# Analizador semántico para un subconjunto de Swift
# Proyecto de Lenguajes de Programación 2026-II - ESPOL
# Integrantes: Kevin Morales, Kenny Chung, Miguel Medina
#
# Uso:
#   python semantico.py <archivo.swift> <usuarioGit>
#   python semantico.py algoritmos/algoritmo_KennyChung.swift Kenny28-176
#
# Recorre el árbol sintáctico que arma parser.py, lleva una tabla de símbolos
# por ámbitos y aplica las reglas semánticas de cada integrante.
# Cada ejecución genera un log en logs/semantico-usuarioGit-ddmmaaaa-HHhMM.txt
# con los errores semánticos encontrados.

import os
import sys
from datetime import datetime

import ply.lex as lex

import lexer as lexer_module
import parser as parser_module


# ---------------------------------------------------------------------------
# Tabla de símbolos
# ---------------------------------------------------------------------------
class TablaSimbolos:
    # Pila de ámbitos: el primero es el global y cada bloque { } agrega otro.
    # De cada identificador se guarda su tipo, su categoría (variable,
    # constante o funcion) y la línea donde se declaró.
    def __init__(self):
        self.ambitos = [{}]

    def abrir_ambito(self):
        self.ambitos.append({})

    def cerrar_ambito(self):
        self.ambitos.pop()

    def declarar(self, nombre, tipo, categoria, linea):
        self.ambitos[-1][nombre] = {
            'tipo': tipo,
            'categoria': categoria,
            'linea': linea,
        }

    # Busca desde el ámbito más interno hacia el global.
    def buscar(self, nombre):
        for ambito in reversed(self.ambitos):
            if nombre in ambito:
                return ambito[nombre]
        return None


tabla = TablaSimbolos()
errores_semanticos = []

# Funciones o closures que se están recorriendo: (nombre, tipo de retorno).
# El nombre es None cuando se trata de un closure.
funciones_abiertas = []


def reportar(linea, descripcion):
    errores_semanticos.append(
        f"Error semántico: {descripcion} (línea {linea})."
    )


# ---------------------------------------------------------------------------
# Tipos
# ---------------------------------------------------------------------------
# Un tipo se representa igual que en el árbol: 'Int', 'Double', 'String',
# 'Bool', 'Character' o un nodo como ('tipo_tupla', ['Double', 'Bool']).
# None significa que el tipo no se pudo determinar; en ese caso no se reporta
# nada, para no encadenar errores falsos. Los opcionales no se modelan:
# readLine() y el acceso a un diccionario se tratan con su tipo base.

def es_nodo(valor, etiqueta):
    return isinstance(valor, tuple) and valor[0] == etiqueta


# Escribe un tipo como en Swift: Int, (Double, Bool), [Int], [String: Double].
def nombre_tipo(tipo):
    if tipo is None:
        return 'desconocido'
    if isinstance(tipo, str):
        return tipo
    if tipo[0] == 'tipo_tupla':
        return '(' + ', '.join(nombre_tipo(t) for t in tipo[1]) + ')'
    if tipo[0] == 'tipo_arreglo':
        return '[' + nombre_tipo(tipo[1]) + ']'
    if tipo[0] == 'tipo_diccionario':
        return '[' + nombre_tipo(tipo[1]) + ': ' + nombre_tipo(tipo[2]) + ']'
    parametros = ', '.join(nombre_tipo(t) for t in tipo[1])
    return '(' + parametros + ') -> ' + nombre_tipo(tipo[2])


def tipos_compatibles(esperado, encontrado):
    if esperado is None or encontrado is None:
        return True
    if isinstance(esperado, (tuple, list)) and isinstance(encontrado, (tuple, list)):
        return len(esperado) == len(encontrado) and all(
            tipos_compatibles(a, b) for a, b in zip(esperado, encontrado)
        )
    return esperado == encontrado


# Indica si un valor se puede usar donde se espera tipo_esperado.
def valor_compatible(tipo_esperado, valor, tipo_valor):
    if es_nodo(tipo_esperado, 'tipo_tupla') and es_nodo(valor, 'tupla_literal'):
        esperados = tipo_esperado[1]
        elementos = valor[1]
        return len(esperados) == len(elementos) and all(
            valor_compatible(esperado, elemento, tipo)
            for esperado, elemento, tipo in zip(esperados, elementos, tipo_valor[1])
        )

    # Un literal entero también sirve como Double y una cadena de un solo
    # carácter como Character.
    if tipo_esperado == 'Double' and isinstance(valor, int):
        return True
    if (tipo_esperado == 'Character' and isinstance(valor, str)
            and valor.startswith('"') and len(valor) == 3):
        return True

    return tipos_compatibles(tipo_esperado, tipo_valor)


# ===================== Inicio aporte: Kevin Morales =====================
# Pendiente. Reglas asignadas:
#   1. Los operandos de +, -, * y / deben ser del mismo tipo.
#   2. Todo identificador debe estar declarado antes de usarse.
# ====================== Fin aporte: Kevin Morales =======================


# ====================== Inicio aporte: Kenny Chung ======================

# Regla 1: una constante declarada con let no se puede modificar.
# Se revisa en cada asignación (=, +=, -=, *=, /=), incluidas las que usan
# subíndice. En Swift los parámetros de una función y la variable de un
# for-in también son constantes, por eso se registran con esa categoría.
#   let maximo: Int = 10
#   maximo = 20            <- error
def regla_constante_no_modificable(nombre, linea):
    simbolo = tabla.buscar(nombre)

    if simbolo is not None and simbolo['categoria'] == 'constante':
        reportar(
            linea,
            f"'{nombre}' es una constante (let) y no se puede modificar"
        )


# Regla 2: el valor de cada return debe ser del tipo declarado después de ->.
# Se compara con la función (o closure) más interna que contiene al return.
# Un return sin valor también es un error si la función declara un tipo.
#   func doble(n: Int) -> Int {
#       return "veinte"    <- error
#   }
def regla_tipo_retorno(valor, tipo_valor, linea):
    if not funciones_abiertas:
        return

    nombre, tipo_declarado = funciones_abiertas[-1]

    # Closure que no declara su tipo de retorno.
    if tipo_declarado is None:
        return

    if nombre is None:
        funcion = "el closure"
    else:
        funcion = f"la función '{nombre}'"

    if valor is None:
        reportar(
            linea,
            f"{funcion} debe retornar {nombre_tipo(tipo_declarado)}, "
            f"pero el return no devuelve ningún valor"
        )
    elif not valor_compatible(tipo_declarado, valor, tipo_valor):
        reportar(
            linea,
            f"{funcion} debe retornar {nombre_tipo(tipo_declarado)}, "
            f"pero retorna {nombre_tipo(tipo_valor)}"
        )
# ======================= Fin aporte: Kenny Chung ========================


# ===================== Inicio aporte: Miguel Medina =====================
# Pendiente. Reglas asignadas:
#   1. La condición de if / else if, while y repeat-while debe ser Bool.
#   2. Las claves y los valores de un diccionario deben coincidir con su
#      tipo declarado [K: V].
# ====================== Fin aporte: Miguel Medina =======================


# ---------------------------------------------------------------------------
# Tipo de las expresiones
# ---------------------------------------------------------------------------
OPERADORES_ARITMETICOS = ('+', '-', '*', '/', '%')

# Nodos de expresión con dos elementos. Sirven para no confundirlos con un
# argumento etiquetado, que el parser entrega como (etiqueta, expresion).
LITERALES_COMPUESTOS = ('arreglo_literal', 'diccionario_literal', 'tupla_literal')


def tipo_identificador(nombre):
    simbolo = tabla.buscar(nombre)
    return simbolo['tipo'] if simbolo is not None else None


def tipo_expresion(expresion, linea):
    # Los literales y los identificadores llegan como valores de Python.
    if isinstance(expresion, int):
        return 'Int'
    if isinstance(expresion, float):
        return 'Double'
    if isinstance(expresion, str):
        if expresion.startswith('"'):
            return 'String'
        if expresion in ('true', 'false'):
            return 'Bool'
        if expresion == 'nil':
            return None
        return tipo_identificador(expresion)

    etiqueta = expresion[0]

    if etiqueta == 'expresion_binaria':
        _, operador, izquierda, derecha = expresion
        tipo_izquierdo = tipo_expresion(izquierda, linea)
        tipo_derecho = tipo_expresion(derecha, linea)

        if operador in OPERADORES_ARITMETICOS:
            if tipo_izquierdo is None:
                return tipo_derecho
            if tipo_derecho is None or tipo_izquierdo == tipo_derecho:
                return tipo_izquierdo
            return None

        if operador == '??':
            return tipo_derecho if tipo_derecho is not None else tipo_izquierdo

        # Comparaciones y operadores lógicos.
        return 'Bool'

    if etiqueta == 'expresion_unaria':
        tipo = tipo_expresion(expresion[2], linea)
        return 'Bool' if expresion[1] == '!' else tipo

    if etiqueta == 'llamada_funcion':
        _, nombre, argumentos = expresion
        for argumento in argumentos:
            if (isinstance(argumento, tuple) and len(argumento) == 2
                    and argumento[0] not in LITERALES_COMPUESTOS):
                argumento = argumento[1]
            tipo_expresion(argumento, linea)

        tipo = tipo_identificador(nombre)
        return tipo[2] if es_nodo(tipo, 'tipo_funcion') else None

    if etiqueta == 'tupla_literal':
        return ('tipo_tupla', [tipo_expresion(e, linea) for e in expresion[1]])

    if etiqueta == 'acceso_tupla':
        _, nombre, indice = expresion
        tipo = tipo_identificador(nombre)
        if es_nodo(tipo, 'tipo_tupla') and indice < len(tipo[1]):
            return tipo[1][indice]
        return None

    if etiqueta == 'arreglo_literal':
        tipos = [tipo_expresion(e, linea) for e in expresion[1]]
        return ('tipo_arreglo', tipos[0])

    if etiqueta == 'arreglo_vacio':
        return ('tipo_arreglo', None)

    if etiqueta == 'diccionario_literal':
        tipos = [
            (tipo_expresion(clave, linea), tipo_expresion(valor, linea))
            for _, clave, valor in expresion[1]
        ]
        return ('tipo_diccionario', tipos[0][0], tipos[0][1])

    if etiqueta == 'diccionario_vacio':
        return ('tipo_diccionario', None, None)

    if etiqueta == 'acceso_subindice':
        _, nombre, indice = expresion
        tipo = tipo_identificador(nombre)
        tipo_expresion(indice, linea)
        if es_nodo(tipo, 'tipo_arreglo'):
            return tipo[1]
        if es_nodo(tipo, 'tipo_diccionario'):
            return tipo[2]
        return None

    if etiqueta == 'lectura_teclado':
        return 'String'

    if etiqueta == 'closure':
        _, firma, cuerpo = expresion
        parametros = firma[1] if firma is not None else []
        tipo_retorno = firma[2] if firma is not None else None
        analizar_funcion(None, parametros, tipo_retorno, cuerpo, linea)
        return ('tipo_funcion', [p[1] for p in parametros], tipo_retorno)

    return None


# ---------------------------------------------------------------------------
# Recorrido de las sentencias
# ---------------------------------------------------------------------------
# Cada lista de sentencias llega del parser como pares (línea, sentencia).

def analizar_sentencias(sentencias):
    for linea, sentencia in sentencias:
        analizar_sentencia(sentencia, linea)


# Un bloque { } tiene su propio ámbito.
def analizar_bloque(sentencias):
    tabla.abrir_ambito()
    analizar_sentencias(sentencias)
    tabla.cerrar_ambito()


def declarar_funcion(sentencia, linea):
    _, nombre, parametros, tipo_retorno, _ = sentencia
    tipo = ('tipo_funcion', [p[1] for p in parametros], tipo_retorno)
    tabla.declarar(nombre, tipo, 'funcion', linea)


# Recorre el cuerpo de una función o closure con sus parámetros declarados.
# Cada parámetro llega como (nombre, tipo) o (nombre, tipo, valor por defecto).
def analizar_funcion(nombre, parametros, tipo_retorno, cuerpo, linea):
    tabla.abrir_ambito()

    for parametro in parametros:
        if len(parametro) == 3:
            tipo_expresion(parametro[2], linea)
        tabla.declarar(parametro[0], parametro[1], 'constante', linea)

    funciones_abiertas.append((nombre, tipo_retorno))
    analizar_sentencias(cuerpo)
    funciones_abiertas.pop()

    tabla.cerrar_ambito()


def analizar_if(sentencia, linea):
    _, condicion, cuerpo, bloque_else = sentencia
    tipo_expresion(condicion, linea)
    analizar_bloque(cuerpo)

    if bloque_else is None:
        return
    if bloque_else[0] == 'else_if':
        analizar_if(bloque_else[1], linea)
    else:
        analizar_bloque(bloque_else[1])


def analizar_sentencia(sentencia, linea):
    etiqueta = sentencia[0]

    if etiqueta in ('declaracion_var_explicita', 'declaracion_let_explicita'):
        _, nombre, tipo, valor = sentencia
        tipo_expresion(valor, linea)

        if etiqueta == 'declaracion_let_explicita':
            tabla.declarar(nombre, tipo, 'constante', linea)
        else:
            tabla.declarar(nombre, tipo, 'variable', linea)

    elif etiqueta == 'declaracion_inferida':
        _, palabra, nombre, valor = sentencia
        tipo = tipo_expresion(valor, linea)
        categoria = 'constante' if palabra == 'let' else 'variable'
        tabla.declarar(nombre, tipo, categoria, linea)

    elif etiqueta == 'reasignacion':
        _, nombre, _, valor = sentencia
        regla_constante_no_modificable(nombre, linea)
        tipo_expresion(valor, linea)

    elif etiqueta == 'reasignacion_subindice':
        _, nombre, indice, _, valor = sentencia
        regla_constante_no_modificable(nombre, linea)
        tipo_expresion(indice, linea)
        tipo_expresion(valor, linea)

    elif etiqueta == 'impresion':
        for expresion in sentencia[1]:
            tipo_expresion(expresion, linea)

    elif etiqueta == 'sentencia_llamada':
        tipo_expresion(sentencia[1], linea)

    elif etiqueta == 'declaracion_funcion':
        _, nombre, parametros, tipo_retorno, cuerpo = sentencia
        declarar_funcion(sentencia, linea)
        analizar_funcion(nombre, parametros, tipo_retorno, cuerpo, linea)

    elif etiqueta == 'retorno':
        valor = sentencia[1]
        regla_tipo_retorno(valor, tipo_expresion(valor, linea), linea)

    elif etiqueta == 'retorno_vacio':
        regla_tipo_retorno(None, None, linea)

    elif etiqueta == 'if':
        analizar_if(sentencia, linea)

    elif etiqueta == 'bucle_while':
        _, condicion, cuerpo = sentencia
        tipo_expresion(condicion, linea)
        analizar_bloque(cuerpo)

    elif etiqueta == 'bucle_repeat_while':
        # La condición va después del bloque y no ve lo declarado dentro de él.
        _, condicion, cuerpo = sentencia
        analizar_bloque(cuerpo)
        tipo_expresion(condicion, linea)

    elif etiqueta == 'bucle_for':
        _, variable, rango, cuerpo = sentencia

        if rango[0] == 'rango':
            tipo_expresion(rango[2], linea)
            tipo_expresion(rango[3], linea)
            tipo_variable = 'Int'
        else:
            tipo_coleccion = tipo_expresion(rango[1], linea)
            if es_nodo(tipo_coleccion, 'tipo_arreglo'):
                tipo_variable = tipo_coleccion[1]
            else:
                tipo_variable = None

        tabla.abrir_ambito()
        tabla.declarar(variable, tipo_variable, 'constante', linea)
        analizar_sentencias(cuerpo)
        tabla.cerrar_ambito()

    elif etiqueta == 'switch':
        _, valor, casos, caso_default = sentencia
        tipo_expresion(valor, linea)

        for _, valores, cuerpo in casos:
            for expresion in valores:
                tipo_expresion(expresion, linea)
            analizar_bloque(cuerpo)

        if caso_default is not None:
            analizar_bloque(caso_default[1])

    # break, continue, print() vacío y las sentencias que quedaron con un
    # error sintáctico no necesitan revisión semántica.


# Punto de entrada: recibe el árbol ('programa', sentencias) y devuelve la
# lista de errores semánticos.
def analizar(arbol):
    tabla.ambitos = [{}]
    errores_semanticos.clear()
    funciones_abiertas.clear()

    sentencias = arbol[1]

    # Las funciones globales se pueden llamar antes de la línea donde se
    # declaran, así que se registran primero.
    for linea, sentencia in sentencias:
        if sentencia[0] == 'declaracion_funcion':
            declarar_funcion(sentencia, linea)

    analizar_sentencias(sentencias)
    return errores_semanticos


# ---------------------------------------------------------------------------
# Generación del log semántico
# ---------------------------------------------------------------------------
def escribir_log_semantico(usuario_git, archivo, errores, errores_previos):
    ahora = datetime.now()

    os.makedirs(lexer_module.CARPETA_LOGS, exist_ok=True)

    nombre_log = f"semantico-{usuario_git}-{ahora:%d%m%Y-%Hh%M}.txt"
    ruta = os.path.join(lexer_module.CARPETA_LOGS, nombre_log)

    lineas = [
        "Análisis semántico de Swift",
        f"Desarrollador: {usuario_git}",
        f"Archivo: {archivo}",
        f"Fecha: {ahora:%d-%m-%Y %H:%M}",
        "",
    ]

    if errores_previos:
        lineas.append(
            "No se realizó el análisis semántico: el archivo tiene "
            f"{errores_previos} errores léxicos o sintácticos."
        )
    else:
        lineas.append(f"ERRORES SEMÁNTICOS ({len(errores)})")
        lineas += errores or ["Ninguno. No se encontraron errores semánticos."]

    with open(ruta, 'w', encoding='utf-8') as archivo_log:
        archivo_log.write('\n'.join(lineas) + '\n')

    return ruta


# ---------------------------------------------------------------------------
# Ejecución principal
# ---------------------------------------------------------------------------
if __name__ == '__main__':

    if len(sys.argv) != 3:
        print("Uso: python semantico.py <archivo.swift> <usuarioGit>")
        sys.exit(1)

    archivo = sys.argv[1]
    usuario_git = ''.join(sys.argv[2].split())

    try:
        with open(archivo, encoding='utf-8') as archivo_swift:
            codigo = archivo_swift.read()

    except FileNotFoundError:
        print(f"Error: no se encontró el archivo '{archivo}'.")
        sys.exit(1)

    print(f"\nAnalizando archivo: {archivo}")

    # El análisis semántico parte del árbol del analizador sintáctico.
    parser_module.codigo_actual = codigo
    parser_module.errores_sintacticos.clear()

    lexer_base = lex.lex(module=lexer_module)
    lexer_base.errores = []

    arbol = parser_module.parser.parse(
        codigo,
        lexer=parser_module.LexerConSeparadores(lexer_base),
        tracking=True
    )

    errores_previos = (
        len(lexer_base.errores) + len(parser_module.errores_sintacticos)
    )

    if errores_previos:
        errores = []
        print(
            f"\nEl archivo tiene {errores_previos} errores léxicos o "
            "sintácticos. Corríjalos antes del análisis semántico."
        )
    else:
        print("\nIniciando análisis semántico...")
        errores = analizar(arbol)
        print("Análisis semántico completado.")
        print(f"Errores semánticos: {len(errores)}")

    ruta_log = escribir_log_semantico(
        usuario_git, archivo, errores, errores_previos
    )
    print(f"Log semántico generado: {os.path.relpath(ruta_log)}")

    if not errores_previos:
        if errores:
            print("\nEl archivo contiene errores semánticos.")
        else:
            print("\nEl archivo cumple las reglas semánticas implementadas.")
