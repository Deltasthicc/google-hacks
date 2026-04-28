import 'package:flutter/material.dart';

import '../../core/widgets/empty_state.dart';
import '../onboarding/onboarding_controller.dart';
import 'report_view_page.dart';
import 'widgets/fairness_chart_card.dart';

class ReportsPage extends StatelessWidget {
  const ReportsPage({super.key, required this.controller});

  final AppController controller;

  @override
  Widget build(BuildContext context) {
    final selected = controller.selectedReport ??
        (controller.reports.isNotEmpty ? controller.reports.first : null);

    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Text('Reports', style: Theme.of(context).textTheme.headlineMedium),
              ),
              Wrap(
                spacing: 10,
                children: [
                  FilledButton.icon(
                    onPressed: controller.audits.isEmpty
                        ? null
                        : () => controller.generateReport(mode: 'executive'),
                    icon: const Icon(Icons.summarize_outlined),
                    label: const Text('Executive'),
                  ),
                  OutlinedButton.icon(
                    onPressed: controller.audits.isEmpty
                        ? null
                        : () => controller.generateReport(mode: 'technical'),
                    icon: const Icon(Icons.table_chart_outlined),
                    label: const Text('Technical'),
                  ),
                ],
              ),
            ],
          ),
          const SizedBox(height: 18),
          FairnessChartCard(
            auditCount: controller.audits.length,
            reportCount: controller.reports.length,
          ),
          const SizedBox(height: 16),
          if (selected == null)
            EmptyState(
              icon: Icons.article_outlined,
              title: 'No reports yet',
              action: 'Go to upload',
              onPressed: () => controller.selectTab(2),
            )
          else
            LayoutBuilder(
              builder: (context, constraints) {
                final wide = constraints.maxWidth >= 980;
                final list = _ReportList(controller: controller);
                final detail = ReportViewPage(report: selected);
                if (!wide) {
                  return Column(
                    children: [
                      list,
                      const SizedBox(height: 16),
                      detail,
                    ],
                  );
                }
                return Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    SizedBox(width: 340, child: list),
                    const SizedBox(width: 16),
                    Expanded(child: detail),
                  ],
                );
              },
            ),
        ],
      ),
    );
  }
}

class _ReportList extends StatelessWidget {
  const _ReportList({required this.controller});

  final AppController controller;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          children: [
            for (final report in controller.reports)
              ListTile(
                selected: report.reportId == controller.selectedReport?.reportId,
                leading: const Icon(Icons.description_outlined),
                title: Text(report.report.title, overflow: TextOverflow.ellipsis),
                subtitle: Text(report.mode),
                onTap: () => controller.selectReport(report),
              ),
          ],
        ),
      ),
    );
  }
}
