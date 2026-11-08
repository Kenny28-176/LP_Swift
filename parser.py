# Analizador sintáctico para un subconjunto de Swift (PLY - ply.yacc)
# Proyecto de Lenguajes de Programación 2026-II - ESPOL
# Integrantes: Kevin Morales, Kenny Chung, Miguel Medina
#
# Uso:
#   python parser.py <archivo.swift> <usuarioGit>
#   python parser.py algoritmos/algoritmo_KevinMorales.swift kevin-moralesc
#
# Cada ejecución genera un único log en la carpeta logs/:
#   - sintactico: errores sintácticos encontrados.
# El análisis léxico se realiza internamente utilizando lexer.py,
# pero no genera un log léxico desde este archivo.

import os
import sys
from datetime import datetime

import ply.lex as lex
import ply.yacc as yacc

import lexer as lexer_module

tokens = lexer_module.tokens


# ---------------------------------------------------------------------------
# Precedencia y asociatividad de operadores
# ---------------------------------------------------------------------------

precedence = (
    ('right', 'ASSIGN', 'PLUS_ASSIGN', 'MINUS_ASSIGN',
     'TIMES_ASSIGN', 'DIVIDE_ASSIGN'),
    ('left', 'OR'),
    ('left', 'AND'),
    ('nonassoc', 'EQ', 'NE', 'LT', 'GT', 'LE', 'GE'),
    ('right', 'NIL_COALESCING'),
    ('nonassoc', 'CLOSED_RANGE', 'HALF_OPEN_RANGE'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'MOD'),
    ('right', 'UMINUS', 'NOT'),
)

# ---------------------------------------------------------------------------
# Reglas gramaticales generales
# ---------------------------------------------------------------------------
def p_programa(p):
    '''programa : lista_sentencias_opt'''
    p[0] = ('programa', p[1])

def p_lista_sentencias_opt(p):
    '''lista_sentencias_opt : lista_sentencias
                            | vacio'''
    p[0] = p[1]

def p_lista_sentencias(p):
    '''lista_sentencias : lista_sentencias sentencia
                        | lista_sentencias SEMICOLON
                        | sentencia
                        | SEMICOLON'''
    if len(p) == 3:
        if p.slice[2].type == 'SEMICOLON':
            p[0] = p[1]
        else:
            p[0] = p[1] + [p[2]]
    elif p.slice[1].type == 'SEMICOLON':
        p[0] = []
    else:
        p[0] = [p[1]]

def p_vacio(p):
    '''vacio :'''
    p[0] = []

# ===================== Inicio aporte: Kevin Morales ====================
def p_sentencia_var_explicita(p):
    '''sentencia : VAR ID COLON tipo ASSIGN expresion'''
    p[0] = ('declaracion_var_explicita', p[2], p[4], p[6])

def p_bucle_for_in(p):
    '''sentencia : FOR ID IN rango LBRACE lista_sentencias_opt RBRACE'''
    p[0] = ('bucle_for', p[2], p[4], p[6])

def p_rango(p):
    '''rango : expresion CLOSED_RANGE expresion
             | expresion HALF_OPEN_RANGE expresion
             | expresion'''
    if len(p) == 4:
        p[0] = ('rango', p[2], p[1], p[3])
    else:
        p[0] = ('coleccion_o_rango', p[1])

def p_funcion_multiple_parametros(p):
    '''sentencia : FUNC ID LPAREN parametros_opt RPAREN ARROW tipo LBRACE lista_sentencias_opt RBRACE'''
    p[0] = ('declaracion_funcion', p[2], p[4], p[7], p[9])

def p_arreglo_tipo_y_literal(p):
    '''tipo : LBRACKET tipo RBRACKET'''
    p[0] = ('tipo_arreglo', p[2])

def p_arreglo_literal(p):
    '''expresion : LBRACKET elementos_corchetes RBRACKET'''
    elementos = p[2]

    if all(not (isinstance(elemento, tuple)
                and elemento[0] == 'par_diccionario')
           for elemento in elementos):
        p[0] = ('arreglo_literal', elementos)
    else:
        p[0] = ('diccionario_literal', elementos)

def p_arreglo_vacio(p):
    '''expresion : LBRACKET RBRACKET'''
    p[0] = ('arreglo_vacio',)

def p_acceso_arreglo(p):
    '''expresion : ID LBRACKET expresion RBRACKET'''
    p[0] = ('acceso_subindice', p[1], p[3])
# ====================== Fin aporte: Kevin Morales ======================

# ===================== Inicio aporte: Kenny Chung ======================

