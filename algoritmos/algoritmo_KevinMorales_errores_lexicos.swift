// Algoritmo de prueba con errores léxicos - Kevin Morales
// Variante corta de algoritmo_KevinMorales.swift con caracteres
// que no pertenecen al lenguaje. Cada uno está marcado con ERROR.

var nombreTienda: String = "Tienda PoliESPOL"
var cantidadDias: Int = 5

// ERROR 1 (léxico): el carácter # no pertenece al lenguaje.
var totalVentas: Int = 0 #

// ERROR 2 (léxico): el carácter @ no pertenece al lenguaje.
var comision: Int = 10 @

// ERROR 3 (léxico): el carácter ^ no pertenece al lenguaje.
var potencia: Int = 2 ^ 3

print("Tienda:", nombreTienda)