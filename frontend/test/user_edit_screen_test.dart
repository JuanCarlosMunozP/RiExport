import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:riexport_app/features/users/presentation/user_edit_screen.dart';

void main() {
  testWidgets('loads user data and submits only changed fields', (
    tester,
  ) async {
    Map<String, Object?>? submitted;
    await tester.pumpWidget(
      MaterialApp(
        home: UserEditScreen(
          user: _user,
          onSave: (changes) async => submitted = changes,
        ),
      ),
    );

    expect(find.text('Ana Pérez'), findsOneWidget);
    expect(find.text('ana@example.com'), findsOneWidget);
    await tester.enterText(find.byType(TextFormField).first, 'Ana María');
    await tester.ensureVisible(find.text('Guardar'));
    await tester.tap(find.text('Guardar'));
    await tester.pumpAndSettle();

    expect(submitted, {'first_name': 'Ana María'});
  });

  testWidgets('validates fields before calling the update endpoint', (
    tester,
  ) async {
    var calls = 0;
    await tester.pumpWidget(
      MaterialApp(
        home: UserEditScreen(user: _user, onSave: (_) async => calls++),
      ),
    );

    await tester.enterText(find.byType(TextFormField).at(2), 'invalid-email');
    await tester.ensureVisible(find.text('Guardar'));
    await tester.tap(find.text('Guardar'));
    await tester.pumpAndSettle();

    expect(find.text('Ingresa un correo válido.'), findsOneWidget);
    expect(calls, 0);
  });
}

final Map<String, dynamic> _user = {
  'id': 5,
  'first_name': 'Ana',
  'last_name': 'Pérez',
  'email': 'ana@example.com',
  'phone': null,
  'role_id': 3,
  'is_active': true,
};
