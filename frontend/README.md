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
