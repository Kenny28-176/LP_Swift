// Algoritmo de prueba con errores semánticos - Miguel Medina
// Avance 3: variante de algoritmo_MiguelMedina.swift con seis errores
// semánticos intencionales en las dos reglas de Miguel:
// 1. La condición de if, else if, while y repeat-while debe ser Bool.
// 2. Las claves y los valores de un diccionario deben coincidir con su
//    tipo declarado [K: V].
// Cada error está marcado con un comentario ERROR para comprobar que el
// analizador semántico lo detecta y lo registra en el log.

// ERROR 1 (diccionario): "seis" es String y los valores deben ser Double
var notas: [String: Double] = ["Ana": 8.5, "Luis": "seis", "Sofia": 9.0]

// ERROR 2 (diccionario): la clave 2 es Int y las claves deben ser String
let codigos: [String: Int] = ["Ana": 1, 2: 2, "Sofia": 3]

print("Ingrese el nombre del estudiante:")
let nombre: String = readLine() ?? "Ana"

// Si el estudiante no existe en el diccionario se usa 0.0
let nota: Double = notas[nombre] ?? 0.0
var aprobado: Bool = false
var bonus: Int = 0;

if nota >= 7.0 && nota <= 10.0 {
    aprobado = true
    print("Aprobado")
} else if nota > 5.0 || nota == 5.0 {
    print("Recuperación")
} else {
    print("Reprobado")
}

// ERROR 3 (condición): bonus es Int, no Bool
if bonus {
    print("Tiene bonus")
}

// ERROR 4 (condición): la condición del else if es String. El error se
// reporta en la línea del if, porque ahí empieza la sentencia.
if !aprobado && nota != 0.0 { print("Debe rendir el mejoramiento") } else if nombre { print("Sin examen") }

var puntos: Int = 10
puntos += 5
let residuo: Int = puntos % 4

switch residuo {
case 0:
    bonus = 2
case 1:
    bonus = 1
default:
    break
}

// ERROR 5 (condición): contador es Int, no Bool
var contador: Int = 3
while contador {
    contador -= 1
}

// ERROR 6 (condición): la condición del repeat-while es String. El error
// se reporta en la línea del repeat, porque ahí empieza la sentencia.
repeat { puntos -= 1 } while "hola"

// Estas condiciones y diccionarios son válidos
while puntos > 0 {
    puntos -= 1
}

var curvas: [String: Double] = ["Ana": 9, "Luis": 7.5]
let iniciales: [Character: Int] = ["A": 1, "L": 2]

let clasificar = { (valor: Double) -> String in
    if valor >= 9.0 {
        return "Excelente"
    } else if valor >= 7.0 && valor < 9.0 {
        return "Bueno"
    }
    return "Regular"
}

print("Nota final: \(nota), bonus: \(bonus)")
print("Clasificación:", clasificar(nota))
