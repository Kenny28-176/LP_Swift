// Algoritmo de prueba - Kenny Chung
// Registro de notas de un estudiante: constantes con tipo, tuplas,
// repeat-while y funciones con parámetro por defecto.

let curso: String = "Lenguajes de Programacion"
let notaMinima: Double = 7.0
let totalParciales: Int = 3

// Tuplas con elementos de distinto tipo
let alumno: (String, Int, Bool) = ("Ana", 20, true)
let mejorParcial: (Int, Double) = (2, 9.5)

// Función con parámetro por defecto
func saludar(nombre: String = "estudiante") -> String {
    return "Hola, " + nombre
}

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
print(saludar(nombre: alumno.0))
print("Curso:", curso, "- Edad:", alumno.1, "- Matriculado:", alumno.2)

// repeat-while: el bloque se ejecuta al menos una vez
var parcial: Int = 1
var nota: Double = 6.5
var suma: Double = 0.0
repeat {
    print("Parcial", parcial, "nota:", nota)
    suma += nota
    nota += 1.0
    parcial += 1
} while parcial <= totalParciales

let promedio: Double = suma / 3.0
let resultado: (Double, Bool) = evaluar(nota: promedio, minimo: notaMinima)
let resultadoPorDefecto: (Double, Bool) = evaluar(nota: 6.0)

print("Promedio:", resultado.0, "- Aprobado:", resultado.1)
print("Con 6.0 aprueba:", resultadoPorDefecto.1)
print("Mejor parcial:", mejorParcial.0, "con", mejorParcial.1)

let restante: Int = cuentaRegresiva()
print("Fin de la cuenta:", restante)
