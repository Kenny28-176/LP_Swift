// Algoritmo de prueba con errores sintácticos - Kevin Morales
// Avance 2: variante de algoritmo_KevinMorales.swift con tres errores
// sintácticos intencionales (arreglo, función, for-in y asignación).
// Cada uno está marcado con un comentario ERROR para comprobar que
// el analizador sintáctico los detecta y los registra en el log.


// Declaración de variables mutables con tipo explícito (var)

var nombreTienda: String = "Tienda PoliESPOL"
var cantidadDias: Int = 5
var totalVentasNetas: Int = 0


// Estructura de Datos: Arreglos (Array)

// ERROR 1 (arreglo): falta la coma entre los elementos.
var ventas: [Int] = [120 250, 180, 300, 420]

var comisiones: [Int] = [5, 10, 8, 15, 20]


// Funciones con múltiples parámetros y valor de retorno

// ERROR 2 (función): falta la coma entre los parámetros.
func calcularVentaNeta(venta: Int comision: Int) -> Int {
    return venta - comision
}

func calcularPromedioVentas(total: Int, dias: Int) -> Int {
    return total / dias
}


// Bucle for-in con rango semiabierto (..<) para recorrer el arreglo por índice

print("--- Procesamiento de Ventas Diarias (..<) ---")

// Bucle for-in con rango semiabierto (..<)

for i in 0..<5 {
    var ventaReal: Int = calcularVentaNeta(venta: ventas[i], comision: comisiones[i])
    print("Dia", i, "venta neta:", ventaReal)
    totalVentasNetas += ventaReal
}


// Bucle for-in con rango cerrado (...)

print("--- Calculo de Bonos por Meta (...) ---")

for meta in 1...3 {
    var bonoExtra: Int = meta * 50

    // ERROR 3 (asignación): falta la expresión del lado derecho.
    totalVentasNetas +=

    print("Meta alcanzada:", meta, "bono otorgado:", bonoExtra)
}


// Cálculo final y llamadas a funciones

var promedioDiario: Int = calcularPromedioVentas(total: totalVentasNetas, dias: cantidadDias)

print("Tienda:", nombreTienda)
print("Total neto acumulado:", totalVentasNetas)
print("Promedio diario:", promedioDiario)