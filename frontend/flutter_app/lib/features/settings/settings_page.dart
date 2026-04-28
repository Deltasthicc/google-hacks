import 'package:flutter/material.dart';

import '../onboarding/onboarding_controller.dart';

class SettingsPage extends StatefulWidget {
  const SettingsPage({super.key, required this.controller});

  final AppController controller;

  @override
  State<SettingsPage> createState() => _SettingsPageState();
}

class _SettingsPageState extends State<SettingsPage> {
  late final TextEditingController apiController;
  late final TextEditingController tokenController;

  @override
  void initState() {
    super.initState();
    apiController = TextEditingController(text: widget.controller.apiBaseUrl);
    tokenController = TextEditingController(text: widget.controller.authToken);
  }

  @override
  void dispose() {
    apiController.dispose();
    tokenController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Align(
        alignment: Alignment.topLeft,
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 720),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Settings', style: Theme.of(context).textTheme.headlineMedium),
              const SizedBox(height: 18),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(18),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Backend', style: Theme.of(context).textTheme.titleMedium),
                      const SizedBox(height: 14),
                      TextField(
                        controller: apiController,
                        decoration: const InputDecoration(labelText: 'API base URL'),
                      ),
                      const SizedBox(height: 12),
                      TextField(
                        controller: tokenController,
                        decoration: const InputDecoration(labelText: 'Bearer token'),
                      ),
                      const SizedBox(height: 16),
                      Wrap(
                        spacing: 12,
                        runSpacing: 12,
                        children: [
                          FilledButton.icon(
                            onPressed: _save,
                            icon: const Icon(Icons.save_outlined),
                            label: const Text('Save'),
                          ),
                          OutlinedButton.icon(
                            onPressed: () async {
                              _save();
                              await widget.controller.checkHealth();
                            },
                            icon: const Icon(Icons.network_check),
                            label: const Text('Check'),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(18),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Session', style: Theme.of(context).textTheme.titleMedium),
                      const SizedBox(height: 8),
                      _Line(label: 'User', value: widget.controller.auth.currentUser.userId),
                      _Line(label: 'Auth mode', value: widget.controller.auth.currentUser.authMode),
                      _Line(label: 'Project', value: widget.controller.currentProject?.name ?? 'None'),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _save() {
    widget.controller.configure(
      baseUrl: apiController.text,
      token: tokenController.text,
    );
  }
}

class _Line extends StatelessWidget {
  const _Line({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        children: [
          SizedBox(
            width: 96,
            child: Text(label, style: Theme.of(context).textTheme.labelMedium),
          ),
          Expanded(child: Text(value, overflow: TextOverflow.ellipsis)),
        ],
      ),
    );
  }
}
