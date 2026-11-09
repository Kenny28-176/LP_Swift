# Pruebas del analizador sintáctico - aporte de Miguel Medina (avance 2)
# Diccionarios, if / else if / else y closures.
#
# Uso (desde la raíz del repositorio):
#   python -m unittest discover -s pruebas -v
#
# Estas pruebas llaman al parser en memoria y no escriben logs; la evidencia
# en logs/ se genera con: python parser.py <archivo.swift> <usuarioGit>

import io
import os
import re
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

import ply.lex as lex  # noqa: E402
import ply.yacc as yacc  # noqa: E402

import lexer as lexer_module  # noqa: E402
import parser as parser_module  # noqa: E402


def analizar(codigo):
    """Analiza el código desde cero y devuelve (ast, errores_sintacticos, errores_lexicos)."""
    parser_module.codigo_actual = codigo
    parser_module.errores_sintacticos.clear()
    lexer_sintactico = lex.lex(module=lexer_module)
    lexer_sintactico.errores = []
    ast = parser_module.parser.parse(codigo, lexer=lexer_sintactico, tracking=True)
    return ast, list(parser_module.errores_sintacticos), list(lexer_sintactico.errores)


def analizar_archivo(ruta_relativa):
    with open(os.path.join(RAIZ, ruta_relativa), encoding='utf-8') as archivo:
        return analizar(archivo.read())


class PruebaBase(unittest.TestCase):
    def assertValido(self, codigo):
        ast, errores, lexicos = analizar(codigo)
        self.assertEqual(lexicos, [], f"errores léxicos inesperados en:\n{codigo}")
        self.assertEqual(errores, [], f"errores sintácticos inesperados en:\n{codigo}")
        return ast

    def assertInvalido(self, codigo, fragmento=None):
        _, errores, lexicos = analizar(codigo)
        self.assertEqual(lexicos, [], "el caso inválido debe fallar en el parser, no en el lexer")
        self.assertTrue(errores, f"se esperaba un error sintáctico en:\n{codigo}")
        if fragmento:
            self.assertIn(fragmento, errores[0])
        return errores


class TestConstruccion(unittest.TestCase):
    def test_sin_conflictos_nuevos(self):
        """Solo debe quedar el conflicto previo de 'return' sin valor (reglas comunes)."""
        avisos = io.StringIO()
        depuracion = io.StringIO()
        yacc.yacc(module=parser_module, start='programa', debug=True,
                  write_tables=False, errorlog=yacc.PlyLogger(avisos),
                  debuglog=yacc.PlyLogger(depuracion))
        tabla = depuracion.getvalue()

        self.assertNotIn('reduce/reduce', avisos.getvalue())
        self.assertNotIn('not used', avisos.getvalue(), "IF y ELSE deben usarse")
        estados = re.split(r'\nstate \d+\n', tabla)
        for estado in estados:
            if '! shift/reduce conflict' in estado:
                self.assertIn('sentencia -> RETURN .', estado)


class TestDiccionarios(PruebaBase):
    def test_literal_con_pares(self):
        ast = self.assertValido(
            'var notas: [String: Double] = ["Ana": 8.5, "Luis": 6.75, "Sofia": 9.0]')
        literal = ast[1][0][3]
        self.assertEqual(literal[0], 'diccionario_literal')
        self.assertEqual(len(literal[1]), 3)
        self.assertEqual(literal[1][0], ('par_diccionario', '"Ana"', 8.5))

    def test_un_solo_par_y_claves_enteras(self):
        self.assertValido('let d: [Int: String] = [1: "uno"]')

    def test_diccionario_vacio(self):
        ast = self.assertValido('var extras: [String: Int] = [:]')
        self.assertEqual(ast[1][0][3], ('diccionario_vacio',))

    def test_valores_con_expresiones_y_arreglos(self):
        self.assertValido('let n: Double = 2.0\n'
                          'var d: [String: Double] = ["a": n * 2.0 + 1.0, "b": (n - 1.0) / 2.0]\n'
                          'var g: [String: [Int]] = ["p": [1, 2], "q": []]')

    def test_inferido_acceso_y_asignacion(self):
        self.assertValido('var notas = ["Ana": 8.5]\n'
                          'notas["Luis"] = 7.0\n'
                          'notas["Ana"] += 0.5\n'
                          'let n: Double = notas["Ana"] ?? 0.0')

    def test_arreglo_sigue_funcionando(self):
        ast = self.assertValido('var v: [Int] = [1, 2, 3]')
        self.assertEqual(ast[1][0][3][0], 'arreglo_literal')

    def test_falta_dos_puntos(self):
        self.assertInvalido('var d: [String: Int] = ["a" 1]', "'1'")

    def test_mezcla_par_y_elemento(self):
        self.assertInvalido('var d: [String: Int] = ["a": 1, 2]', "']'")

    def test_par_sin_valor(self):
        self.assertInvalido('var d: [String: Int] = ["a": ]', "']'")


