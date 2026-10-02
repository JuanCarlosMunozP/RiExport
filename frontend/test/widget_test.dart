import 'package:flutter_test/flutter_test.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:riexport_app/app/app.dart';
import 'package:riexport_app/app/state/app_preferences.dart';

void main() {
  testWidgets('provides app preferences and updates the theme mode', (
    tester,
  ) async {
    await tester.pumpWidget(const RiExportApp());

    var app = tester.widget<MaterialApp>(find.byType(MaterialApp));
    expect(app.themeMode, ThemeMode.system);

    final context = tester.element(find.byType(MaterialApp));
    Provider.of<AppPreferences>(
      context,
      listen: false,
    ).setThemeMode(ThemeMode.dark);
    await tester.pump();

    app = tester.widget<MaterialApp>(find.byType(MaterialApp));
    expect(app.themeMode, ThemeMode.dark);
  });
}
