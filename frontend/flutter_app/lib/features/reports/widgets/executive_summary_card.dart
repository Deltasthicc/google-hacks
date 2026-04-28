import 'package:flutter/material.dart';

import '../../../models/fairness_report.dart';

class ExecutiveSummaryCard extends StatelessWidget {
  const ExecutiveSummaryCard({super.key, required this.report});

  final ReportRecord report;

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
                  child: Text(
                    report.report.title,
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                ),
                Chip(label: Text(report.report.riskLevel)),
              ],
            ),
            const SizedBox(height: 12),
            Text(report.report.summary),
          ],
        ),
      ),
    );
  }
}
