import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'state/app_preferences.dart';

class RiExportApp extends StatelessWidget {
  const RiExportApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (_) => AppPreferences(),
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
