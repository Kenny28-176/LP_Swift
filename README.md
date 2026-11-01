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

## Estructura

- `lexer.py`: analizador léxico. Cada integrante agrega sus tokens dentro de su sección (`Inicio aporte` / `Fin aporte`).
- `algoritmos/`: algoritmos de prueba en Swift, uno por integrante.
- `logs/`: logs de las pruebas del analizador.
