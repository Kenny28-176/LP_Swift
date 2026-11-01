// Algoritmo de prueba: calificaciones de un curso
// Autor: Miguel Medina

/* Prueba de comentario multilínea:
   esta parte no debe generar tokens */

// Diccionario con las notas de los estudiantes
var notas: [String: Double] = ["Ana": 8.5, "Luis": 6.75, "Sofia": 9.0]

print("Ingrese el nombre del estudiante:")
let nombre: String = readLine() ?? "Ana"

// Si el estudiante no existe en el diccionario se usa 0.0
let nota: Double = notas[nombre] ?? 0.0
var aprobado: Bool = false
var bonus: Int = 0;

// Operadores de comparación y lógicos
if nota >= 7.0 && nota <= 10.0 {
    aprobado = true
    print("Aprobado")
} else if nota > 5.0 || nota == 5.0 {
    print("Recuperación")
} else {
    print("Reprobado")
}

if !aprobado && nota != 0.0 {
    print("Debe rendir el examen de mejoramiento")
}

// Operadores aritméticos y de asignación compuesta
var puntos: Int = 10
puntos += 5
puntos -= 2
puntos *= 3
puntos /= 2
let residuo: Int = puntos % 4
let promedio: Double = (8.5 + 6.75 + 9.0) / 3.0
let diferencia: Double = 10.0 - promedio * 1.0

// switch con break y default
switch residuo {
case 0:
    bonus = 2
case 1:
    bonus = 1
default:
    break
}

// continue dentro de un ciclo: solo cuenta los números impares
var contador: Int = 0
while puntos > 0 {
    puntos -= 1
    if puntos % 2 == 0 {
        continue
    }
    contador += 1
}

let comentario: String = readLine() ?? "Sin comentarios"
if readLine() == nil {
    print("No hay más datos de entrada")
}

let inicial: Character = "M"
print("Nota final: \(nota), bonus: \(bonus), inicial: \(inicial)")
