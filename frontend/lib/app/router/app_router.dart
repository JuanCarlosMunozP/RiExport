import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import '../../core/api/api_client.dart';
import '../../features/auth/presentation/login_screen.dart';
import '../../features/auth/state/auth_session.dart';

abstract final class AppRoutes {
  static const home = '/';
  static const login = '/login';
}

GoRouter createAppRouter({String initialLocation = AppRoutes.login}) {
  return GoRouter(
    initialLocation: initialLocation,
    routes: [
      GoRoute(
        path: AppRoutes.home,
        name: 'home',
        builder: (_, _) => const _RoutePlaceholder(title: 'Inicio'),
      ),
      GoRoute(
        path: AppRoutes.login,
        name: 'login',
        builder: (context, _) => LoginScreen(
          onLogin: (email, password) =>
              context.read<AuthSession>().authenticate(
                context.read<ApiClient>(),
                email: email,
                password: password,
              ),
        ),
      ),
    ],
    errorBuilder: (_, state) => _RoutePlaceholder(
      title: 'Página no encontrada',
      message: 'No existe la ruta ${state.uri.path}.',
    ),
  );
}

class _RoutePlaceholder extends StatelessWidget {
  const _RoutePlaceholder({required this.title, this.message});

  final String title;
  final String? message;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(title)),
      body: Center(child: Text(message ?? title)),
    );
  }
}
