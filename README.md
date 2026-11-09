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


## Estructura

- `lexer.py`: analizador léxico. Cada integrante agrega sus tokens dentro de su sección (`Inicio aporte` / `Fin aporte`).
- `parser.py`: analizador sintáctico. Contiene las reglas gramaticales implementadas por los integrantes.
- `algoritmos/`: algoritmos de prueba en Swift, uno por integrante.
- `logs/`: logs de las pruebas del analizador.
