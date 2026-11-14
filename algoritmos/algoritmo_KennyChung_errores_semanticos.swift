// Algoritmo de prueba con errores semánticos - Kenny Chung
// Avance 3: variante de algoritmo_KennyChung.swift con siete errores
// semánticos intencionales en las dos reglas de Kenny: una constante (let)
// no se puede modificar y cada return debe ser del tipo declarado después
// de ->. Cada uno está marcado con un comentario ERROR para comprobar que
// el analizador semántico los detecta y los registra en el log.

let curso: String = "Lenguajes de Programacion"
let notaMinima: Double = 7.0
let totalParciales: Int = 3

// Tuplas con elementos de distinto tipo
let alumno: (String, Int, Bool) = ("Ana", 20, true)
let mejorParcial: (Int, Double) = (2, 9.5)

// ERROR 1 (constante): notaMinima se declaró con let
notaMinima = 6.0

// ERROR 2 (constante): tampoco se permite la asignación compuesta
totalParciales += 1

// ERROR 3 (retorno): la función declara String y retorna un Int
func saludar(nombre: String = "estudiante") -> String {
    return 0
}

// ERROR 4 (retorno): el segundo elemento de la tupla debe ser Bool
func evaluar(nota: Double, minimo: Double = 7.0) -> (Double, Bool) {
    return (nota, minimo)
}

// Función con repeat-while interno
func cuentaRegresiva(desde: Int = 3) -> Int {
    // ERROR 5 (constante): un parámetro también es una constante
    desde -= 1
    var n: Int = desde
    repeat {
        print("Faltan", n)
        n -= 1
        if n == 1 {
            // ERROR 6 (retorno): dentro de un bloque anidado, retorna Bool
            return n > 0
        }
    } while n > 0
    // ERROR 7 (retorno): return sin valor en una función que retorna Int
    return
}

print(saludar())
print(saludar(nombre: alumno.0))
print("Curso:", curso, "- Edad:", alumno.1, "- Matriculado:", alumno.2)

// Estas asignaciones son válidas: las tres variables se declararon con var
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
print("Promedio:", resultado.0, "- Aprobado:", resultado.1)
print("Mejor parcial:", mejorParcial.0, "con", mejorParcial.1)

let restante: Int = cuentaRegresiva()
print("Fin de la cuenta:", restante)
