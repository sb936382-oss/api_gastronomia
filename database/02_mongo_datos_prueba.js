// =====================================================================
// 02_mongo_datos_prueba.js
// Datos de prueba de bd_gastronomia (mínimo 10 documentos por colección principal)
// Contraseña de todos los usuarios de prueba: Admin123*  (hash bcrypt, RN06)
// Subtotales y totales calculados con las reglas RN01 (pedidos) y de compras
// Se ejecuta automáticamente con docker compose después de 01_mongo_estructura.js
// o manualmente:  mongosh -u admin -p --authenticationDatabase admin database/02_mongo_datos_prueba.js
// =====================================================================
const k_db = db.getSiblingDB('bd_gastronomia');

// ---------- Funciones de apoyo ----------
const k_int = (k_n) => NumberInt(k_n);
const k_dinero = (k_n) => NumberDecimal(k_n.toFixed(2));
const k_cantidad = (k_n) => NumberDecimal(k_n.toFixed(3));
// La API guarda las fechas con la hora de Bogotá tal cual (sin zona horaria); aquí se hace igual
const k_fecha = (k_texto) => new Date(k_texto + 'Z');
// Hoy en Bogotá (UTC-5) a las 00:00, para que los insumos venzan en N días contados desde hoy
const k_ahora_bogota = new Date(Date.now() - 5 * 60 * 60 * 1000);
const k_hoy = Date.UTC(k_ahora_bogota.getUTCFullYear(), k_ahora_bogota.getUTCMonth(), k_ahora_bogota.getUTCDate());
const k_en_dias = (k_dias) => (k_dias === null ? null : new Date(k_hoy + k_dias * 24 * 60 * 60 * 1000));

// 1. Categorías: [nombre, descripcion, estado]
const k_categorias = [
  ['Entradas', 'Platos para iniciar la comida', 'ACTIVO'],
  ['Platos Fuertes', 'Platos principales y almuerzos', 'ACTIVO'],
  ['Postres', 'Dulces y postres', 'ACTIVO'],
  ['Bebidas', 'Bebidas frías y calientes', 'ACTIVO'],
  ['Ensaladas', 'Ensaladas frescas', 'ACTIVO'],
  ['Sopas', 'Sopas y cremas', 'ACTIVO'],
  ['Panadería', 'Pan artesanal horneado en la unidad productiva', 'ACTIVO'],
  ['Repostería', 'Tortas, galletas y productos de repostería', 'ACTIVO'],
  ['Desayunos', 'Desayunos para aprendices y funcionarios', 'ACTIVO'],
  ['Comidas Rápidas', 'Comidas rápidas y refrigerios', 'ACTIVO']
];
k_db.categorias.insertMany(k_categorias.map((k_c, k_i) => ({
  id_categoria: k_int(k_i + 1), nombre: k_c[0], descripcion: k_c[1], estado: k_c[2]
})));

