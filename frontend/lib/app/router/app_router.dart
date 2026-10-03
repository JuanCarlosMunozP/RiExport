import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import '../../core/api/api_client.dart';
import '../../features/auth/presentation/login_screen.dart';
import '../../features/auth/state/auth_session.dart';
import '../../features/roles/presentation/roles_screen.dart';
import '../../features/users/presentation/user_registration_screen.dart';
import '../../features/users/presentation/user_edit_screen.dart';
import '../../features/users/presentation/users_screen.dart';

abstract final class AppRoutes {
  static const home = '/';
  static const login = '/login';
  static const userRegistration = '/users/new';
  static const users = '/users';
  static const roles = '/roles';
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
      GoRoute(
        path: AppRoutes.userRegistration,
        name: 'user-registration',
        builder: (context, _) => UserRegistrationScreen(
          onRegister: (request) async {
            await context.read<ApiClient>().post('/users', body: request);
          },
        ),
      ),
      GoRoute(
        path: AppRoutes.users,
        name: 'users',
        builder: (context, _) => UsersScreen(
          deactivateUser: (userId) async {
            await context.read<ApiClient>().patch('/users/$userId/deactivate');
          },
          loadUsers: ({required limit, required offset, query, isActive}) {
            final parameters = <String, String>{
              'limit': '$limit',
              'offset': '$offset',
            };
            if (query != null) parameters['q'] = query;
            if (isActive != null) parameters['is_active'] = '$isActive';
            return context.read<ApiClient>().get(
              '/users',
              queryParameters: parameters,
            );
          },
        ),
      ),
      GoRoute(
        path: AppRoutes.roles,
        name: 'roles',
        builder: (context, _) => RolesScreen(
          loadRoles: () => context.read<ApiClient>().get(
            '/roles',
            queryParameters: const {'include_inactive': 'true'},
          ),
          loadPermissions: () =>
              context.read<ApiClient>().get('/roles/permissions'),
          createRole: (request) =>
              context.read<ApiClient>().post('/roles', body: request),
          updateRole: (roleId, changes) =>
              context.read<ApiClient>().patch('/roles/$roleId', body: changes),
          setRolePermissions: (roleId, permissionCodes) =>
              context.read<ApiClient>().put(
                '/roles/$roleId/permissions',
                body: {'permission_codes': permissionCodes},
              ),
          deactivateRole: (roleId) =>
              context.read<ApiClient>().patch('/roles/$roleId/deactivate'),
        ),
      ),
      GoRoute(
        path: '${AppRoutes.users}/:userId/edit',
        name: 'user-edit',
        builder: (context, state) {
          final userId = int.tryParse(state.pathParameters['userId'] ?? '');
          final extra = state.extra;
          if (userId == null || extra is! Map<String, dynamic>) {
            return const _RoutePlaceholder(
              title: 'Usuario no disponible',
              message: 'Abre la edición desde el listado de usuarios.',
            );
          }
          return UserEditScreen(
            user: extra,
            onSave: (changes) async {
              await context.read<ApiClient>().patch(
                '/users/$userId',
                body: changes,
              );
            },
          );
        },
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
    body: Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Text('Inicio'),
          const SizedBox(height: 20),
          FilledButton.icon(
            onPressed: () => context.go(AppRoutes.userRegistration),
            icon: const Icon(Icons.person_add_alt_1_rounded),
            label: const Text('Registrar usuario'),
          ),
          const SizedBox(height: 10),
          OutlinedButton.icon(
            onPressed: () => context.go(AppRoutes.users),
            icon: const Icon(Icons.manage_search_rounded),
            label: const Text('Consultar usuarios'),
          ),
          const SizedBox(height: 10),
          OutlinedButton.icon(
            onPressed: () => context.go(AppRoutes.roles),
            icon: const Icon(Icons.admin_panel_settings_outlined),
            label: const Text('Administrar roles y permisos'),
          ),
        ],
      ),
    ),
  );
}
