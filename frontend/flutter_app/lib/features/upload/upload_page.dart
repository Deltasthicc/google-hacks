import 'package:flutter/material.dart';

import '../../core/utils.dart';
import '../onboarding/onboarding_controller.dart';
import 'widgets/file_preview_card.dart';
import 'widgets/upload_dropzone.dart';

class UploadPage extends StatefulWidget {
  const UploadPage({super.key, required this.controller});

  final AppController controller;

  @override
  State<UploadPage> createState() => _UploadPageState();
}

class _UploadPageState extends State<UploadPage> {
  late final TextEditingController targetController;
  late final TextEditingController predictionController;
  late final TextEditingController sensitiveController;

  @override
  void initState() {
    super.initState();
    targetController = TextEditingController(text: widget.controller.targetColumn);
    predictionController = TextEditingController(text: widget.controller.predictionColumn);
    sensitiveController = TextEditingController(
      text: widget.controller.sensitiveColumns.join(', '),
    );
  }

  @override
  void dispose() {
    targetController.dispose();
    predictionController.dispose();
    sensitiveController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final project = widget.controller.currentProject;
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Upload', style: Theme.of(context).textTheme.headlineMedium),
          const SizedBox(height: 18),
          if (project == null)
            UploadDropzone(
              icon: Icons.folder_open,
              label: 'Create a project before uploading files',
              onPressed: () => widget.controller.selectTab(0),
            )
          else
            Text(project.name, style: Theme.of(context).textTheme.titleMedium),
          const SizedBox(height: 16),
          LayoutBuilder(
            builder: (context, constraints) {
              final twoColumns = constraints.maxWidth >= 880;
              final cards = [
                FilePreviewCard(
                  title: 'Dataset',
                  file: widget.controller.selectedDataset,
                  uploadedLabel: widget.controller.datasetUpload == null
                      ? null
                      : 'Uploaded ${widget.controller.datasetUpload!.uploadId}',
                  onPick: widget.controller.pickDataset,
                  onUpload: widget.controller.uploadDataset,
                ),
                FilePreviewCard(
                  title: 'Policy document',
                  file: widget.controller.selectedPolicy,
                  uploadedLabel: widget.controller.policyUpload == null
                      ? null
                      : 'Uploaded ${widget.controller.policyUpload!.uploadId}',
                  onPick: widget.controller.pickPolicy,
                  onUpload: widget.controller.uploadPolicy,
                ),
              ];
              if (!twoColumns) {
                return Column(
                  children: [
                    for (final card in cards) ...[card, const SizedBox(height: 16)],
                  ],
                );
              }
              return Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Expanded(child: cards[0]),
                  const SizedBox(width: 16),
                  Expanded(child: cards[1]),
                ],
              );
            },
          ),
          const SizedBox(height: 16),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(18),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Audit inputs', style: Theme.of(context).textTheme.titleMedium),
                  const SizedBox(height: 14),
                  Wrap(
                    spacing: 12,
                    runSpacing: 12,
                    children: [
                      SizedBox(
                        width: 220,
                        child: TextField(
                          controller: targetController,
                          decoration: const InputDecoration(labelText: 'Target column'),
                        ),
                      ),
                      SizedBox(
                        width: 220,
                        child: TextField(
                          controller: predictionController,
                          decoration: const InputDecoration(labelText: 'Prediction column'),
                        ),
                      ),
                      SizedBox(
                        width: 260,
                        child: TextField(
                          controller: sensitiveController,
                          decoration: const InputDecoration(labelText: 'Sensitive columns'),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  Wrap(
                    spacing: 12,
                    runSpacing: 12,
                    children: [
                      FilledButton.icon(
                        onPressed: _saveAndRunData,
                        icon: const Icon(Icons.play_arrow),
                        label: const Text('Data audit'),
                      ),
                      FilledButton.icon(
                        onPressed: _saveAndRunModel,
                        icon: const Icon(Icons.model_training),
                        label: const Text('Model audit'),
                      ),
                      OutlinedButton.icon(
                        onPressed: _saveAndRunCounterfactual,
                        icon: const Icon(Icons.compare_arrows),
                        label: const Text('Counterfactuals'),
                      ),
                      OutlinedButton.icon(
                        onPressed: widget.controller.runBenchmarks,
                        icon: const Icon(Icons.language),
                        label: const Text('Benchmarks'),
                      ),
                      OutlinedButton.icon(
                        onPressed: widget.controller.refreshHistory,
                        icon: const Icon(Icons.history),
                        label: const Text('History'),
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
                  Text('Queued work', style: Theme.of(context).textTheme.titleMedium),
                  const SizedBox(height: 8),
                  if (widget.controller.audits.isEmpty)
                    const Text('No audit jobs yet.')
                  else
                    for (final audit in widget.controller.audits)
                      ListTile(
                        contentPadding: EdgeInsets.zero,
                        leading: const Icon(Icons.task_alt),
                        title: Text(titleCase(audit.auditType)),
                        subtitle: Text(audit.auditId),
                        trailing: Text(audit.status),
                      ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  void _saveInputs() {
    widget.controller.setAuditInputs(
      target: targetController.text,
      prediction: predictionController.text,
      sensitive: sensitiveController.text,
    );
  }

  void _saveAndRunData() {
    _saveInputs();
    widget.controller.runDataAudit();
  }

  void _saveAndRunModel() {
    _saveInputs();
    widget.controller.runModelAudit();
  }

  void _saveAndRunCounterfactual() {
    _saveInputs();
    widget.controller.runCounterfactuals();
  }
}
