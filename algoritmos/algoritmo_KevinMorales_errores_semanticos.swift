// Algoritmo de prueba con errores semánticos - Kevin Morales
// Avance 3: variante de algoritmo_KevinMorales.swift con cinco errores
// semánticos intencionales relacionados con las dos reglas de Kevin:
// 1. Los operandos de una operación aritmética deben ser del mismo tipo.
// 2. Todo identificador debe estar declarado antes de utilizarse.
// Cada error está marcado con un comentario ERROR para comprobar que el analizador lo detecte
// y lo registre en el log.

// Declaración de variables mutables con tipo explícito
var nombreTienda: String = "Tienda PoliESPOL"
var cantidadDias: Int = 5
var totalVentasNetas: Int = 0

// Estructura de datos: arreglos
var ventas: [Int] = [120, 250, 180, 300, 420]
var comisiones: [Int] = [5, 10, 8, 15, 20]

// ERROR 1: se intenta sumar un Int con un Double.
print("Prueba 1:", ventas[0] + 2.5)

// ERROR 2: se intenta multiplicar un Int con un Double.
print("Prueba 2:", comisiones[1] * 1.5)

// ERROR 3: se intenta dividir un Double entre un Int.
var porcentaje: Double = 10.0
print("Prueba 3:", porcentaje / cantidadDias)

// ERROR 4: codigoDescuento no ha sido declarado.
print("Código de descuento:", codigoDescuento)

// ERROR 5: nombreCliente no ha sido declarado.
print("Cliente:", nombreCliente)

// Funciones con múltiples parámetros y valor de retorno
func calcularVentaNeta(venta: Int, comision: Int) -> Int {
    return venta - comision
}

func calcularPromedioVentas(total: Int, dias: Int) -> Int {
    return total / dias
}

// Bucle for-in con rango semiabierto
print("--- Procesamiento de Ventas Diarias (..<) ---")
for i in 0..<5 {
    var ventaReal: Int = calcularVentaNeta(venta: ventas[i], comision: comisiones[i])
    print("Dia", i, "venta neta:", ventaReal)
    totalVentasNetas += ventaReal
}

// Bucle for-in con rango cerrado
print("--- Calculo de Bonos por Meta (...) ---")
for meta in 1...3 {
    var bonoExtra: Int = meta * 50
    totalVentasNetas += bonoExtra
    print("Meta alcanzada:", meta, "bono otorgado:", bonoExtra)
}

// Cálculo final y llamadas a funciones
var promedioDiario: Int = calcularPromedioVentas(total: totalVentasNetas, dias: cantidadDias)

print("Tienda:", nombreTienda)
print("Total neto acumulado:", totalVentasNetas)
print("Promedio diario:", promedioDiario)