// 2. Usuarios: [identificacion, nombres, apellidos, correo, password (bcrypt), rol, estado]
const k_usuarios = [
  ['1000000001', 'Carlos', 'Administrador', 'admin@gastronomia.com', '$2b$12$Abk9m0EFFdpAoa7dWz6bSO0PA11ct671vMwN94GrUxc22H8x0LaFm', 'ADMIN', 'ACTIVO'],
  ['1000000002', 'María', 'Cajera', 'cajero@gastronomia.com', '$2b$12$H632AYBhikOpOOC1x4GBle3a1VtFFgaFy0hyVKB4QMGwTMD6/rurW', 'CAJERO', 'ACTIVO'],
  ['1000000003', 'Juan', 'Cocinero', 'cocinero@gastronomia.com', '$2b$12$qcp7fV.kl5IqdUNyfuDKguzdHzEfDJ1VE44vi2hrnEHftB4HO8T6y', 'COCINERO', 'ACTIVO'],
  ['1000000004', 'Ana', 'Cajera Dos', 'cajero2@gastronomia.com', '$2b$12$iQISro3/ayGesxOUBSJiOOM0JLfd17TLXtJXVXpNPRB.2UbMKgZly', 'CAJERO', 'ACTIVO'],
  ['1000000005', 'Pedro', 'Cocinero Dos', 'cocinero2@gastronomia.com', '$2b$12$bvt/yJwgZMtRfyBfn33fYOs9U0fqQ1t/fnbvgGD1n8p2vfOHTE0i.', 'COCINERO', 'ACTIVO'],
  ['1000000006', 'Luisa', 'Administradora', 'admin2@gastronomia.com', '$2b$12$9bZdWT9Ngg5l5Oo527JLae2fEryzftqaDH067lQHIGU5Oc76/j.BS', 'ADMIN', 'ACTIVO'],
  ['1000000007', 'Felipe', 'Cajero Tres', 'cajero3@gastronomia.com', '$2b$12$MaB3JBrSkh6f0ADacdEjE.L6mmAGu3.KjedX5aCJARdVgatdq/LhS', 'CAJERO', 'ACTIVO'],
  ['1000000008', 'Sandra', 'Cocinera Tres', 'cocinero3@gastronomia.com', '$2b$12$p3eq83apolml1Q4xITBJse/gPo7X8Ld1thySqXZmZAPMozrIURbzm', 'COCINERO', 'ACTIVO'],
  ['1000000009', 'Óscar', 'Cajero Cuatro', 'cajero4@gastronomia.com', '$2b$12$n/X.HCvEB2ERVH4iWN2C9esAf5gpVAbVhQZxHYOWWz6wDJq5ESdlS', 'CAJERO', 'ACTIVO'],
  ['1000000010', 'Laura', 'Inactiva', 'inactivo@gastronomia.com', '$2b$12$Fs1bOJj93Q0RQMKKOnDOpOmbmgfI417XZkYQ3O2DSqohLRnA5oeMW', 'CAJERO', 'INACTIVO']
];
k_db.usuarios.insertMany(k_usuarios.map((k_u, k_i) => ({
  id_usuario: k_int(k_i + 1), identificacion: k_u[0], nombres: k_u[1], apellidos: k_u[2], correo: k_u[3],
  password: k_u[4], rol: k_u[5], estado: k_u[6]
})));

// 3. Productos (incluye un producto AGOTADO y uno INACTIVO)
//    [codigo, nombre, descripcion, precio_venta, unidad_venta, id_categoria, estado]
const k_productos = [
  ['ENT001', 'Ceviche Mixto', 'Ceviche de pescado y mariscos frescos', 25000, 'porcion', 1, 'DISPONIBLE'],
  ['ENT002', 'Empanadas de Carne', 'Empanadas caseras de carne', 12000, 'porcion', 1, 'DISPONIBLE'],
  ['ENT003', 'Patacones con Hogao', 'Plátano verde frito con hogao criollo', 10000, 'porcion', 1, 'DISPONIBLE'],
  ['PF001', 'Bandeja Paisa', 'Frijoles, arroz, carne, chorizo, huevo, aguacate y plátano', 35000, 'porcion', 2, 'DISPONIBLE'],
  ['PF002', 'Salmón a la Plancha', 'Salmón fresco con vegetales salteados', 42000, 'porcion', 2, 'DISPONIBLE'],
  ['PF003', 'Pollo a la Brasa', 'Pollo marinado asado con papas', 28000, 'porcion', 2, 'DISPONIBLE'],
  ['PF004', 'Lomo Saltado', 'Carne de res salteada con cebolla, tomate y papas', 32000, 'porcion', 2, 'DISPONIBLE'],
  ['PST001', 'Tres Leches', 'Bizcocho bañado en tres leches', 15000, 'porcion', 3, 'DISPONIBLE'],
  ['PST002', 'Flan de Caramelo', 'Flan casero con caramelo', 12000, 'porcion', 3, 'DISPONIBLE'],
  ['PST003', 'Brownie con Helado', 'Brownie de chocolate con helado de vainilla', 18000, 'porcion', 3, 'DISPONIBLE'],
  ['BEB001', 'Jugo Natural de Maracuyá', 'Jugo fresco de maracuyá', 8000, 'vaso', 4, 'DISPONIBLE'],
  ['BEB002', 'Limonada de Coco', 'Limonada con leche de coco', 9000, 'vaso', 4, 'DISPONIBLE'],
  ['BEB003', 'Café Colombiano', 'Café de origen recién colado', 5000, 'taza', 4, 'DISPONIBLE'],
  ['BEB004', 'Agua Mineral', 'Botella de agua mineral 600 ml', 4000, 'botella', 4, 'DISPONIBLE'],
  ['ENS001', 'Ensalada César', 'Lechuga, crutones, parmesano y aderezo césar', 18000, 'porcion', 5, 'DISPONIBLE'],
  ['ENS002', 'Ensalada Mediterránea', 'Tomate, pepino, aceitunas y queso feta', 20000, 'porcion', 5, 'DISPONIBLE'],
  ['SOP001', 'Sopa de Verduras', 'Caldo de verduras frescas', 12000, 'porcion', 6, 'DISPONIBLE'],
  ['SOP002', 'Crema de Calabaza', 'Crema suave de calabaza', 14000, 'porcion', 6, 'DISPONIBLE'],
  ['PAN001', 'Pan de Bono', 'Pan de bono horneado con queso', 2500, 'unidad', 7, 'DISPONIBLE'],
  ['PAN002', 'Almojábana', 'Almojábana de cuajada', 2500, 'unidad', 7, 'AGOTADO'],
  ['REP001', 'Torta de Chocolate', 'Porción de torta de chocolate', 7000, 'porcion', 8, 'DISPONIBLE'],
  ['DES001', 'Desayuno Huilense', 'Huevos, arepa, chocolate y queso', 14000, 'porcion', 9, 'DISPONIBLE'],
  ['CR001', 'Hamburguesa Artesanal', 'Hamburguesa de res con papas', 22000, 'porcion', 10, 'DISPONIBLE'],
  ['CR002', 'Perro Caliente', 'Perro caliente tradicional', 12000, 'porcion', 10, 'INACTIVO']
];
k_db.productos.insertMany(k_productos.map((k_p, k_i) => ({
  id_producto: k_int(k_i + 1), codigo: k_p[0], nombre: k_p[1], descripcion: k_p[2], precio_venta: k_dinero(k_p[3]),
  unidad_venta: k_p[4], id_categoria: k_int(k_p[5]), estado: k_p[6]
})));

