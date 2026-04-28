import 'package:flutter/material.dart';

import '../../core/utils.dart';
import '../../models/fairness_report.dart';
import 'widgets/executive_summary_card.dart';
import 'widgets/metric_table.dart';
import 'widgets/recommendation_list.dart';

class ReportViewPage extends StatelessWidget {
  const ReportViewPage({super.key, required this.report});

  final ReportRecord report;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Expanded(
              child: Text(
                'Report ${report.reportId}',
                style: Theme.of(context).textTheme.titleMedium,
                overflow: TextOverflow.ellipsis,
              ),
            ),
            Chip(label: Text(report.mode)),
          ],
        ),
        const SizedBox(height: 8),
        Text(formatDateTime(report.createdAt)),
        const SizedBox(height: 16),
        ExecutiveSummaryCard(report: report),
        const SizedBox(height: 16),
        MetricTable(findings: report.report.findings),
        const SizedBox(height: 16),
        RecommendationList(items: report.report.recommendations),
      ],
    );
  }
}
