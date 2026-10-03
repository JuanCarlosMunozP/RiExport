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
        builder: (context, _) => _HomePlaceholder(
          onLogout: () => context.read<AuthSession>().clear(),
        ),
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

class _HomePlaceholder extends StatefulWidget {
  const _HomePlaceholder({required this.onLogout});

  final Future<bool> Function() onLogout;

  @override
  State<_HomePlaceholder> createState() => _HomePlaceholderState();
}

class _HomePlaceholderState extends State<_HomePlaceholder> {
  bool _isSigningOut = false;

  Future<void> _signOut() async {
    setState(() => _isSigningOut = true);
    final messenger = ScaffoldMessenger.of(context);
    var tokenRemoved = false;
    try {
      tokenRemoved = await widget.onLogout();
    } finally {
      if (mounted) context.go(AppRoutes.login);
    }
    if (!tokenRemoved) {
      messenger.showSnackBar(
        const SnackBar(
          content: Text(
            'La sesión se cerró, pero no se pudo borrar el token guardado.',
          ),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(
      title: const Text('Inicio'),
      actions: [
        IconButton(
          tooltip: 'Cerrar sesión',
          onPressed: _isSigningOut ? null : _signOut,
          icon: _isSigningOut
              ? const SizedBox.square(
                  dimension: 20,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              : const Icon(Icons.logout_rounded),
        ),
        const SizedBox(width: 8),
      ],
    ),
    body: const Center(child: Text('Inicio')),
  );
}