// 4. Insumos (algunos con stock bajo y otros próximos a vencer para probar RF07)
//    [nombre, unidad_medida, stock_actual, stock_minimo, costo_unitario, vence en N días (null = no vence), estado]
const k_insumos = [
  ['Pescado blanco fresco', 'kg', 15, 5, 25000, 3, 'ACTIVO'],
  ['Camarones medianos', 'kg', 8, 3, 45000, 2, 'ACTIVO'],
  ['Limones', 'unidad', 100, 20, 800, 10, 'ACTIVO'],
  ['Cebolla cabezona', 'kg', 20, 5, 3500, 15, 'ACTIVO'],
  ['Tomate', 'kg', 15, 5, 4000, 7, 'ACTIVO'],
  ['Plátano verde', 'kg', 30, 10, 2500, 10, 'ACTIVO'],
  ['Carne de res', 'kg', 25, 8, 35000, 4, 'ACTIVO'],
  ['Pollo entero', 'kg', 20, 6, 18000, 3, 'ACTIVO'],
  ['Arroz blanco', 'kg', 50, 15, 3500, 60, 'ACTIVO'],
  ['Frijoles rojos', 'kg', 20, 5, 8000, 90, 'ACTIVO'],
  ['Chorizo', 'kg', 10, 3, 28000, 10, 'ACTIVO'],
  ['Huevos', 'unidad', 120, 30, 600, 15, 'ACTIVO'],
  ['Aguacate hass', 'unidad', 40, 10, 3500, 5, 'ACTIVO'],
  ['Papa criolla', 'kg', 25, 8, 3000, 20, 'ACTIVO'],
  ['Salmón fresco', 'kg', 12, 4, 55000, 2, 'ACTIVO'],
  ['Vegetales mixtos', 'kg', 15, 5, 6000, 5, 'ACTIVO'],
  ['Leche condensada', 'l', 10, 3, 8000, 30, 'ACTIVO'],
  ['Leche evaporada', 'l', 10, 3, 6000, 30, 'ACTIVO'],
  ['Crema de leche', 'l', 8, 2, 7000, 10, 'ACTIVO'],
  ['Harina de trigo', 'kg', 20, 5, 3000, 60, 'ACTIVO'],
  ['Azúcar', 'kg', 15, 5, 4000, null, 'ACTIVO'],
  ['Chocolate en polvo', 'kg', 5, 2, 25000, 120, 'ACTIVO'],
  ['Helado de vainilla', 'l', 6, 2, 12000, 30, 'ACTIVO'],
  ['Maracuyá', 'kg', 8, 3, 12000, 7, 'ACTIVO'],
  ['Leche de coco', 'l', 5, 2, 15000, 15, 'ACTIVO'],
  ['Café en grano', 'kg', 5, 1, 45000, 60, 'ACTIVO'],
  ['Lechuga romana', 'kg', 8, 3, 5000, 4, 'ACTIVO'],
  ['Queso parmesano', 'kg', 3, 1, 40000, 20, 'ACTIVO'],
  ['Pepino', 'kg', 10, 3, 4000, 7, 'ACTIVO'],
  ['Queso feta', 'kg', 4, 1, 35000, 10, 'ACTIVO'],
  ['Aceitunas', 'kg', 3, 1, 25000, 30, 'ACTIVO'],
  ['Calabaza', 'kg', 12, 3, 3500, 15, 'ACTIVO'],
  ['Verduras surtidas', 'kg', 15, 5, 4500, 5, 'ACTIVO'],
  ['Cilantro', 'kg', 0.5, 2, 8000, 3, 'ACTIVO'],
  ['Perejil', 'kg', 0.3, 1, 7000, 2, 'ACTIVO'],
  ['Albahaca', 'kg', 0.2, 1, 9000, 1, 'ACTIVO'],
  ['Almidón de yuca', 'kg', 10, 3, 6000, 90, 'ACTIVO'],
  ['Queso costeño', 'kg', 6, 2, 22000, 1, 'ACTIVO'],
  ['Pan de hamburguesa', 'unidad', 3, 10, 1200, 0, 'ACTIVO'],
  ['Arepa', 'unidad', 60, 20, 700, 6, 'ACTIVO'],
  ['Chocolate de mesa', 'kg', 4, 1, 20000, 180, 'ACTIVO'],
  ['Agua mineral 600 ml', 'unidad', 48, 12, 1500, 365, 'ACTIVO']
];
k_db.insumos.insertMany(k_insumos.map((k_s, k_i) => ({
  id_insumo: k_int(k_i + 1), nombre: k_s[0], unidad_medida: k_s[1], stock_actual: k_dinero(k_s[2]),
  stock_minimo: k_dinero(k_s[3]), costo_unitario: k_dinero(k_s[4]), fecha_vencimiento: k_en_dias(k_s[5]),
  estado: k_s[6]
})));

