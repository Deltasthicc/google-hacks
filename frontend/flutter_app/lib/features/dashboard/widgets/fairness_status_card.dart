import 'package:flutter/material.dart';

import '../../../config/theme.dart';

class FairnessStatusCard extends StatelessWidget {
  const FairnessStatusCard({
    super.key,
    required this.auditCount,
    required this.reportCount,
    required this.benchmarkCount,
  });

  final int auditCount;
  final int reportCount;
  final int benchmarkCount;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Status', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 16),
            Wrap(
              spacing: 12,
              runSpacing: 12,
              children: [
                _Stat(label: 'Audits', value: auditCount, color: AppTheme.aqua),
                _Stat(label: 'Reports', value: reportCount, color: AppTheme.leaf),
                _Stat(label: 'Benchmarks', value: benchmarkCount, color: AppTheme.gold),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _Stat extends StatelessWidget {
  const _Stat({
    required this.label,
    required this.value,
    required this.color,
  });

  final String label;
  final int value;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 128,
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: color.withAlpha(31),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withAlpha(89)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('$value', style: Theme.of(context).textTheme.headlineSmall),
          const SizedBox(height: 4),
          Text(label),
        ],
      ),
    );
  }
}
