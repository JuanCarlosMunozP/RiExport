# RiExport Flutter

Cliente Flutter de RiExport para Android, iOS y Web. La estructura de `lib/` sigue la arquitectura modular descrita en la documentación del proyecto. Las features aún no contienen funcionalidad de negocio.

El estado compartido se gestiona con `provider` y `ChangeNotifier`; cada feature mantendrá sus propios notifiers/estados. Usa `setState` para estado efímero limitado a un widget. La sesión se restaura al iniciar y conserva solo el token de acceso en almacenamiento seguro del dispositivo.

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
El token se conecta mediante `tokenProvider`. La app guarda el JWT de acceso
con `flutter_secure_storage` (Keychain en Apple, almacenamiento cifrado en
Android y Web Crypto en navegador), lo restaura al iniciar y elimina los tokens
vencidos. No se guardan contraseñas. En Web, el almacenamiento seguro requiere
HTTPS o `localhost`; no publiques la app en HTTP sin TLS.
Al cerrar sesión se elimina el JWT local y se vuelve a `/login`. El contrato
actual no define revocación de JWT en el servidor; el token deja de enviarse
desde este dispositivo, y el backend conserva la validación de expiración.

## Navegación

La navegación declarativa con `go_router` está centralizada en
`lib/app/router/app_router.dart`. Una sesión restaurada abre `/` y una sesión
ausente o vencida abre `/login`; rutas desconocidas muestran una página 404.
El enrutador sincroniza la ubicación web con la URL y permite abrir rutas
directamente. Las pantallas de negocio se incorporarán al implementar cada
feature, sin definir rutas vacías por adelantado.