// 5. Recetas (ficha técnica: cantidad de insumo por unidad de producto): [id_producto, id_insumo, cantidad]
const k_recetas = [
  [1, 1, 0.200], [1, 2, 0.100], [1, 3, 0.050], [1, 4, 0.050], [1, 34, 0.010],
  [2, 7, 0.150], [2, 4, 0.050], [2, 20, 0.200], [2, 35, 0.010],
  [3, 6, 0.300], [3, 4, 0.100], [3, 5, 0.100],
  [4, 9, 0.150], [4, 10, 0.150], [4, 7, 0.150], [4, 11, 0.080], [4, 12, 1.000], [4, 13, 0.500], [4, 6, 0.200],
  [5, 15, 0.200], [5, 16, 0.150], [5, 3, 0.020],
  [6, 8, 0.500], [6, 14, 0.200],
  [7, 7, 0.200], [7, 4, 0.100], [7, 5, 0.100], [7, 14, 0.150],
  [8, 17, 0.100], [8, 18, 0.100], [8, 19, 0.050], [8, 20, 0.100], [8, 21, 0.080], [8, 12, 3.000],
  [9, 17, 0.200], [9, 18, 0.200], [9, 12, 4.000], [9, 21, 0.100],
  [10, 20, 0.120], [10, 22, 0.050], [10, 21, 0.150], [10, 12, 2.000], [10, 23, 0.100],
  [11, 24, 0.100], [11, 21, 0.030],
  [12, 3, 2.000], [12, 25, 0.100], [12, 21, 0.020],
  [13, 26, 0.015],
  [14, 42, 1.000],
  [15, 27, 0.150], [15, 28, 0.020], [15, 20, 0.030],
  [16, 27, 0.100], [16, 29, 0.100], [16, 30, 0.050], [16, 31, 0.020],
  [17, 33, 0.200], [17, 4, 0.050], [17, 5, 0.050],
  [18, 32, 0.300], [18, 4, 0.050], [18, 19, 0.050],
  [19, 37, 0.040], [19, 38, 0.030], [19, 12, 0.200],
  [21, 20, 0.080], [21, 22, 0.030], [21, 12, 1.000],
  [22, 12, 2.000], [22, 40, 1.000], [22, 41, 0.030], [22, 38, 0.050],
  [23, 7, 0.150], [23, 39, 1.000], [23, 5, 0.050], [23, 14, 0.200]
];
k_db.recetas.insertMany(k_recetas.map((k_r, k_i) => ({
  id_receta: k_int(k_i + 1), id_producto: k_int(k_r[0]), id_insumo: k_int(k_r[1]), cantidad: k_cantidad(k_r[2])
})));

