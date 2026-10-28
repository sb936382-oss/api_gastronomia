# API REST Gastronomía CGDSS

Prototipo de API REST con **Python (FastAPI)** para la Unidad Productiva de Gastronomía del Centro de Gestión y
Desarrollo Sostenible Surcolombiano. Usa **una sola base de datos: MongoDB** (`bd_gastronomia`), con seguridad
**JWT** en todos los endpoints excepto el login.

> Convención del instructivo: archivos, clases, funciones, variables y routers llevan la inicial del aprendiz
> (**k**): `k_productos_router.py`, `KProductoService`, `k_obtener_producto()`, `k_db`…

## Requisitos

| Herramienta | Versión |
|---|---|
| Python | 3.11 o superior (también funciona con 3.10) |
| Docker Desktop | con Docker Compose |
| MongoDB | 7 (imagen `mongo:7`) |
| Clientes opcionales | MongoDB Compass o Studio 3T, Postman o Thunder Client |

## Instalación y ejecución

```bash
# 1. Variables de entorno (cambie las contraseñas de root y JWT_SECRET_KEY)
copy .env.example .env          # Windows  (Linux/Mac: cp .env.example .env)

# 2. Base de datos: crea MongoDB y ejecuta los scripts de database/ automáticamente
docker compose up -d

# 3. Entorno virtual y dependencias
python -m venv .venv
.venv\Scripts\activate          # Windows  (Linux/Mac: source .venv/bin/activate)
pip install -r requirements.txt

# 4. API
uvicorn app.k_main:k_app --reload
```

- API: http://localhost:8000/api/v1
- Documentación Swagger/OpenAPI: http://localhost:8000/docs (botón **Authorize** → pegue el token del login)

Los scripts de `database/` se ejecutan solos **la primera vez** que se crea el contenedor. Para volver a
crear la base desde cero: `docker compose down -v` y luego `docker compose up -d`.

> Si venía de la versión con MySQL, ejecute `docker compose down -v --remove-orphans` antes de `docker compose up -d`
> para borrar el contenedor de MySQL y crear la base `bd_gastronomia` nueva en MongoDB.

### Verificar la base de datos

```bash
docker exec -it k_mongo_gastronomia mongosh -u k_api_mongo -p --authenticationDatabase bd_gastronomia bd_gastronomia
#   show collections;  db.productos.find().limit(3);  db.pedidos.countDocuments();  db.contadores.find()
```

### Respaldo y restauración

```bash
docker exec k_mongo_gastronomia mongodump -u admin -p <password> --authenticationDatabase admin --db bd_gastronomia --archive > respaldo_mongo.archive
docker exec -i k_mongo_gastronomia mongorestore -u admin -p <password> --authenticationDatabase admin --archive < respaldo_mongo.archive
```

## Usuarios de prueba

Contraseña de todos: `Admin123*`

| Correo | Rol | Estado |
|---|---|---|
| admin@gastronomia.com | ADMIN | ACTIVO |
| cajero@gastronomia.com | CAJERO | ACTIVO |
| cocinero@gastronomia.com | COCINERO | ACTIVO |
| inactivo@gastronomia.com | CAJERO | INACTIVO (el login responde 401) |

## Estructura del proyecto

```
api_gastronomia/
├── app/
│   ├── k_main.py              # punto de entrada (FastAPI) y manejo global de errores
│   ├── core/                  # k_config.py (.env), k_security.py (JWT, bcrypt, roles), k_respuestas.py
│   ├── database/              # k_conexion_mongo.py (conexión, Decimal128 e ids enteros con contadores)
│   ├── models/                # k_enums.py (valores permitidos de rol, estado, unidad...)
│   ├── schemas/               # validaciones de entrada y salida (Pydantic)
│   ├── repositories/          # consultas a MongoDB (find, $inc, aggregate, $lookup)
│   ├── services/              # reglas de negocio RN01..RN06
│   └── routers/               # endpoints por recurso
├── database/
│   ├── 01_mongo_estructura.js # colecciones, índices únicos y usuario de la API
│   └── 02_mongo_datos_prueba.js
├── postman/k_api_gastronomia.postman_collection.json
├── docker-compose.yml         # MongoDB
├── requirements.txt
├── .env.example               # sin credenciales reales
└── README.md
```

## Endpoints (prefijo `/api/v1`)

Cada recurso tiene los cinco servicios `GET /recurso`, `GET /recurso/{id}`, `POST /recurso`, `PUT /recurso/{id}`
y `DELETE /recurso/{id}`.

| Recurso | Ruta base | Roles |
|---|---|---|
| Usuarios | `/usuarios` | ADMIN |
| Categorías | `/categorias` | ADMIN (consulta: todos) |
| Productos | `/productos` | ADMIN (consulta: todos) |
| Insumos | `/insumos` | ADMIN, COCINERO |
| Recetas | `/recetas` | ADMIN, COCINERO |
| Proveedores | `/proveedores` | ADMIN |
| Compras | `/compras` | ADMIN |
| Clientes | `/clientes` | ADMIN, CAJERO |
| Pedidos | `/pedidos` | ADMIN, CAJERO (cambio de estado: también COCINERO) |
| Calificaciones | `/calificaciones` | ADMIN, CAJERO |

