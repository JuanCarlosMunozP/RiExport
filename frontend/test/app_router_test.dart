import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:riexport_app/app/router/app_router.dart';

void main() {
  testWidgets('resolves the initial location and unknown routes', (
    tester,
  ) async {
    final router = createAppRouter(initialLocation: '/not-defined');
    addTearDown(router.dispose);

    await tester.pumpWidget(MaterialApp.router(routerConfig: router));
    await tester.pumpAndSettle();

    expect(find.text('Página no encontrada'), findsOneWidget);
    expect(find.text('No existe la ruta /not-defined.'), findsOneWidget);
  });
}