// 6. Proveedores: [nit, razon_social, telefono, correo, direccion, estado]
const k_proveedores = [
  ['900123456-1', 'Distribuidora Alimentos del Huila SAS', '3001234567', 'ventas@alimentoshuila.com', 'Calle 21 # 5-30, Neiva', 'ACTIVO'],
  ['900234567-2', 'Frigorífico Surcolombiano Ltda', '3102345678', 'pedidos@frigosur.com', 'Km 4 vía Palermo, Neiva', 'ACTIVO'],
  ['900345678-3', 'Lácteos La Montaña SA', '3203456789', 'comercial@lacteoslamontana.com', 'Vereda El Rosal, Pitalito', 'ACTIVO'],
  ['900456789-4', 'Frutas y Verduras El Campo SAS', '3154567890', 'ventas@frutaselcampo.com', 'Plaza Mercar, Neiva', 'ACTIVO'],
  ['900567890-5', 'Café Especial del Huila', '3185678901', 'ventas@cafehuila.com', 'Carrera 4 # 10-15, Garzón', 'ACTIVO'],
  ['900678901-6', 'Panificadora Central Ltda', '3126789012', 'pedidos@panificadora.com', 'Calle 8 # 15-20, Neiva', 'ACTIVO'],
  ['900789012-7', 'Carnes Premium del Llano', '3147890123', 'ventas@carnespremium.com', 'Vía Villavicencio Km 15', 'ACTIVO'],
  ['900890123-8', 'Mariscos del Pacífico SA', '3168901234', 'comercial@mariscospacifico.com', 'Puerto Bahía, Buenaventura', 'ACTIVO'],
  ['900901234-9', 'Abarrotes Don Pacho', '3179012345', 'donpacho@abarrotes.com', 'Carrera 2 # 3-40, Neiva', 'ACTIVO'],
  ['901012345-0', 'Bebidas y Refrescos del Sur', '3180123456', 'ventas@bebidassur.com', 'Zona Industrial, Neiva', 'ACTIVO']
];
k_db.proveedores.insertMany(k_proveedores.map((k_p, k_i) => ({
  id_proveedor: k_int(k_i + 1), nit: k_p[0], razon_social: k_p[1], telefono: k_p[2], correo: k_p[3],
  direccion: k_p[4], estado: k_p[5]
})));

