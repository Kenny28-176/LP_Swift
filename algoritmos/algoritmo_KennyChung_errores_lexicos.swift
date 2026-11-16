// Algoritmo de prueba con errores léxicos - Kenny Chung
// Avance final: variante de algoritmo_KennyChung.swift con cinco errores
// léxicos intencionales (caracteres que no pertenecen al lenguaje). Cada uno
// está marcado con un comentario ERROR para comprobar que el analizador
// léxico lo reporta con su línea y su columna.

let curso: String = "Lenguajes de Programacion"

// ERROR 1 (carácter no válido): el signo # no es parte del lenguaje
let notaMinima: Double = #7.0
let totalParciales: Int = 3

// ERROR 2 (comilla simple): las cadenas solo se escriben con comilla doble.
// Se reporta un error por cada comilla.
let alumno: (String, Int, Bool) = ('Ana', 20, true)

// Función con parámetro por defecto
func saludar(nombre: String = "estudiante") -> String {
    return "Hola, " + nombre
}

// ERROR 3 (carácter no válido): el signo @ antes del nombre de la función
print(@saludar())

// repeat-while: el bloque se ejecuta al menos una vez
var parcial: Int = 1
var suma: Double = 0.0
repeat {
    // ERROR 4 (operador no válido): ^ no es un operador del lenguaje
    suma += 6.5 ^ 2.0
    parcial += 1
// ERROR 5 (operador incompleto): un solo & no es el operador lógico &&
} while parcial <= totalParciales & parcial > 0

print("Suma de notas:", suma)