Autenticación y consultas de negocio:

| Método | Endpoint | Descripción | Roles |
|---|---|---|---|
| POST | `/auth/login` | Inicia sesión y retorna el token JWT (**único endpoint público**) | — |
| POST | `/auth/registro` | Registra un usuario | ADMIN |
| GET | `/auth/perfil` | Datos del usuario autenticado | todos |
| GET | `/productos/categoria/{id_categoria}` | Productos de una categoría | todos |
| GET | `/productos/{id}/receta` | Insumos y cantidades de la receta | ADMIN, COCINERO |
| GET | `/productos/{id}/costo` | Costo de producción (Σ cantidad × costo_unitario) y margen | ADMIN, COCINERO |
| GET | `/insumos/stock-bajo` | Insumos con stock_actual <= stock_minimo | ADMIN, COCINERO |
| GET | `/insumos/por-vencer?dias=7` | Insumos que vencen en los próximos N días | ADMIN, COCINERO |
| GET | `/proveedores/{id}/compras` | Historial de compras a un proveedor | ADMIN |
| GET | `/clientes/{id}/pedidos` | Historial de pedidos de un cliente | ADMIN, CAJERO |
| GET | `/pedidos/estado/{estado}` | Pedidos filtrados por estado | ADMIN, CAJERO, COCINERO |
| PATCH | `/pedidos/{id}/estado` | Cambia el estado del pedido (aplica RN03 y RN05) | ADMIN, CAJERO, COCINERO |
| GET | `/reportes/ventas?desde=&hasta=` | Total vendido y número de pedidos ENTREGADOS en el rango | ADMIN |
| GET | `/reportes/productos-mas-vendidos?limite=10` | Ranking de productos más vendidos | ADMIN |
| GET | `/calificaciones/producto/{id_producto}` | Calificaciones y promedio de un producto (agregación MongoDB) | ADMIN, CAJERO |

Decisiones de diseño:
- Todo está en MongoDB. Cada documento conserva su id entero (`id_producto`, `id_pedido`...) para que los endpoints
  sigan iguales; la colección `contadores` guarda el último id de cada colección. Las calificaciones usan el `_id`
  (ObjectId) como antes.
- El detalle de compras y pedidos va **embebido** en el documento de la compra o del pedido.
- Precios, cantidades y stock se guardan como `Decimal128` para no perder centavos.
- `DELETE /pedidos/{id}` **anula** el pedido (estado ANULADO) para conservar el historial de ventas.
- `DELETE /compras/{id}` descuenta del inventario lo que había ingresado la compra (409 si el stock quedaría negativo).
- El COCINERO puede consultar `/pedidos/estado/{estado}` para ver los pedidos por preparar, ya que es quien cambia su estado.

## Reglas de negocio

| Regla | Implementación |
|---|---|
| RN01 | El pedido solo recibe `id_producto` y `cantidad`; la API toma el precio actual del producto, calcula `subtotal = cantidad * precio_unitario` y el total. |
| RN02 | Al registrar una compra se suma la cantidad al `stock_actual` y se actualiza el `costo_unitario` de cada insumo (primero se valida todo y luego se aplica con `$inc`). |
| RN03 | Al pasar un pedido a ENTREGADO se descuentan los insumos según la receta; si no alcanza responde **409** y no descuenta nada. |
| RN04 | Producto, insumo, cliente o proveedor con movimientos no se borra: pasa a INACTIVO (la respuesta indica `"borrado_logico": true`). |
| RN05 | Un pedido ENTREGADO o ANULADO no se puede modificar, cambiar de estado ni anular (**409**). |
| RN06 | Contraseñas cifradas con bcrypt; ninguna respuesta incluye el campo `password`. |

## Seguridad

- Token en el encabezado `Authorization: Bearer <token>`, con expiración (`JWT_EXPIRE_MINUTES`).
- **401** si no hay token, es inválido, expiró o el usuario está INACTIVO; **403** si el rol no tiene permiso.
- Credenciales y clave JWT en `.env` (incluido en `.gitignore`); en el repositorio solo va `.env.example`.
- La API se conecta a MongoDB con `k_api_mongo` (rol `readWrite` solo en `bd_gastronomia`), nunca con root.
- Códigos de error: 400 (regla de negocio), 401, 403, 404, 409 (duplicado, estado o inventario), 422 (validación
  de datos), 500 (error interno, sin exponer detalles).

## Pruebas con Postman

Importe `postman/k_api_gastronomia.postman_collection.json` y ejecute **Run collection**. La primera carpeta
inicia sesión con ADMIN, CAJERO y COCINERO y guarda los tokens en variables. La colección prueba los 65
endpoints (136 peticiones), incluidos los casos 401, 403, 404, 409, 422 y cada regla de negocio.
