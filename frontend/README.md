# RiExport Flutter

Cliente Flutter de RiExport para Android, iOS y Web. La estructura de `lib/` sigue la arquitectura modular descrita en la documentación del proyecto. Las features aún no contienen funcionalidad de negocio.

El estado compartido se gestiona con `provider` y `ChangeNotifier`; cada feature mantendrá sus propios notifiers/estados. Usa `setState` para estado efímero limitado a un widget. La preferencia de tema es el único estado global de ejemplo por ahora.

## Ejecutar

Desde `D:\riexport\frontend`:

```powershell
flutter pub get
.\run_web.ps1
```

El servidor web escucha siempre en `http://127.0.0.1:8080`. Si el puerto está ocupado, el proceso informa del conflicto en vez de cambiar automáticamente de puerto.

## Verificar

```powershell
flutter analyze
flutter test
```

`pubspec.lock` fija las dependencias Dart resueltas para esta aplicación.

## Cliente HTTP

`ApiClient` se inyecta con Provider y usa `package:http`. La URL base por defecto
es `http://127.0.0.1:8001/api/v1`; se puede reemplazar en compilación:

```powershell
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8001/api/v1
```

`10.0.2.2` corresponde al emulador Android para acceder al host. En un teléfono
físico se debe usar la dirección LAN del equipo que ejecuta el backend; en
despliegues se debe configurar una URL HTTPS. El cliente procesa el formato de
error del contrato (`error.code`, `message`, `details` y `request_id`), agrega
`X-Request-ID`, aplica un timeout y no expone el cuerpo crudo de errores HTTP.
El token se conecta mediante `tokenProvider`; la autenticación y persistencia
de credenciales aún no están implementadas.

## Navegación

La navegación declarativa con `go_router` está centralizada en
`lib/app/router/app_router.dart`. Las rutas iniciales son `/` (inicio) y
`/login` (marcador de posición); rutas desconocidas muestran una página 404.
El enrutador sincroniza la ubicación web con la URL y permite abrir rutas
directamente. Las pantallas de negocio se incorporarán al implementar cada
feature, sin definir rutas vacías por adelantado.
