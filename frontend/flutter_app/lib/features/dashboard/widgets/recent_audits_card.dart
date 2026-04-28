import 'package:flutter/material.dart';

import '../../../core/utils.dart';
import '../../../models/audit_job.dart';

class RecentAuditsCard extends StatelessWidget {
  const RecentAuditsCard({
    super.key,
    required this.audits,
    required this.onGenerateReport,
  });

  final List<AuditJob> audits;
  final VoidCallback onGenerateReport;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text('Recent audits', style: Theme.of(context).textTheme.titleMedium),
                ),
                FilledButton.icon(
                  onPressed: audits.isEmpty ? null : onGenerateReport,
                  icon: const Icon(Icons.article_outlined),
                  label: const Text('Report'),
                ),
              ],
            ),
            const SizedBox(height: 12),
            if (audits.isEmpty)
              const Padding(
                padding: EdgeInsets.symmetric(vertical: 24),
                child: Text('No audits yet.'),
              )
            else
              ...audits.take(5).map(
                    (audit) => ListTile(
                      contentPadding: EdgeInsets.zero,
                      leading: const Icon(Icons.fact_check_outlined),
                      title: Text(titleCase(audit.auditType)),
                      subtitle: Text(formatDateTime(audit.createdAt)),
                      trailing: Chip(label: Text(audit.status)),
                    ),
                  ),
          ],
        ),
      ),
    );
  }
}