// 7. Compras con su detalle embebido (subtotal = cantidad * costo_unitario; total = suma de subtotales)
//    [numero_factura, fecha_compra, id_proveedor, id_usuario, [[id_insumo, cantidad, costo_unitario], ...]]
const k_compras = [
  ['FV-1001', '2026-01-15T09:30:00', 8, 1, [[1, 10, 25000], [2, 5, 45000], [15, 2, 55000]]],
  ['FV-2001', '2026-02-20T10:15:00', 3, 1, [[17, 10, 8000], [18, 10, 6000], [19, 5, 7000], [38, 4, 22000]]],
  ['FV-3001', '2026-03-10T08:45:00', 2, 6, [[7, 15, 35000], [8, 10, 18000], [11, 8, 28000]]],
  ['FV-4001', '2026-04-05T11:20:00', 4, 1, [[3, 50, 800], [4, 15, 3500], [5, 10, 4000], [6, 20, 2500], [13, 20, 3500]]],
  ['FV-5001', '2026-05-12T14:30:00', 5, 1, [[26, 3, 45000]]],
  ['FV-6001', '2026-06-18T09:00:00', 6, 6, [[20, 10, 3000], [37, 5, 6000], [39, 30, 1200]]],
  ['FV-7001', '2026-07-22T10:30:00', 7, 1, [[7, 10, 35000]]],
  ['FV-8001', '2026-08-10T08:00:00', 1, 1, [[9, 30, 3500], [10, 15, 8000], [21, 10, 4000], [22, 2, 25000]]],
  ['FV-9001', '2026-09-05T07:40:00', 9, 6, [[12, 90, 600], [40, 60, 700], [41, 2, 20000]]],
  ['FV-1002', '2026-10-01T09:10:00', 10, 1, [[42, 48, 1500], [24, 5, 12000], [25, 3, 15000]]]
];
let k_id_detalle_compra = 0;
k_db.compras.insertMany(k_compras.map((k_c, k_i) => {
  const k_detalle = k_c[4].map((k_d) => ({
    id_detalle_compra: k_int(++k_id_detalle_compra), id_insumo: k_int(k_d[0]), cantidad: k_dinero(k_d[1]),
    costo_unitario: k_dinero(k_d[2]), subtotal: k_dinero(k_d[1] * k_d[2])
  }));
  const k_total = k_c[4].reduce((k_suma, k_d) => k_suma + k_d[1] * k_d[2], 0);
  return {
    id_compra: k_int(k_i + 1), numero_factura: k_c[0], fecha_compra: k_fecha(k_c[1]), id_proveedor: k_int(k_c[2]),
    id_usuario: k_int(k_c[3]), total: k_dinero(k_total), detalle: k_detalle
  };
}));

// 8. Clientes: [identificacion, nombres, apellidos, telefono, correo, tipo_cliente, estado]
const k_clientes = [
  ['1001234567', 'Andrés', 'Gómez Pérez', '3001112233', 'andres.gomez@email.com', 'APRENDIZ', 'ACTIVO'],
  ['1002345678', 'Carolina', 'Rodríguez López', '3102223344', 'caro.rodriguez@email.com', 'APRENDIZ', 'ACTIVO'],
  ['1003456789', 'Diego', 'Martínez Silva', '3203334455', 'diego.martinez@email.com', 'APRENDIZ', 'ACTIVO'],
  ['1004567890', 'Laura', 'Fernández Castro', '3154445566', 'laura.fernandez@email.com', 'INSTRUCTOR', 'ACTIVO'],
  ['1005678901', 'Jorge', 'Herrera Vargas', '3185556677', 'jorge.herrera@email.com', 'INSTRUCTOR', 'ACTIVO'],
  ['1006789012', 'Patricia', 'Morales Jiménez', '3126667788', 'patricia.morales@email.com', 'FUNCIONARIO', 'ACTIVO'],
  ['1007890123', 'Ricardo', 'Torres Méndez', '3147778899', 'ricardo.torres@email.com', 'FUNCIONARIO', 'ACTIVO'],
  ['1008901234', 'Sofía', 'Ramírez Ortiz', '3168889900', 'sofia.ramirez@email.com', 'EXTERNO', 'ACTIVO'],
  ['1009012345', 'Miguel', 'Vargas Ruiz', '3109990011', 'miguel.vargas@email.com', 'EXTERNO', 'ACTIVO'],
  ['1000123456', 'Elena', 'Castro Gómez', '3200001122', 'elena.castro@email.com', 'APRENDIZ', 'ACTIVO'],
  ['1001111111', 'Cliente', 'Inactivo', '3000000000', 'inactivo@email.com', 'EXTERNO', 'INACTIVO']
];
k_db.clientes.insertMany(k_clientes.map((k_c, k_i) => ({
  id_cliente: k_int(k_i + 1), identificacion: k_c[0], nombres: k_c[1], apellidos: k_c[2], telefono: k_c[3],
  correo: k_c[4], tipo_cliente: k_c[5], estado: k_c[6]
})));