class TestIfElse(PruebaBase):
    def test_if_simple(self):
        ast = self.assertValido('if x > 1 {\n print("si")\n}')
        self.assertEqual(ast[1][0][0], 'if')
        self.assertIsNone(ast[1][0][3])

    def test_if_else(self):
        ast = self.assertValido('if x > 1 { print("si") } else { print("no") }')
        self.assertEqual(ast[1][0][3][0], 'else')

    def test_cadena_else_if(self):
        ast = self.assertValido(
            'if n >= 9.0 { a = 1 } else if n >= 7.0 && n < 9.0 { a = 2 }\n'
            'else if n == 5.0 || !ok { a = 3 } else { a = 4 }')
        segundo = ast[1][0][3]
        self.assertEqual(segundo[0], 'else_if')
        tercero = segundo[1][3]
        self.assertEqual(tercero[0], 'else_if')
        self.assertEqual(tercero[1][3][0], 'else')

    def test_bloques_vacios_y_anidados(self):
        self.assertValido('while x > 0 {\n'
                          '  if x % 2 == 0 {\n'
                          '    if x > 10 { continue } else { }\n'
                          '  } else if x == 1 {\n'
                          '    break\n'
                          '  }\n'
                          '  x -= 1\n'
                          '}')

    def test_if_dentro_de_funcion_y_switch(self):
        self.assertValido('func f(n: Int) -> Int {\n'
                          '  switch n {\n'
                          '  case 1:\n'
                          '    if n > 0 { return 1 }\n'
                          '  default:\n'
                          '    return 0\n'
                          '  }\n'
                          '  return n\n'
                          '}')

    def test_falta_llave_de_apertura(self):
        self.assertInvalido('if x > 1\n print("si")\n}', "'print'")

    def test_else_sin_if_ni_bloque(self):
        self.assertInvalido('if x > 1 { a = 1 } else x < 0 { a = 2 }', "'x'")

    def test_if_sin_condicion(self):
        # '{ a = 1 }' es un closure válido, así que se toma como condición y
        # el error aparece al final: falta el bloque del if.
        self.assertInvalido('if { a = 1 }', 'fin de archivo')

    def test_else_sin_if_previo(self):
        self.assertInvalido('else { a = 1 }', "'else'")

    def test_bloque_sin_cerrar_al_final(self):
        self.assertInvalido('if x > 1 {\n print("si")', 'fin de archivo')


class TestClosures(PruebaBase):
    def test_parametros_y_retorno(self):
        ast = self.assertValido('let sumar = { (a: Int, b: Int) -> Int in return a + b }')
        closure = ast[1][0][3]
        self.assertEqual(closure[0], 'closure')
        self.assertEqual(closure[1], ('firma_closure', [('a', 'Int'), ('b', 'Int')], 'Int'))

    def test_sin_tipo_de_retorno(self):
        self.assertValido('let mostrar = { (n: Double) in print(n) }')

    def test_sin_parametros(self):
        self.assertValido('let hola = { () -> String in return "Hola" }')

    def test_sin_firma_y_vacio(self):
        self.assertValido('let fin = { return "Fin" }\nlet nada = { }')

    def test_anotado_con_tipo_funcion(self):
        self.assertValido('let f: (Int, Int) -> Int = { (a: Int, b: Int) -> Int in return a * b }\n'
                          'let g: (Double) -> Bool = { (x: Double) -> Bool in return x > 0.0 }\n'
                          'let h: () -> String = { () -> String in return "h" }')

    def test_tupla_sigue_funcionando(self):
        self.assertValido('let t: (String, Int) = ("Ana", 20)')

    def test_como_argumento_y_parametro(self):
        self.assertValido('func aplicar(n: Double, regla: (Double) -> Double) -> Double {\n'
                          '  return regla(n)\n'
                          '}\n'
                          'let r: Double = aplicar(n: 8.0, regla: { (x: Double) -> Double in return x + 1.0 })')

    def test_retornado_por_funcion(self):
        self.assertValido('func crear() -> (Int) -> Int {\n'
                          '  return { (x: Int) -> Int in return x * 2 }\n'
                          '}')

    def test_cuerpo_con_if_y_diccionario(self):
        self.assertValido('let c = { (n: Double) -> String in\n'
                          '  var d: [String: Double] = [:]\n'
                          '  d["n"] = n\n'
                          '  if n > 5.0 { return "alto" } else { return "bajo" }\n'
                          '}')

    def test_falta_in(self):
        self.assertInvalido('let s = { (a: Int) -> Int return a }', "'return'")

    def test_falta_tipo_de_retorno(self):
        self.assertInvalido('let s = { (a: Int) -> in return a }', "'in'")

    def test_parametro_sin_tipo(self):
        self.assertInvalido('let s = { (a) in return a }', "')'")

    def test_tipo_funcion_incompleto(self):
        self.assertInvalido('let f: (Int) -> = { (x: Int) -> Int in return x }', "'='")

    def test_closure_sin_cerrar(self):
        self.assertInvalido('let s = { (a: Int) -> Int in return a', 'fin de archivo')


