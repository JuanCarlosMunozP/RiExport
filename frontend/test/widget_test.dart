import 'package:flutter_test/flutter_test.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import 'package:riexport_app/app/app.dart';
import 'package:riexport_app/app/router/app_router.dart';
import 'package:riexport_app/app/state/app_preferences.dart';
import 'package:riexport_app/core/api/api_client.dart';

void main() {
  testWidgets('provides app preferences and updates the theme mode', (
    tester,
  ) async {
    await tester.pumpWidget(const RiExportApp());
    await tester.pumpAndSettle();

    var app = tester.widget<MaterialApp>(find.byType(MaterialApp));
    expect(app.themeMode, ThemeMode.system);

    final context = tester.element(find.byType(MaterialApp));
    expect(
      Provider.of<ApiClient>(context, listen: false).config.baseUri.toString(),
      'http://127.0.0.1:8001/api/v1',
    );
    expect(find.text('Bienvenido'), findsOneWidget);
    expect(find.text('Correo electrónico'), findsOneWidget);

    final scaffoldContext = tester.element(find.byType(Scaffold));
    GoRouter.of(scaffoldContext).go(AppRoutes.home);
    await tester.pumpAndSettle();
    expect(find.text('Inicio'), findsNWidgets(2));
    Provider.of<AppPreferences>(
      context,
      listen: false,
    ).setThemeMode(ThemeMode.dark);
    await tester.pump();

    app = tester.widget<MaterialApp>(find.byType(MaterialApp));
    expect(app.themeMode, ThemeMode.dark);
    await tester.pumpWidget(const SizedBox.shrink());
  });
}