// 9. Pedidos con su detalle embebido (RN01: subtotal = cantidad * precio_unitario; total = suma de subtotales)
//    [fecha_pedido, id_cliente, id_usuario, tipo_pedido, estado, observaciones, [[id_producto, cantidad, precio], ...]]
const k_pedidos = [
  ['2026-01-20T12:30:00', 1, 2, 'MESA', 'ENTREGADO', 'Mesa 5', [[1, 1, 25000], [4, 1, 35000], [11, 1, 8000], [13, 1, 5000]]],
  ['2026-02-14T19:45:00', 2, 2, 'PARA_LLEVAR', 'ENTREGADO', 'Empacar bien', [[5, 1, 42000], [8, 1, 15000], [12, 1, 9000]]],
  ['2026-03-08T13:15:00', 3, 4, 'MESA', 'ENTREGADO', 'Mesa 3 - aniversario', [[2, 2, 12000], [6, 2, 28000], [14, 2, 4000], [9, 1, 12000]]],
  ['2026-04-25T20:00:00', 4, 2, 'EVENTO', 'ENTREGADO', 'Evento de instructores', [[4, 5, 35000], [11, 5, 8000]]],
  ['2026-05-10T12:00:00', 5, 4, 'MESA', 'ENTREGADO', null, [[3, 2, 10000], [7, 1, 32000], [11, 1, 8000]]],
  ['2026-06-15T13:00:00', 6, 2, 'MESA', 'ENTREGADO', null, [[4, 1, 35000], [8, 1, 15000]]],
  ['2026-07-20T19:30:00', 7, 4, 'PARA_LLEVAR', 'ENTREGADO', null, [[6, 1, 28000], [3, 2, 10000], [10, 1, 18000], [14, 2, 4000]]],
  ['2026-08-10T12:00:00', 4, 2, 'MESA', 'ENTREGADO', 'Mesa 4', [[1, 1, 25000], [5, 1, 42000], [9, 1, 12000], [13, 1, 5000], [14, 1, 4000]]],
  ['2026-09-11T13:30:00', 5, 4, 'MESA', 'ENTREGADO', null, [[6, 1, 28000], [9, 1, 12000], [12, 1, 9000], [13, 1, 5000]]],
  ['2026-10-02T07:30:00', 10, 7, 'MESA', 'ENTREGADO', 'Desayuno', [[22, 1, 14000], [13, 1, 5000], [19, 2, 2500]]],
  ['2026-10-14T18:00:00', 2, 2, 'MESA', 'ANULADO', 'El cliente no se presentó', [[4, 1, 35000], [8, 1, 15000]]],
  ['2026-10-15T20:00:00', 3, 4, 'EVENTO', 'ANULADO', 'Evento cancelado por lluvia', [[7, 1, 32000], [11, 1, 8000], [13, 1, 5000]]],
  ['2026-10-20T11:30:00', 8, 2, 'MESA', 'PENDIENTE', 'Mesa 2', [[1, 1, 25000], [15, 1, 18000]]],
  ['2026-10-20T13:00:00', 9, 4, 'PARA_LLEVAR', 'PENDIENTE', null, [[10, 1, 18000], [12, 1, 9000], [13, 1, 5000]]],
  ['2026-10-20T14:00:00', 10, 2, 'MESA', 'EN_PREPARACION', 'Mesa 8 - urgente', [[4, 1, 35000], [3, 2, 10000], [8, 1, 15000]]],
  ['2026-10-20T14:30:00', 1, 4, 'PARA_LLEVAR', 'EN_PREPARACION', null, [[6, 1, 28000], [12, 1, 9000], [14, 1, 4000]]]
];
let k_id_detalle_pedido = 0;
k_db.pedidos.insertMany(k_pedidos.map((k_p, k_i) => {
  const k_detalle = k_p[6].map((k_d) => ({
    id_detalle: k_int(++k_id_detalle_pedido), id_producto: k_int(k_d[0]), cantidad: k_int(k_d[1]),
    precio_unitario: k_dinero(k_d[2]), subtotal: k_dinero(k_d[1] * k_d[2])
  }));
  const k_total = k_p[6].reduce((k_suma, k_d) => k_suma + k_d[1] * k_d[2], 0);
  return {
    id_pedido: k_int(k_i + 1), fecha_pedido: k_fecha(k_p[0]), id_cliente: k_int(k_p[1]), id_usuario: k_int(k_p[2]),
    tipo_pedido: k_p[3], estado: k_p[4], total: k_dinero(k_total), observaciones: k_p[5], detalle: k_detalle
  };
}));

