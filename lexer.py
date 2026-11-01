# Analizador léxico para un subconjunto de Swift (PLY - ply.lex)
# Proyecto de Lenguajes de Programación 2026-II - ESPOL
# Integrantes: Kevin Morales, Kenny Chung, Miguel Medina
#
# Uso:
#   python lexer.py <archivo.swift> <NombreApellido>
#   python lexer.py algoritmos/algoritmo_KennyChung.swift KennyChung
#
# Cada ejecución genera un log en logs/lexico-NombreApellido-dd-mm-aaaa-HHhMM.txt
# con los tokens reconocidos y los errores léxicos.

import os
import sys
from datetime import datetime

import ply.lex as lex

CARPETA_LOGS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')

# ---------------------------------------------------------------------------
# Base común
# ---------------------------------------------------------------------------

# Palabras reservadas (lexema -> token). Cada integrante agrega las suyas.
# La regla de identificadores consulta este diccionario para que, por
# ejemplo, 'let' se reconozca como LET y no como un nombre de variable.
reserved = {}

# Tokens que no son palabras reservadas. Cada integrante agrega los suyos.
tokens = []

# ===================== Inicio aporte: Kevin Morales =====================
# Pendiente. Tokens asignados: var, for, in, ..., ..<, [ ]
# ====================== Fin aporte: Kevin Morales =======================

# ====================== Inicio aporte: Kenny Chung ======================
reserved.update({
    'let': 'LET',          # constante: let pi: Double = 3.1416
    'repeat': 'REPEAT',    # repeat { ... } while condicion
    'while': 'WHILE',
    'func': 'FUNC',
    'return': 'RETURN',
})

tokens += [
    'ARROW',    # ->  separa los parámetros del tipo de retorno
    'LPAREN',   # (
    'RPAREN',   # )
    'COMMA',    # ,
    'COLON',    # :   anotación de tipo, etiqueta de argumento, clave: valor
    'DOT',      # .   acceso a los elementos de una tupla: punto.0
]

t_ARROW = r'->'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_COMMA = r','
t_COLON = r':'
t_DOT = r'\.'
# ======================= Fin aporte: Kenny Chung ========================

# ===================== Inicio aporte: Miguel Medina =====================
reserved.update({
    'if': 'IF',
    'else': 'ELSE',
    'true': 'TRUE',
    'false': 'FALSE',
    'nil': 'NIL',
    'print': 'PRINT',
    'readLine': 'READLINE',
    'Int': 'TIPO',          # los tipos de dato comparten un mismo token
    'Double': 'TIPO',
    'String': 'TIPO',
    'Bool': 'TIPO',
    'Character': 'TIPO',
    'switch': 'SWITCH',
    'case': 'CASE',
    'default': 'DEFAULT',
    'break': 'BREAK',
    'continue': 'CONTINUE',
})

tokens += [
    'ID',
    # Literales
    'INT',
    'DOUBLE',
    'STRING',
    # Aritméticos
    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDE',
    'MOD',
    # Asignación
    'ASSIGN',
    'PLUS_ASSIGN',
    'MINUS_ASSIGN',
    'TIMES_ASSIGN',
    'DIVIDE_ASSIGN',
    # Comparación
    'EQ',
    'NE',
    'LT',
    'GT',
    'LE',
    'GE',
    # Lógicos
    'AND',
    'OR',
    'NOT',
    # Coalescencia de nil
    'NIL_COALESCING',
    # Delimitadores
    'LBRACE',
    'RBRACE',
    'SEMICOLON',
]

# Operadores y delimitadores. PLY ordena las reglas de cadena de mayor a
# menor longitud, así '==' se prueba antes que '=' y '+=' antes que '+'.
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_MOD = r'%'

t_ASSIGN = r'='
t_PLUS_ASSIGN = r'\+='
t_MINUS_ASSIGN = r'-='
t_TIMES_ASSIGN = r'\*='
t_DIVIDE_ASSIGN = r'/='

