import 'package:flutter/material.dart';

import '../../../config/theme.dart';

class FairnessChartCard extends StatelessWidget {
  const FairnessChartCard({
    super.key,
    required this.auditCount,
    required this.reportCount,
  });

  final int auditCount;
  final int reportCount;

  @override
  Widget build(BuildContext context) {
    final total = (auditCount + reportCount).clamp(1, 999);
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Activity', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 18),
            _Bar(
              label: 'Audits',
              value: auditCount,
              fraction: auditCount / total,
              color: AppTheme.aqua,
            ),
            const SizedBox(height: 12),
            _Bar(
              label: 'Reports',
              value: reportCount,
              fraction: reportCount / total,
              color: AppTheme.leaf,
            ),
          ],
        ),
      ),
    );
  }
}

class _Bar extends StatelessWidget {
  const _Bar({
    required this.label,
    required this.value,
    required this.fraction,
    required this.color,
  });

  final String label;
  final int value;
  final double fraction;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Expanded(child: Text(label)),
            Text('$value'),
          ],
        ),
        const SizedBox(height: 6),
        ClipRRect(
          borderRadius: BorderRadius.circular(6),
          child: LinearProgressIndicator(
            minHeight: 10,
            value: fraction,
            backgroundColor: color.withAlpha(36),
            valueColor: AlwaysStoppedAnimation<Color>(color),
          ),
        ),
      ],
    );
  }
}
