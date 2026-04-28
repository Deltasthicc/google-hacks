import 'package:flutter/material.dart';

import '../onboarding/onboarding_controller.dart';
import 'widgets/fairness_status_card.dart';
import 'widgets/project_summary_card.dart';
import 'widgets/recent_audits_card.dart';

class DashboardPage extends StatelessWidget {
  const DashboardPage({super.key, required this.controller});

  final AppController controller;

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Dashboard', style: Theme.of(context).textTheme.headlineMedium),
          const SizedBox(height: 18),
          LayoutBuilder(
            builder: (context, constraints) {
              final twoColumns = constraints.maxWidth >= 880;
              final cards = [
                ProjectSummaryCard(
                  project: controller.currentProject,
                  dataset: controller.datasetUpload,
                  policy: controller.policyUpload,
                ),
                FairnessStatusCard(
                  auditCount: controller.audits.length,
                  reportCount: controller.reports.length,
                  benchmarkCount: controller.benchmarks.length,
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
          RecentAuditsCard(
            audits: controller.audits,
            onGenerateReport: () => controller.generateReport(),
          ),
        ],
      ),
    );
  }
}