# ---------------------------------------------------------------------------
# 1. Estructura de datos: TUPLAS
# ---------------------------------------------------------------------------
# El tipo de una tupla, por ejemplo (String, Int, Bool), lo reconoce la regla
# común p_tipo. Aquí se agregan las reglas que faltaban para declararlas,
# crear sus valores y acceder a sus elementos.

# Constante con tipo explícito. Sirve para declarar tuplas con elementos de
# distintos tipos:
#   let curso: String = "Lenguajes de Programacion"
#   let alumno: (String, Int, Bool) = ("Ana", 20, true)
# (las reglas comunes cubren 'let' sin tipo y la de Kevin cubre 'var' con tipo)
def p_sentencia_let_explicita(p):
    '''sentencia : LET ID COLON tipo ASSIGN expresion'''
    p[0] = ('declaracion_let_explicita', p[2], p[4], p[6])

# Valor de una tupla: dos o más expresiones separadas por coma, entre paréntesis.
#   ("Ana", 20, true)        (nota, nota >= minimo)
# Una sola expresión entre paréntesis sigue siendo una expresión agrupada
# (p_expresion_parentesis).
def p_expresion_tupla(p):
    '''expresion : LPAREN expresion COMMA lista_expresiones RPAREN'''
    p[0] = ('tupla_literal', [p[2]] + p[4])

# Acceso a un elemento de la tupla mediante su índice:  alumno.0   alumno.1
def p_acceso_tupla(p):
    '''expresion : ID DOT INT'''
    p[0] = ('acceso_tupla', p[1], p[3])

# ---------------------------------------------------------------------------
# 2. Estructura de control: REPEAT-WHILE
# ---------------------------------------------------------------------------
# repeat { instrucciones } while condicion
# El bloque se ejecuta al menos una vez; la condición se escribe después de él.
def p_sentencia_repeat_while(p):
    '''sentencia : REPEAT LBRACE lista_sentencias_opt RBRACE WHILE expresion'''
    p[0] = ('bucle_repeat_while', p[6], p[3])

# ---------------------------------------------------------------------------
# 3. Tipo de función: FUNCIONES CON PARÁMETROS POR DEFECTO
# ---------------------------------------------------------------------------
# No necesita producciones nuevas: ya las cubren las reglas comunes, y
# duplicarlas haría fallar la construcción del parser.
#   - p_parametro (ID COLON tipo ASSIGN expresion) acepta el valor por defecto.
#   - p_funcion_multiple_parametros (Kevin) define func ... -> tipo { ... }.
#   - p_argumentos y p_argumento permiten llamar con o sin argumentos:
#       saludar()    saludar(nombre: alumno.0)    evaluar(nota: 6.0)
# Ejemplo: func saludar(nombre: String = "estudiante") -> String { ... }

# ====================== Fin aporte: Kenny Chung =======================

# ===================== Inicio aporte: Miguel Medina ====================

# -----------------------------------------------------------------------
# APORTE PENDIENTE: MIGUEL MEDINA
#
# Instrucciones:
# Implementar las reglas sintácticas correspondientes a las siguientes
# contribuciones, tomando como referencia el algoritmo de Miguel:
#
# 1. Estructura de datos: DICCIONARIOS.
#    (Reconocer declaraciones y literales de diccionarios, incluyendo
#    pares clave-valor y diccionarios vacíos).
#
# 2. Estructura de control: IF-ELSE.
#    (Reconocer condiciones if, bloques else y estructuras else-if).
#
# 3. Tipo de función: CLOSURES.
#    (Reconocer expresiones closure de Swift, respetando los parámetros,
#    el tipo de retorno y las instrucciones de su cuerpo).
#
# Importante:
# Las reglas generales que necesita el parser se encuentran
# fuera de esta sección. No deben eliminarse ni duplicarse.
#
# Miguel debe implementar sus reglas utilizando los tokens
# existentes en lexer.py, comentar cada producción y probar
# su algoritmo completo.
# ====================== Fin aporte: Miguel Medina ======================

# REGLAS GRAMATICALES GENERALES Y COMPARTIDAS
def p_sentencia_inferida(p):
    '''sentencia : VAR ID ASSIGN expresion
                 | LET ID ASSIGN expresion'''
    p[0] = ('declaracion_inferida', p[1], p[2], p[4])


def p_sentencia_reasignacion(p):
    '''sentencia : ID operador_asignacion expresion
                 | ID LBRACKET expresion RBRACKET operador_asignacion expresion'''
    if len(p) == 4:
        p[0] = ('reasignacion', p[1], p[2], p[3])
    else:
        p[0] = ('reasignacion_subindice', p[1], p[3], p[5], p[6])


