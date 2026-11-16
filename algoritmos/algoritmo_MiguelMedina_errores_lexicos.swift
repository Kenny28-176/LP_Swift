// Algoritmo de prueba con errores léxicos: calificaciones de un curso
// Autor: Miguel Medina
// Variante corta de algoritmo_MiguelMedina.swift. Cada error está marcado
// con // ERROR n. El error 5 está marcado en la línea anterior porque una
// cadena sin cerrar se extiende hasta el fin de la línea.

var notas: [String: Double] = ["Ana": 8.5, "Luis": 6.75, "Sofia": 9.0]
let nombre: String = readLine() ?? "Ana"
let nota: Double = notas[nombre] ?? 0.0
var bonus: Int = 0 @ 2                      // ERROR 1: '@' no es del lenguaje

if nota >= 7.0 # nota <= 10.0 {             // ERROR 2: '#' no es del lenguaje
    print("Aprobado")
} else {
    print("Reprobado")
}

var puntos: Int = 10
puntos += ~5                                // ERROR 3: '~' no es del lenguaje
let promedio: Double = (8.5 + 6.75.2) / 3.0 // ERROR 4: número mal formado

let clasificar = { (valor: Double) -> String in
    if valor >= 9.0 {
        return "Excelente"
    }
    // ERROR 5: cadena sin cerrar
    return "Insuficiente
}

print("Promedio:", promedio, "-", clasificar(promedio))
