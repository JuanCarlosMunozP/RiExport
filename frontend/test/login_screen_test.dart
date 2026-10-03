import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:riexport_app/core/api/api_exception.dart';
import 'package:riexport_app/features/auth/presentation/login_screen.dart';

void main() {
  testWidgets('validates required login fields without submitting', (
    tester,
  ) async {
    var submitted = false;
    await tester.pumpWidget(
      MaterialApp(home: LoginScreen(onLogin: (_, _) async => submitted = true)),
    );

    await tester.tap(find.text('Iniciar sesión'));
    await tester.pump();

    expect(find.text('Ingresa tu correo electrónico.'), findsOneWidget);
    expect(find.text('Ingresa tu contraseña.'), findsOneWidget);
    expect(submitted, isFalse);
  });

  testWidgets('toggles password visibility and displays API errors', (
    tester,
  ) async {
    await tester.pumpWidget(
      MaterialApp(
        home: LoginScreen(
          onLogin: (_, _) async {
            throw const ApiException(
              statusCode: 401,
              code: 'UNAUTHORIZED',
              message: 'Credenciales incorrectas.',
            );
          },
        ),
      ),
    );

    final passwordField = find.byType(TextFormField).last;
    final editablePassword = find.descendant(
      of: passwordField,
      matching: find.byType(EditableText),
    );
    expect(tester.widget<EditableText>(editablePassword).obscureText, isTrue);
    await tester.tap(find.byTooltip('Mostrar contraseña'));
    await tester.pump();
    expect(tester.widget<EditableText>(editablePassword).obscureText, isFalse);

    await tester.enterText(
      find.byType(TextFormField).first,
      'user@example.com',
    );
    await tester.enterText(passwordField, 'wrong-password');
    await tester.tap(find.text('Iniciar sesión'));
    await tester.pumpAndSettle();

    expect(find.text('Credenciales incorrectas.'), findsOneWidget);
  });
}