def p_operador_asignacion(p):
    '''operador_asignacion : ASSIGN
                           | PLUS_ASSIGN
                           | MINUS_ASSIGN
                           | TIMES_ASSIGN
                           | DIVIDE_ASSIGN'''
    p[0] = p[1]

def p_elemento_arreglo(p):
    '''elemento_corchetes : expresion'''
    p[0] = p[1]


def p_elementos_corchetes(p):
    '''elementos_corchetes : elementos_corchetes COMMA elemento_corchetes
                           | elemento_corchetes'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]

def p_impresion(p):
    '''sentencia : PRINT LPAREN lista_expresiones RPAREN
                 | PRINT LPAREN RPAREN'''
    if len(p) == 5:
        p[0] = ('impresion', p[3])
    else:
        p[0] = ('impresion_vacia',)

# ---------------------------------------------------------------------------
# Reglas gramaticales auxiliares comunes
# ---------------------------------------------------------------------------
# Tipos primitivos, arreglos, diccionarios y tuplas.
def p_tipo(p):
    '''tipo : TYPE_INT
            | TYPE_DOUBLE
            | TYPE_STRING
            | TYPE_BOOL
            | TYPE_CHARACTER
            | LBRACKET tipo COLON tipo RBRACKET
            | LPAREN tipo COMMA lista_tipos RPAREN'''
    if len(p) == 2:
        p[0] = p[1]
    elif p.slice[1].type == 'LBRACKET':
        p[0] = ('tipo_diccionario', p[2], p[4])
    else:
        p[0] = ('tipo_tupla', [p[2]] + p[4])

def p_lista_tipos(p):
    '''lista_tipos : lista_tipos COMMA tipo
                   | tipo'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]

# Parámetros de funciones y argumentos de llamadas.
def p_parametros_opt(p):
    '''parametros_opt : parametros
                      | vacio'''
    p[0] = p[1]

def p_parametros(p):
    '''parametros : parametros COMMA parametro
                  | parametro'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]

def p_parametro(p):
    '''parametro : ID COLON tipo
                 | ID COLON tipo ASSIGN expresion'''
    if len(p) == 4:
        p[0] = (p[1], p[3])
    else:
        p[0] = (p[1], p[3], p[5])

def p_argumentos_opt(p):
    '''argumentos_opt : argumentos
                      | vacio'''
    p[0] = p[1]

def p_argumentos(p):
    '''argumentos : argumentos COMMA argumento
                  | argumento'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]

def p_argumento(p):
    '''argumento : ID COLON expresion
                 | expresion'''
    if len(p) == 4:
        p[0] = (p[1], p[3])
    else:
        p[0] = p[1]