// 10. Calificaciones de los pedidos ENTREGADOS
//     [id_pedido, id_cliente, fecha, calificacion_servicio, comentario, [[id_producto, nombre, calificacion], ...]]
const k_calificaciones = [
  [1, 1, '2026-01-20T12:30:00', 5, 'Excelente atención y buen sabor',
    [[1, 'Ceviche Mixto', 5], [4, 'Bandeja Paisa', 5], [11, 'Jugo Natural de Maracuyá', 4]]],
  [2, 2, '2026-02-14T19:45:00', 4, 'El salmón muy bueno, la limonada algo dulce',
    [[5, 'Salmón a la Plancha', 5], [12, 'Limonada de Coco', 3]]],
  [3, 3, '2026-03-08T13:15:00', 5, 'Todo delicioso',
    [[2, 'Empanadas de Carne', 4], [6, 'Pollo a la Brasa', 5], [9, 'Flan de Caramelo', 5]]],
  [4, 4, '2026-04-25T20:00:00', 4, 'Buen servicio para el evento',
    [[4, 'Bandeja Paisa', 4], [11, 'Jugo Natural de Maracuyá', 5]]],
  [5, 5, '2026-05-10T12:00:00', 3, 'Demoraron un poco',
    [[3, 'Patacones con Hogao', 4], [7, 'Lomo Saltado', 3]]],
  [6, 6, '2026-06-15T13:00:00', 5, null,
    [[4, 'Bandeja Paisa', 5], [8, 'Tres Leches', 5]]],
  [7, 7, '2026-07-20T19:30:00', 4, 'Muy rico el brownie',
    [[6, 'Pollo a la Brasa', 4], [10, 'Brownie con Helado', 5]]],
  [8, 4, '2026-08-10T12:00:00', 5, 'Volveremos',
    [[1, 'Ceviche Mixto', 4], [5, 'Salmón a la Plancha', 5], [9, 'Flan de Caramelo', 4]]],
  [9, 5, '2026-09-11T13:30:00', 4, null,
    [[6, 'Pollo a la Brasa', 4], [12, 'Limonada de Coco', 4]]],
  [10, 10, '2026-10-02T07:30:00', 5, 'El mejor desayuno del centro',
    [[22, 'Desayuno Huilense', 5], [19, 'Pan de Bono', 5]]]
];
k_db.calificaciones.insertMany(k_calificaciones.map((k_c) => ({
  id_pedido: k_int(k_c[0]), id_cliente: k_int(k_c[1]), fecha: k_c[2], calificacion_servicio: k_int(k_c[3]),
  comentario: k_c[4],
  productos: k_c[5].map((k_p) => ({ id_producto: k_int(k_p[0]), nombre: k_p[1], calificacion: k_int(k_p[2]) }))
})));

// 11. Contadores: último id usado en cada colección (la API continúa desde aquí)
k_db.contadores.insertMany([
  { _id: 'categorias', secuencia: k_int(k_categorias.length) },
  { _id: 'usuarios', secuencia: k_int(k_usuarios.length) },
  { _id: 'productos', secuencia: k_int(k_productos.length) },
  { _id: 'insumos', secuencia: k_int(k_insumos.length) },
  { _id: 'recetas', secuencia: k_int(k_recetas.length) },
  { _id: 'proveedores', secuencia: k_int(k_proveedores.length) },
  { _id: 'compras', secuencia: k_int(k_compras.length) },
  { _id: 'detalle_compra', secuencia: k_int(k_id_detalle_compra) },
  { _id: 'clientes', secuencia: k_int(k_clientes.length) },
  { _id: 'pedidos', secuencia: k_int(k_pedidos.length) },
  { _id: 'detalle_pedido', secuencia: k_int(k_id_detalle_pedido) }
]);

// Verificación
['usuarios', 'categorias', 'productos', 'insumos', 'recetas', 'proveedores', 'compras', 'clientes', 'pedidos',
  'calificaciones'].forEach((k_nombre) => print(k_nombre + ': ' + k_db.getCollection(k_nombre).countDocuments()));
