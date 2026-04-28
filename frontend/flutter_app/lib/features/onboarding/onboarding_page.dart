import 'package:flutter/material.dart';

import '../../core/constants.dart';
import 'onboarding_controller.dart';

class OnboardingPage extends StatefulWidget {
  const OnboardingPage({super.key, required this.controller});

  final AppController controller;

  @override
  State<OnboardingPage> createState() => _OnboardingPageState();
}

class _OnboardingPageState extends State<OnboardingPage> {
  final nameController = TextEditingController(text: 'Lending fairness demo');
  final descriptionController = TextEditingController(
    text: 'Credit approval audit with protected-attribute checks.',
  );
  String domain = demoDomains.first;

  @override
  void dispose() {
    nameController.dispose();
    descriptionController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 960),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Workspace', style: Theme.of(context).textTheme.headlineMedium),
              const SizedBox(height: 18),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(18),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Project setup', style: Theme.of(context).textTheme.titleLarge),
                      const SizedBox(height: 16),
                      TextField(
                        controller: nameController,
                        decoration: const InputDecoration(labelText: 'Project name'),
                      ),
                      const SizedBox(height: 12),
                      DropdownButtonFormField<String>(
                        value: domain,
                        decoration: const InputDecoration(labelText: 'Domain'),
                        items: demoDomains
                            .map(
                              (item) => DropdownMenuItem(
                                value: item,
                                child: Text(item),
                              ),
                            )
                            .toList(),
                        onChanged: (value) {
                          if (value != null) {
                            setState(() => domain = value);
                          }
                        },
                      ),
                      const SizedBox(height: 12),
                      TextField(
                        controller: descriptionController,
                        minLines: 3,
                        maxLines: 4,
                        decoration: const InputDecoration(labelText: 'Description'),
                      ),
                      const SizedBox(height: 18),
                      Wrap(
                        spacing: 12,
                        runSpacing: 12,
                        children: [
                          FilledButton.icon(
                            onPressed: widget.controller.busy
                                ? null
                                : () => widget.controller.createProject(
                                      name: nameController.text,
                                      domain: domain,
                                      description: descriptionController.text,
                                    ),
                            icon: const Icon(Icons.add),
                            label: const Text('Create project'),
                          ),
                          OutlinedButton.icon(
                            onPressed: widget.controller.checkHealth,
                            icon: const Icon(Icons.network_check),
                            label: const Text('Check backend'),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 18),
              if (widget.controller.projects.isNotEmpty)
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(18),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('Projects', style: Theme.of(context).textTheme.titleMedium),
                        const SizedBox(height: 8),
                        for (final project in widget.controller.projects)
                          ListTile(
                            contentPadding: EdgeInsets.zero,
                            leading: const Icon(Icons.folder_outlined),
                            title: Text(project.name),
                            subtitle: Text(project.projectId),
                            trailing: OutlinedButton(
                              onPressed: () => widget.controller.chooseProject(project),
                              child: const Text('Open'),
                            ),
                          ),
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
}
