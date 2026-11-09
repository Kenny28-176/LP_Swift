# LP_Swift

Analizador léxico, sintáctico y semántico para un subconjunto de Swift, desarrollado con Python y PLY.
Proyecto de Lenguajes de Programación, ESPOL, término 2026-II.

**Integrantes:** Kevin Morales · Kenny Chung · Miguel Medina

## Requisitos

- Python 3.12 o superior
- PLY 3.11: `pip install -r requirements.txt`

## Avance 1: analizador léxico

```
python lexer.py <archivo.swift> <NombreApellido>
python lexer.py algoritmos/algoritmo_KennyChung.swift KennyChung
```

Cada prueba genera un log en `logs/` con el nombre `lexico-NombreApellido-dd-mm-aaaa-HHhMM.txt`, que contiene los tokens reconocidos (línea, columna, token y lexema) y los errores léxicos.

## Avance 2: analizador sintáctico
```
python parser.py <archivo.swift> <usuarioGit>
python parser.py algoritmos/algoritmo_KevinMorales.swift kevin-moralesc
```
El analizador sintáctico utiliza los tokens del analizador léxico para comprobar que el código cumpla las reglas gramaticales implementadas mediante PLY (Yacc).

Cada prueba genera un log en `logs/` con el nombre `sintactico-usuarioGit-ddmmaaaa-HHhMM.txt`, que contiene los errores sintácticos encontrados durante el análisis.

### Aporte de Miguel Medina (Miguelmml16)

Reglas dentro de la sección `Inicio aporte: Miguel Medina` de `parser.py`:

- **Estructura de datos: diccionarios.** Literal con pares `["Ana": 8.5, "Luis": 6.75]` (`p_diccionario_literal`, `p_pares_diccionario`, `p_par_diccionario`) y diccionario vacío `[:]` (`p_diccionario_vacio`). Un literal no puede mezclar pares con elementos sueltos.
- **Estructura de control: `if / else if / else`.** Admite cualquier cantidad de `else if` encadenados y el `else` final es opcional (`p_sentencia_if`, `p_condicional_if`, `p_bloque_else_opt`).
- **Tipo de función: closures.** Admite las formas `{ (a: Int) -> Int in ... }`, `{ (a: Int) in ... }` y `{ ... }`, y el tipo función `(Int, Int) -> Int` para anotar variables o parámetros que reciben un closure (`p_expresion_closure`, `p_firma_closure`, `p_tipo_funcion`).

```
python parser.py algoritmos/algoritmo_MiguelMedina.swift Miguelmml16
python parser.py algoritmos/algoritmo_MiguelMedina_errores.swift Miguelmml16
python -m unittest discover -s pruebas -v
```

`algoritmo_MiguelMedina_errores.swift` contiene errores intencionales. El parser los reporta junto con dos errores en cascada: después de recuperarse de un error, la `}` que cerraba ese bloque queda sin pareja.

## Estructura

- `lexer.py`: analizador léxico. Cada integrante agrega sus tokens dentro de su sección (`Inicio aporte` / `Fin aporte`).
- `parser.py`: analizador sintáctico. Contiene las reglas gramaticales implementadas por los integrantes.
- `algoritmos/`: algoritmos de prueba en Swift, uno por integrante.
- `logs/`: logs de las pruebas del analizador.
- `pruebas/`: pruebas automatizadas del parser (`unittest`, sin dependencias adicionales).
