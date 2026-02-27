# Desarrollo web en entorno servidor | Grupo 8: Andrés Cárdenas, Andrés Rivero, Alejandra Herrera-Picazo

# RoomRaid: Coworking Scheduler

Nuestro proyecto final consiste en desarrollar una plataforma web en Django para gestionar la reserva de salas en un coworking, con administración de espacios, franjas horarias y tarifas, y un sistema de reservas que valida disponibilidad. 
Funcionalidades principales y grupos de usuarios.

La aplicación está pensada para dos tipos de usuarios:
- Administrador: gestiona los espacios (salas) y sus características, así como las tarifas aplicables a las reservas. Valida la disponibilidad por franja horaria y puede crear reservas para los clientes. También puede consultar la ocupación diaria (en formato calendario o lista) y acceder a estadísticas detalladas sobre el uso de los espacios, número de reservas, horas reservadas, ingresos, etc.

- Cliente: puede crear reservas en los espacios disponibles y consultar la ocupación. Su acceso está limitado a las funciones necesarias para gestionar sus propias reservas.

## Ejecución y despliegue con Docker
La plataforma funciona mediante Docker Compose y utiliza PostgreSQL como base de datos.

#### 1. Configuración inicial
Primero se configuraron los archivos Dockerfile y docker-compose.yml partiendo de las variables de entorno definidas en el archivo .env

#### 2. Instalación de Docker
Windows: Instalar desde la página oficial de Docker.
Linux: Puedes instalarlo desde terminal con: pip install docker

#### 3. Dependencias del proyecto
En el archivo requirements.txt se añadió: psycopg2-binary==2.9.11
Este paquete permite usar PostgreSQL como base de datos dentro de Docker.

#### 4. Migraciones de base de datos
Antes de levantar el servidor, ejecuta las migraciones:
docker-compose exec web python manage.py migrate