class TestRecuperacionYEstado(PruebaBase):
    def test_estado_se_reinicia_entre_analisis(self):
        _, primeros, _ = analizar_archivo('algoritmos/algoritmo_MiguelMedina_errores.swift')
        self.assertValido('var d: [String: Int] = ["a": 1]')
        _, segundos, _ = analizar_archivo('algoritmos/algoritmo_MiguelMedina_errores.swift')
        self.assertEqual(primeros, segundos)

    def test_varios_errores_no_se_ocultan(self):
        _, errores, lexicos = analizar('var a: [String: Int] = ["x" 1]\n'
                                       'var b: Int = 0\n'
                                       'let s = { (a: Int) -> Int return a }\n'
                                       'var c: Int = 0\n')
        self.assertEqual(lexicos, [])
        self.assertEqual(len(errores), 2)
        self.assertIn('línea 1', errores[0])
        self.assertIn('línea 3', errores[1])

    def test_lexico_y_sintactico_se_distinguen(self):
        # El lexer descarta '@' y lo reporta; lo que queda es sintácticamente válido.
        _, errores, lexicos = analizar('var a: Int = 1 @\nvar b: Int = 2')
        self.assertEqual(len(lexicos), 1)
        self.assertIn("'@'", lexicos[0])
        self.assertEqual(errores, [])
        # Si al descartar el carácter el resto queda inválido, hay ambos tipos.
        _, errores, lexicos = analizar('var a: Int = 1 @ 2')
        self.assertEqual(len(lexicos), 1)
        self.assertEqual(len(errores), 1)


class TestAlgoritmos(unittest.TestCase):
    """Algoritmo completo de Miguel y regresión contra los logs del equipo."""

    def test_algoritmo_miguel_sin_errores(self):
        _, errores, lexicos = analizar_archivo('algoritmos/algoritmo_MiguelMedina.swift')
        self.assertEqual(lexicos, [])
        self.assertEqual(errores, [])

    def test_algoritmo_miguel_errores_intencionales(self):
        _, errores, lexicos = analizar_archivo('algoritmos/algoritmo_MiguelMedina_errores.swift')
        self.assertEqual(lexicos, [])
        lineas = [int(m.group(1)) for e in errores
                  for m in [re.search(r'línea (\d+)', e)] if m]
        # 7 errores intencionales (líneas 9, 13, 18, 25, 31, 35 y fin de archivo)
        # más 2 en cascada: tras recuperarse de los errores 4 y 6, PLY descarta
        # tokens y la '}' que cierra ese bloque/closure queda sin pareja
        # (línea 27 y línea 35). Se registran, no se ocultan.
        self.assertEqual(lineas, [9, 13, 18, 25, 27, 31, 35, 35])
        self.assertIn("'}'", errores[4])
        self.assertIn("'}'", errores[7])
        self.assertIn('fin de archivo', errores[-1])
        self.assertEqual(len(errores), 9)

    def test_regresion_algoritmos_del_equipo(self):
        # Cantidad de errores registrada en los logs que subió cada integrante.
        esperados = {
            'algoritmos/algoritmo_KennyChung.swift': 0,
            'algoritmos/algoritmo_KennyChung_errores.swift': 4,
            'algoritmos/algoritmo_KevinMorales.swift': 3,
        }
        for ruta, cantidad in esperados.items():
            with self.subTest(ruta=ruta):
                _, errores, _ = analizar_archivo(ruta)
                self.assertEqual(len(errores), cantidad)


if __name__ == '__main__':
    unittest.main()