# Expresiones y literales.
def p_lista_expresiones(p):
    '''lista_expresiones : lista_expresiones COMMA expresion
                         | expresion'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]

def p_expresion_literal(p):
    '''expresion : INT
                 | DOUBLE
                 | STRING
                 | TRUE
                 | FALSE
                 | NIL
                 | ID'''
    p[0] = p[1]

def p_expresion_llamada(p):
    '''expresion : ID LPAREN argumentos_opt RPAREN'''
    p[0] = ('llamada_funcion', p[1], p[3])

def p_expresion_readline(p):
    '''expresion : READLINE LPAREN RPAREN'''
    p[0] = ('lectura_teclado',)

def p_expresion_parentesis(p):
    '''expresion : LPAREN expresion RPAREN'''
    p[0] = p[2]

def p_expresion_operadores(p):
    '''expresion : expresion PLUS expresion
                 | expresion MINUS expresion
                 | expresion TIMES expresion
                 | expresion DIVIDE expresion
                 | expresion MOD expresion
                 | expresion EQ expresion
                 | expresion NE expresion
                 | expresion LT expresion
                 | expresion GT expresion
                 | expresion LE expresion
                 | expresion GE expresion
                 | expresion AND expresion
                 | expresion OR expresion
                 | expresion NIL_COALESCING expresion'''
    p[0] = ('expresion_binaria', p[2], p[1], p[3])

def p_expresion_unaria(p):
    '''expresion : MINUS expresion %prec UMINUS
                 | NOT expresion'''
    p[0] = ('expresion_unaria', p[1], p[2])

# Instrucciones adicionales de control.
def p_sentencia_while(p):
    '''sentencia : WHILE expresion LBRACE lista_sentencias_opt RBRACE'''
    p[0] = ('bucle_while', p[2], p[4])

def p_sentencia_break(p):
    '''sentencia : BREAK'''
    p[0] = ('break',)

def p_sentencia_continue(p):
    '''sentencia : CONTINUE'''
    p[0] = ('continue',)

def p_sentencia_return(p):
    '''sentencia : RETURN expresion
                 | RETURN'''
    if len(p) == 3:
        p[0] = ('retorno', p[2])
    else:
        p[0] = ('retorno_vacio',)

# Estructura switch, case y default.
def p_sentencia_switch(p):
    '''sentencia : SWITCH expresion LBRACE lista_casos_opt caso_default_opt RBRACE'''
    p[0] = ('switch', p[2], p[4], p[5])

def p_lista_casos_opt(p):
    '''lista_casos_opt : lista_casos
                       | vacio'''
    p[0] = p[1]

def p_lista_casos(p):
    '''lista_casos : lista_casos caso
                   | caso'''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]

def p_caso(p):
    '''caso : CASE lista_expresiones COLON lista_sentencias_opt'''
    p[0] = ('caso', p[2], p[4])

def p_caso_default_opt(p):
    '''caso_default_opt : DEFAULT COLON lista_sentencias_opt
                        | vacio'''
    if len(p) == 4:
        p[0] = ('default', p[3])
    else:
        p[0] = None

# ---------------------------------------------------------------------------
# Manejo de errores sintácticos
# ---------------------------------------------------------------------------
errores_sintacticos = []
codigo_actual = ''

def p_error(p):
    if p:
        columna = lexer_module.find_column(codigo_actual, p.lexpos)

        mensaje = (
            f"Error sintáctico: token inesperado '{p.value}' "
            f"(tipo {p.type}) en la línea {p.lineno}, "
            f"columna {columna}."
        )
    else:
        mensaje = (
            "Error sintáctico: fin de archivo inesperado. "
            "Puede faltar cerrar una expresión o un bloque."
        )

    errores_sintacticos.append(mensaje)

# ---------------------------------------------------------------------------
# Generación del log sintáctico
# ---------------------------------------------------------------------------
def escribir_log_sintactico(usuario_git, archivo, errores):
    ahora = datetime.now()

    os.makedirs(lexer_module.CARPETA_LOGS, exist_ok=True)

    nombre_log = f"sintactico-{usuario_git}-{ahora:%d%m%Y-%Hh%M}.txt"
    ruta = os.path.join(lexer_module.CARPETA_LOGS, nombre_log)

    lineas = [
        "Análisis sintáctico de Swift (PLY - yacc)",
        f"Desarrollador: {usuario_git}",
        f"Archivo: {archivo}",
        f"Fecha: {ahora:%d-%m-%Y %H:%M}",
        "",
        f"ERRORES SINTÁCTICOS ({len(errores)})"
    ]

    lineas += errores or ["Ninguno. No se encontraron errores sintácticos."]

    with open(ruta, 'w', encoding='utf-8') as archivo_log:
        archivo_log.write('\n'.join(lineas) + '\n')

    return ruta

# ---------------------------------------------------------------------------
# Construcción del analizador sintáctico
# ---------------------------------------------------------------------------

parser = yacc.yacc(
    start='programa',
    debug=False,
    write_tables=False
)

# ---------------------------------------------------------------------------
# Ejecución principal
# ---------------------------------------------------------------------------
if __name__ == '__main__':

    if len(sys.argv) != 3:
        print("Uso: python parser.py <archivo.swift> <usuarioGit>")
        sys.exit(1)

    archivo = sys.argv[1]
    usuario_git = ''.join(sys.argv[2].split())

    try:
        with open(archivo, encoding='utf-8') as archivo_swift:
            codigo_actual = archivo_swift.read()

    except FileNotFoundError:
        print(f"Error: no se encontró el archivo '{archivo}'.")
        sys.exit(1)

    print(f"\nAnalizando archivo: {archivo}")
    print("\nIniciando análisis sintáctico...")

    errores_sintacticos.clear()

    lexer_sintactico = lex.lex(module=lexer_module)
    lexer_sintactico.errores = []

    resultado = parser.parse(
        codigo_actual,
        lexer=lexer_sintactico,
        tracking=True
    )
    ruta_log_sintactico = escribir_log_sintactico(
        usuario_git,
        archivo,
        errores_sintacticos
    )

    print("Análisis sintáctico completado.")
    print(f"Errores sintácticos: {len(errores_sintacticos)}")
    print(
        "Log sintáctico generado: "
        f"{os.path.relpath(ruta_log_sintactico)}"
    )

    if errores_sintacticos:
        print("\nEl archivo contiene errores sintácticos.")
    else:
        print("\nEl archivo cumple las reglas sintácticas implementadas.")