#### 5. Arranque del servidor
Para iniciar la aplicación:
Windows: docker compose up - -build
Linux: docker-compose up - -build
Una vez activo, la aplicación estará disponible en:[ http://localhost:8000](http://localhost:8000/)

#### 6. Apagar el servidor
Windows: docker compose down
Linux: docker-compose down

NOTA: recuerda ejecutar todos los comandos dentro de tu entorno virtual.

## Credenciales de pruebas
El proyecto ya tiene creados dos perfiles de prueba al ejecutar la aplicación, uno de administrador y otro de cliente. Sus respectivos datos:

#### Superuser (Administrador)
email: [admin@admin.com](mailto:admin@admin.com) |
user: admin |
password: admin

#### Usuario (Cliente)
email: [usuario@usuario.com](mailto:usuario@usuario.com) |
user: usuario |
password: usuario

IMPORTANTE PARA USER! Los usuarios se registran con un email obligatorio, y se inician sesión con el email y la contraseña.

PARA CREAR UN SUPERADMIN:
Una vez abierto Docker y levantado el servidor con docker compose up –build, creamos un super usuario con el comando:
docker-compose exec web python manage.py migrate

## Flujo de trabajo (Workflow) del proyecto
Cuando se nos mandó el trabajo, nuestro equipo se reunió para organizar todo y repartir las tareas de cada uno. Desde el principio decidimos usar GitHub como herramienta principal, ya que era lo más cómodo para mantener el control, trabajar en equipo y evitar conflictos de código.

Cada avance se subía mediante Pull Requests, configuradas para que otro miembro del grupo tuviera que revisarlas antes de mergear. Así nos asegurábamos de que todo funcionara bien y no se pisara el trabajo de nadie.
En esa primera reunión también acordamos seguir los roles propuestos por el profesor, con algunos cambios que especificamos a continuación:

### Andrés Cárdenas 
Rol 1
- Relaciones
- Modelos bookings
- Templates y CSS
- Configuración inicial login y logout
- Validaciones simples en modelos
- Gestión de migraciones
- Consultas ORM
- Documentación en modelos necesaria requirements.txt.

#### Andrés Rivero - Rol 2
- Forms
- Admin
- Accounts (Model User, Forms, Admin, Urls, Views)
- Signals
- Mixins
- Middleware

#### Alejandra Herrera-Picazo - Rol 3
- CRUD (CBV)
- FBV
- Cookies y Sessions
- Dockerización y variables de entorno
- PostgresSQL
- Documentación del proyecto

Creamos la base del proyecto con todos los archivos necesarios y configuramos el repositorio compartido. Cada miembro trabajó desde su rama o feature correspondiente a su parte, manteniendo siempre el orden y evitando pisar el trabajo del otro.
Durante todo el desarrollo hubo comunicación continua: hablábamos por mensajes, llamadas o directamente desde GitHub. Además de los commits y PRs, llevamos un documento de logs diarios donde apuntábamos lo que hacía cada uno con su fecha, para tener un seguimiento más visual de los avances.

También usamos las issues de GitHub para reportar errores, comentar mejoras o pedir ayuda a otros compañeros.
En resumen, el flujo de trabajo fue muy limpio y fácil de seguir gracias a la buena comunicación, organización y colaboración del equipo desde el primer día.

## Flujo de cookies y sesiones
La cookie que hemos decidido implementar guarda el tema claro/oscuro de la página.

Al entrar en la plataforma sin estar registrado o sin haber iniciado sesión, la página tiene una cookie por defecto. Cuando creas un usuario o este se registra o inicia sesión, el modelo profile, el cual se crea automáticamente, tiene una variable “preferencia” que está sincronizada con la cookie por defecto. El usuario puede cambiar esta preferencia desde su perfil con un select o desde la página principal mediante un botón que cambia la cookie.

La sesión que hemos decidido implementar se aplica a occupancy.

Nuestra sesión se escribe cuando el usuario escribe una fecha y la envía mediante un GET. Esta se guarda mediante request.session[“occ_fecha”], que se encuentra en nuestra view. Cuando el usuario vuelve a la vista, esta recupera automáticamente la fecha almacenada previamente y la muestra. 

## Plan de Hitos y Cronología de Desarrollo
### Fase 1 — Base operativa
Periodo: 18/02/2026 – 21/02/2026
Objetivo: Establecer la estructura base del proyecto y preparar el entorno de trabajo.

Tareas principales:
- Creación de estructura de proyecto RoomRaid (inicio: 18/02).
- Repartición de roles y responsabilidades del equipo.
- Definición y creación de modelos principales: Space, TimeSlot, Rate, Booking.
- Integración de forms y admin iniciales para todos los modelos.
- Implementación de usuario personalizado (User, Profile, sus forms y admins) .
- Estructura completa de templates (base.html, form.html, accounts/*.html).
- Creación inicial de requirements.txt, activación de login/logout en settings y urls.py

### Fase 2 — Reservas completas y control de acceso
Periodo: 22/02/2026 – 25/02/2026
Objetivo: Implementar el flujo central de reservas, control de usuarios y CRUD completo.

Tareas principales:
- CRUDs de Space y TimeSlot
- Implementación del flujo de cancelación de reservas
- Desarrollo de vistas de autenticación (register, login, logout, profile) y sincronización Profile–User
- Refactorización de forms, validaciones adicionales y corrección de clean() en modelos
- Creación de servicio services.py con consultas ORM y primer uso de expresiones F
- Terminación del CRUD completo y permisos de administrador
- Integración de mixins personalizados: AdminOnlyMixin y OwnerOrAdminBookingMixin
- Validaciones de disponibilidad y lógica avanzada en BookingForm
- Mejoras de estilo, responsive y cookies de tema en base.html

## Fase 3 — Estadísticas, optimización y middleware
Periodo: 24/02/2026 – 26/02/2026
Objetivo: Añadir analítica, rendimiento y trazabilidad del sistema.

Tareas principales:
- Implementación de UIPreferenceMiddleware y BookingAuditMiddleware 
- Consultas agregadas con annotate, aggregate, select_related, prefetch_related
- Creación de vistas dashboard y occupancy con estadísticas
- Refactorización de consultas ORM y filtros de reservas
- Integración de Dockerfile y docker-compose.yml
- Mejora del dashboard: ingresos totales, métricas dinámicas y formularios de filtrado
- Documentación del middleware, estilos finales y ajustes de vistas y templates.

## Mapa de trazabilidad

https://docs.google.com/document/d/17hIXebafUvYpp1KzDRtjkhEJkoeTLzJPVuqAMN8WTUk/edit?tab=t.0#heading=h.jgjo4nbgxyjq