import 'package:flutter/material.dart';

import '../../../core/api/api_exception.dart';

Future<bool> showUserEditDialog(
  BuildContext context, {
  required Map<String, dynamic> user,
  required Future<void> Function(Map<String, Object?> changes) onSave,
}) async =>
    await showDialog<bool>(
      context: context,
      builder: (_) => _UserEditDialog(user: user, onSave: onSave),
    ) ??
    false;

class _UserEditDialog extends StatefulWidget {
  const _UserEditDialog({required this.user, required this.onSave});

  final Map<String, dynamic> user;
  final Future<void> Function(Map<String, Object?> changes) onSave;

  @override
  State<_UserEditDialog> createState() => _UserEditDialogState();
}

class _UserEditDialogState extends State<_UserEditDialog> {
  final _formKey = GlobalKey<FormState>();
  late final _firstName = TextEditingController(
    text: '${widget.user['first_name'] ?? ''}',
  );
  late final _lastName = TextEditingController(
    text: '${widget.user['last_name'] ?? ''}',
  );
  late final _email = TextEditingController(
    text: '${widget.user['email'] ?? ''}',
  );
  late final _phone = TextEditingController(
    text: '${widget.user['phone'] ?? ''}',
  );
  late final _roleId = TextEditingController(
    text: '${widget.user['role_id'] ?? ''}',
  );
  bool _saving = false;
  String? _error;

  @override
  void dispose() {
    _firstName.dispose();
    _lastName.dispose();
    _email.dispose();
    _phone.dispose();
    _roleId.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    final changes =
        <String, Object?>{
          'first_name': _firstName.text.trim(),
          'last_name': _lastName.text.trim(),
          'email': _email.text.trim(),
          'phone': _phone.text.trim().isEmpty ? null : _phone.text.trim(),
          'role_id': int.parse(_roleId.text),
        }..removeWhere(
          (key, value) =>
              value == widget.user[key] ||
              (key == 'phone' && value == (widget.user[key] ?? '')),
        );
    if (changes.isEmpty) {
      Navigator.pop(context, false);
      return;
    }

    setState(() {
      _saving = true;
      _error = null;
    });
    try {
      await widget.onSave(changes);
      if (mounted) Navigator.pop(context, true);
    } on ApiException catch (exception) {
      if (mounted) {
        setState(() {
          _error = exception.message;
          _saving = false;
        });
      }
    } catch (_) {
      if (mounted) {
        setState(() {
          _error = 'No fue posible guardar los cambios.';
          _saving = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) => AlertDialog(
    title: const Text('Editar usuario'),
    content: SizedBox(
      width: 440,
      child: Form(
        key: _formKey,
        child: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              _editField(_firstName, 'Nombres', required: true),
              const SizedBox(height: 12),
              _editField(_lastName, 'Apellidos', required: true),
              const SizedBox(height: 12),
              _editField(_email, 'Correo electrónico', required: true),
              const SizedBox(height: 12),
              _editField(_phone, 'Teléfono'),
              const SizedBox(height: 12),
              _editField(_roleId, 'ID del rol', required: true, numeric: true),
              if (_error != null) ...[
                const SizedBox(height: 12),
                Text(_error!, style: const TextStyle(color: Color(0xFF84382C))),
              ],
            ],
          ),
        ),
      ),
    ),
    actions: [
      TextButton(
        onPressed: _saving ? null : () => Navigator.pop(context, false),
        child: const Text('Cancelar'),
      ),
      FilledButton(
        onPressed: _saving ? null : _submit,
        child: Text(_saving ? 'Guardando…' : 'Guardar'),
      ),
    ],
  );
}

Widget _editField(
  TextEditingController controller,
  String label, {
  bool required = false,
  bool numeric = false,
}) => TextFormField(
  controller: controller,
  keyboardType: numeric ? TextInputType.number : TextInputType.text,
  decoration: InputDecoration(labelText: label),
  validator: (value) {
    final text = value?.trim() ?? '';
    if (required && text.isEmpty) return 'Este campo es obligatorio.';
    if (numeric && int.tryParse(text) == null) return 'Ingresa un ID válido.';
    if (label == 'Correo electrónico' &&
        !RegExp(r'^[^\s@]+@[^\s@]+\.[^\s@]+$').hasMatch(text)) {
      return 'Ingresa un correo válido.';
    }
    return null;
  },
);
