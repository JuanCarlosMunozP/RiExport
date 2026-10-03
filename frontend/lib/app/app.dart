import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';

import '../core/api/api_client.dart';
import '../core/config/api_config.dart';
import 'router/app_router.dart';
import 'state/app_preferences.dart';

class RiExportApp extends StatefulWidget {
  const RiExportApp({super.key});

  @override
  State<RiExportApp> createState() => _RiExportAppState();
}

class _RiExportAppState extends State<RiExportApp> {
  late final GoRouter _router = createAppRouter();

  @override
  void dispose() {
    _router.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        Provider<ApiClient>(
          create: (_) => ApiClient(config: ApiConfig()),
          dispose: (_, client) => client.close(),
        ),
        ChangeNotifierProvider(create: (_) => AppPreferences()),
      ],
      child: _RiExportView(router: _router),
    );
  }
}

class _RiExportView extends StatelessWidget {
  const _RiExportView({required this.router});

  final GoRouter router;

  @override
  Widget build(BuildContext context) {
    return Consumer<AppPreferences>(
      builder: (context, preferences, _) => MaterialApp.router(
        title: 'RiExport',
        themeMode: preferences.themeMode,
        routerConfig: router,
      ),
    );
  }
}
