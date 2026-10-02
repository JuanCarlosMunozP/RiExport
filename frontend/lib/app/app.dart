import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../core/api/api_client.dart';
import '../core/config/api_config.dart';
import 'state/app_preferences.dart';

class RiExportApp extends StatelessWidget {
  const RiExportApp({super.key});

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
      child: const _RiExportView(),
    );
  }
}

class _RiExportView extends StatelessWidget {
  const _RiExportView();

  @override
  Widget build(BuildContext context) {
    return Consumer<AppPreferences>(
      builder: (context, preferences, _) => MaterialApp(
        title: 'RiExport',
        themeMode: preferences.themeMode,
        home: const Scaffold(body: SizedBox.shrink()),
      ),
    );
  }
}
