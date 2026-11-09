// Algoritmo de prueba con errores sintácticos - Miguel Medina
// Avance 2: variante de algoritmo_MiguelMedina.swift con errores sintácticos
// intencionales en diccionarios, if / else if / else y closures. Cada uno
// está marcado con un comentario ERROR para comprobar que el analizador
// sintáctico los detecta y los registra en el log. El último error es un
// bloque sin cerrar, que se detecta al llegar al fin del archivo.

// ERROR 1 (diccionario): falta ':' entre la clave "Ana" y su valor
var notas: [String: Double] = ["Ana" 8.5, "Luis": 6.75, "Sofia": 9.0]
var aprobado: Bool = false

// ERROR 2 (diccionario): se mezcla un par clave: valor con un elemento suelto
var extras: [String: Int] = ["bonus": 2, 3]
let nota: Double = 8.5

// ERROR 3 (if): falta la llave de apertura del bloque
if nota >= 7.0 && nota <= 10.0
    aprobado = true
}
var bonus: Int = 0

// ERROR 4 (else if): falta la palabra 'if' entre 'else' y la condición
if nota > 9.0 {
    bonus = 2
} else nota > 5.0 {
    bonus = 1
}
var puntos: Int = 10

// ERROR 5 (closure): falta 'in' entre la firma y el cuerpo
let sumar = { (a: Int, b: Int) -> Int return a + b }
var contador: Int = 0

// ERROR 6 (closure): falta el tipo de retorno después de '->'
let duplicar: (Int) -> = { (x: Int) -> Int in return x * 2 }
var total: Int = 0

// ERROR 7 (fin de archivo): el bloque del if no se cierra
if puntos > 0 {
    print("Puntos:", puntos)
