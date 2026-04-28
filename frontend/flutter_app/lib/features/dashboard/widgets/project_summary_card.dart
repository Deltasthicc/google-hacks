import 'package:flutter/material.dart';

import '../../../core/utils.dart';
import '../../../models/audit_job.dart';

class ProjectSummaryCard extends StatelessWidget {
  const ProjectSummaryCard({
    super.key,
    required this.project,
    required this.dataset,
    required this.policy,
  });

  final ProjectRecord? project;
  final UploadRecord? dataset;
  final UploadRecord? policy;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Project', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 14),
            _Row(label: 'Name', value: project?.name ?? 'No active project'),
            _Row(label: 'Domain', value: project?.domain ?? 'Unset'),
            _Row(label: 'Created', value: formatDateTime(project?.createdAt)),
            const Divider(height: 26),
            _Row(label: 'Dataset', value: dataset?.filename ?? 'Not uploaded'),
            _Row(label: 'Policy', value: policy?.filename ?? 'Not uploaded'),
          ],
        ),
      ),
    );
  }
}

class _Row extends StatelessWidget {
  const _Row({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        children: [
          SizedBox(
            width: 88,
            child: Text(label, style: Theme.of(context).textTheme.labelMedium),
          ),
          Expanded(child: Text(value, overflow: TextOverflow.ellipsis)),
        ],
      ),
    );
  }
}
