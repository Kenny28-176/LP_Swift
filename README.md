# LP_Swift

Analizador léxico, sintáctico y semántico para un subconjunto de Swift, desarrollado con Python y PLY.
Proyecto de Lenguajes de Programación, ESPOL, término 2026-II.

**Integrantes:** Kevin Morales · Kenny Chung · Miguel Medina

## Requisitos

- Python 3.12 o superior
- PLY 3.11: `pip install -r requirements.txt`
- Tkinter, para la interfaz gráfica. Viene incluido con Python en Windows y macOS; en Linux se instala con `sudo apt install python3-tk`.

PLY es la única biblioteca que se instala aparte. El resto del proyecto usa la biblioteca estándar de Python.

## Interfaz gráfica

```
python interfaz.py
```

Desde la interfaz se puede escribir código o abrir un archivo `.swift`, y ejecutar cada fase con su botón (Léxico, Sintáctico, Semántico) o las tres en orden con Análisis completo (también con F5).

- **Resultados:** la tabla de tokens, el árbol sintáctico, la tabla de símbolos y el log de la prueba, cada uno en su pestaña.
- **Errores:** aparecen en el panel inferior con su fase, línea, columna y mensaje. Al elegir un error, el cursor va a esa línea del editor, que queda resaltada.
- **Logs:** antes de analizar se elige el desarrollador en la lista. Cada prueba genera en `logs/` el log de la fase ejecutada con el nombre de ese desarrollador; el análisis completo genera los tres. La casilla "Generar log" permite probar sin crear archivos.

Los analizadores también se pueden ejecutar por consola, como se indica en las secciones siguientes.

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

## Avance 3: analizador semántico
```
python semantico.py <archivo.swift> <usuarioGit>
python semantico.py algoritmos/algoritmo_KennyChung_errores_semanticos.swift Kenny28-176
```
El analizador semántico recorre el árbol que construye el analizador sintáctico, mantiene una tabla de símbolos por ámbitos y aplica las reglas semánticas de cada integrante. Si el archivo tiene errores léxicos o sintácticos, el análisis semántico no se ejecuta hasta que se corrijan.

Cada prueba genera un log en `logs/` con el nombre `semantico-usuarioGit-ddmmaaaa-HHhMM.txt`, que contiene los errores semánticos encontrados y la línea de cada uno.

## Estructura

- `lexer.py`: analizador léxico. Cada integrante agrega sus tokens dentro de su sección (`Inicio aporte` / `Fin aporte`).
- `parser.py`: analizador sintáctico. Contiene las reglas gramaticales implementadas por los integrantes.
- `semantico.py`: analizador semántico. Cada integrante agrega sus reglas dentro de su sección (`Inicio aporte` / `Fin aporte`).
- `interfaz.py`: interfaz gráfica (Tkinter) que integra los tres analizadores.
- `algoritmos/`: algoritmos de prueba en Swift de cada integrante: el algoritmo completo y variantes con errores intencionales para probar cada analizador.
- `logs/`: logs de las pruebas de cada analizador.