t_EQ = r'=='
t_NE = r'!='
t_LT = r'<'
t_GT = r'>'
t_LE = r'<='
t_GE = r'>='

t_AND = r'&&'
t_OR = r'\|\|'
t_NOT = r'!'

t_NIL_COALESCING = r'\?\?'

t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_SEMICOLON = r';'


# Los comentarios son funciones para que se evalúen antes que DIVIDE.
# No retornan nada, así que se descartan.
def t_COMMENT_MULTILINE(t):
    r'/\*(.|\n)*?\*/'
    t.lexer.lineno += t.value.count('\n')


def t_COMMENT(t):
    r'//.*'


def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'ID')
    return t


# DOUBLE va antes que INT; si no, '3.14' se partiría en INT DOT INT.
def t_DOUBLE(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t


def t_INT(t):
    r'\d+'
    t.value = int(t.value)
    return t


def t_STRING(t):
    r'"([^"\n]|\\.)*"'
    return t
# ====================== Fin aporte: Miguel Medina =======================

# ---------------------------------------------------------------------------
# Base común (continuación)
# ---------------------------------------------------------------------------

tokens += sorted(set(reserved.values()))

t_ignore = ' \t\r'  # \r: fin de línea de Windows (\r\n)


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


def t_error(t):
    columna = find_column(t.lexer.lexdata, t.lexpos)
    t.lexer.errores.append(
        f"Error léxico: carácter no reconocido '{t.value[0]}' "
        f"en la línea {t.lineno}, columna {columna}."
    )
    t.lexer.skip(1)


def find_column(data, lexpos):
    inicio_linea = data.rfind('\n', 0, lexpos) + 1
    return lexpos - inicio_linea + 1


def analizar(codigo):
    """Devuelve los tokens (tipo, lexema, línea, columna) y los errores léxicos."""
    lexer = lex.lex()
    lexer.errores = []
    lexer.input(codigo)
    encontrados = [
        (tok.type, tok.value, tok.lineno, find_column(codigo, tok.lexpos))
        for tok in lexer
    ]
    return encontrados, lexer.errores


def escribir_log(nombre, archivo, encontrados, errores):
    ahora = datetime.now()
    os.makedirs(CARPETA_LOGS, exist_ok=True)
    ruta = os.path.join(CARPETA_LOGS, f"lexico-{nombre}-{ahora:%d-%m-%Y-%Hh%M}.txt")

    lineas = [
        "Análisis léxico de Swift (PLY)",
        f"Desarrollador: {nombre}",
        f"Archivo: {archivo}",
        f"Fecha: {ahora:%d-%m-%Y %H:%M}",
        "",
        f"TOKENS RECONOCIDOS ({len(encontrados)})",
        f"{'#':>4}  {'Línea':>5}  {'Columna':>7}  {'Token':<16}  Lexema",
    ]
    for i, (tipo, valor, linea, columna) in enumerate(encontrados, 1):
        lineas.append(f"{i:>4}  {linea:>5}  {columna:>7}  {tipo:<16}  {valor}")

    lineas += ["", f"ERRORES LÉXICOS ({len(errores)})"]
    lineas += errores or ["Ninguno."]

    with open(ruta, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lineas) + '\n')
    return ruta


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Uso: python lexer.py <archivo.swift> <NombreApellido>")
        sys.exit(1)

    archivo = sys.argv[1]
    nombre = ''.join(sys.argv[2].split())  # "Kenny Chung" -> "KennyChung"

    with open(archivo, encoding='utf-8') as f:
        codigo = f.read()

    encontrados, errores = analizar(codigo)
    ruta = escribir_log(nombre, archivo, encontrados, errores)
    print(f"{len(encontrados)} tokens reconocidos, {len(errores)} errores léxicos.")
    print(f"Log generado: {os.path.relpath(ruta)}")
