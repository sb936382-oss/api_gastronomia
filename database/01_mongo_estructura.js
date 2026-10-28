// =====================================================================
// 01_mongo_estructura.js
// MongoDB 7 - Base de datos única bd_gastronomia (Unidad Productiva de Gastronomía, CGDSS)
// Crea las colecciones, los índices únicos (equivalen a los UNIQUE de SQL) y el usuario de la API.
// Se ejecuta automáticamente con docker compose (docker-entrypoint-initdb.d)
// o manualmente:  mongosh -u admin -p --authenticationDatabase admin database/01_mongo_estructura.js
// =====================================================================
const k_db = db.getSiblingDB('bd_gastronomia');

// Cada documento tiene un id entero (id_usuario, id_producto...) además del _id de MongoDB.
// La colección contadores guarda el último id usado por cada colección (la API lo incrementa con $inc).
k_db.createCollection('contadores');

k_db.createCollection('usuarios');
k_db.usuarios.createIndex({ id_usuario: 1 }, { unique: true, name: 'uq_usuarios_id' });
k_db.usuarios.createIndex({ identificacion: 1 }, { unique: true, name: 'uq_usuarios_identificacion' });
k_db.usuarios.createIndex({ correo: 1 }, { unique: true, name: 'uq_usuarios_correo' });

k_db.createCollection('categorias');
k_db.categorias.createIndex({ id_categoria: 1 }, { unique: true, name: 'uq_categorias_id' });
k_db.categorias.createIndex({ nombre: 1 }, { unique: true, name: 'uq_categorias_nombre' });

k_db.createCollection('productos');
k_db.productos.createIndex({ id_producto: 1 }, { unique: true, name: 'uq_productos_id' });
k_db.productos.createIndex({ codigo: 1 }, { unique: true, name: 'uq_productos_codigo' });
k_db.productos.createIndex({ id_categoria: 1 }, { name: 'idx_productos_categoria' });

k_db.createCollection('insumos');
k_db.insumos.createIndex({ id_insumo: 1 }, { unique: true, name: 'uq_insumos_id' });
k_db.insumos.createIndex({ nombre: 1 }, { unique: true, name: 'uq_insumos_nombre' });
k_db.insumos.createIndex({ fecha_vencimiento: 1 }, { name: 'idx_insumos_venc' });

// Ficha técnica: relación N:M entre productos e insumos
k_db.createCollection('recetas');
k_db.recetas.createIndex({ id_receta: 1 }, { unique: true, name: 'uq_recetas_id' });
k_db.recetas.createIndex({ id_producto: 1, id_insumo: 1 }, { unique: true, name: 'uq_recetas_producto_insumo' });
k_db.recetas.createIndex({ id_insumo: 1 }, { name: 'idx_recetas_insumo' });

k_db.createCollection('proveedores');
k_db.proveedores.createIndex({ id_proveedor: 1 }, { unique: true, name: 'uq_proveedores_id' });
k_db.proveedores.createIndex({ nit: 1 }, { unique: true, name: 'uq_proveedores_nit' });

// Compras: el detalle va embebido dentro de cada compra
k_db.createCollection('compras');
k_db.compras.createIndex({ id_compra: 1 }, { unique: true, name: 'uq_compras_id' });
k_db.compras.createIndex({ id_proveedor: 1, numero_factura: 1 }, { unique: true, name: 'uq_compras_factura_proveedor' });
k_db.compras.createIndex({ 'detalle.id_insumo': 1 }, { name: 'idx_compras_insumo' });

k_db.createCollection('clientes');
k_db.clientes.createIndex({ id_cliente: 1 }, { unique: true, name: 'uq_clientes_id' });
k_db.clientes.createIndex({ identificacion: 1 }, { unique: true, name: 'uq_clientes_identificacion' });

// Pedidos: el detalle va embebido dentro de cada pedido
k_db.createCollection('pedidos');
k_db.pedidos.createIndex({ id_pedido: 1 }, { unique: true, name: 'uq_pedidos_id' });
k_db.pedidos.createIndex({ estado: 1 }, { name: 'idx_pedidos_estado' });
k_db.pedidos.createIndex({ fecha_pedido: 1 }, { name: 'idx_pedidos_fecha' });
k_db.pedidos.createIndex({ id_cliente: 1 }, { name: 'idx_pedidos_cliente' });
k_db.pedidos.createIndex({ 'detalle.id_producto': 1 }, { name: 'idx_pedidos_producto' });

// Calificaciones con validación $jsonSchema (estructura del documento de calificación)
k_db.createCollection('calificaciones', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['id_pedido', 'id_cliente', 'fecha', 'calificacion_servicio', 'productos'],
      properties: {
        id_pedido: { bsonType: 'int', minimum: 1, description: 'id_pedido de la colección pedidos' },
        id_cliente: { bsonType: 'int', minimum: 1, description: 'id_cliente de la colección clientes' },
        fecha: { bsonType: 'string', description: 'Fecha ISO 8601, hora de Bogotá' },
        calificacion_servicio: { bsonType: 'int', minimum: 1, maximum: 5 },
        comentario: { bsonType: ['string', 'null'], maxLength: 500 },
        productos: {
          bsonType: 'array',
          minItems: 1,
          items: {
            bsonType: 'object',
            required: ['id_producto', 'nombre', 'calificacion'],
            properties: {
              id_producto: { bsonType: 'int', minimum: 1 },
              nombre: { bsonType: 'string' },
              calificacion: { bsonType: 'int', minimum: 1, maximum: 5 }
            }
          }
        }
      }
    }
  },
  validationLevel: 'strict',
  validationAction: 'error'
});
// Una calificación por pedido y búsqueda rápida por producto
k_db.calificaciones.createIndex({ id_pedido: 1 }, { unique: true, name: 'uq_calificaciones_pedido' });
k_db.calificaciones.createIndex({ 'productos.id_producto': 1 }, { name: 'idx_calificaciones_producto' });

// Usuario de la API con privilegios mínimos (solo lectura/escritura en esta base de datos, nunca root)
// La contraseña debe coincidir con la de MONGO_URI en el archivo .env
k_db.createUser({
  user: 'k_api_mongo',
  pwd: 'MongoApi_2026',
  roles: [{ role: 'readWrite', db: 'bd_gastronomia' }]
});

print('Base de datos bd_gastronomia creada con ' + k_db.getCollectionNames().length + ' colecciones');
