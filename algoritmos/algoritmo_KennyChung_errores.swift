// Algoritmo de prueba con errores sintácticos - Kenny Chung
// Avance 2: variante de algoritmo_KennyChung.swift con cuatro errores
// sintácticos intencionales (tupla, parámetro por defecto, acceso a tupla
// y repeat-while). Cada uno está marcado con un comentario ERROR para
// comprobar que el analizador sintáctico los detecta y los registra en el log.

let curso: String = "Lenguajes de Programacion"
let notaMinima: Double = 7.0
let totalParciales: Int = 3

// Tuplas con elementos de distinto tipo
let alumno: (String, Int, Bool) = ("Ana", 20, true)
// ERROR 1 (tupla): falta la coma entre los dos elementos
let mejorParcial: (Int, Double) = (2 9.5)

// Función con parámetro por defecto
func saludar(nombre: String = "estudiante") -> String {
    return "Hola, " + nombre
}

// ERROR 2 (parámetro por defecto): falta el valor después del signo =
func despedir(nombre: String = ) -> String { return nombre }

// Función con parámetro por defecto que retorna una tupla
func evaluar(nota: Double, minimo: Double = 7.0) -> (Double, Bool) {
    return (nota, nota >= minimo)
}

// Función con repeat-while interno
func cuentaRegresiva(desde: Int = 3) -> Int {
    var n: Int = desde
    repeat {
        print("Faltan", n)
        n -= 1
    } while n > 0
    return n
}

print(saludar())
// ERROR 3 (acceso a tupla): falta el índice después del punto
print(saludar(nombre: alumno.))
print("Curso:", curso, "- Edad:", alumno.1, "- Matriculado:", alumno.2)

var parcial: Int = 1
var nota: Double = 6.5
var suma: Double = 0.0
// ERROR 4 (repeat-while): falta la palabra reservada while antes de la condición
repeat {
    print("Parcial", parcial, "nota:", nota)
    suma += nota
    nota += 1.0
    parcial += 1
} (parcial <= totalParciales)

let promedio: Double = suma / 3.0
let resultado: (Double, Bool) = evaluar(nota: promedio, minimo: notaMinima)
print("Promedio:", resultado.0, "- Aprobado:", resultado.1)

let restante: Int = cuentaRegresiva()
print("Fin de la cuenta:", restante)
