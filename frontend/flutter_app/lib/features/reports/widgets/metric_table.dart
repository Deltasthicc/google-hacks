import 'package:flutter/material.dart';

class MetricTable extends StatelessWidget {
  const MetricTable({super.key, required this.findings});

  final List<Map<String, dynamic>> findings;

  @override
  Widget build(BuildContext context) {
    if (findings.isEmpty) {
      return const Card(
        child: Padding(
          padding: EdgeInsets.all(18),
          child: Text('No metric findings returned yet.'),
        ),
      );
    }

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          child: DataTable(
            columns: const [
              DataColumn(label: Text('Finding')),
              DataColumn(label: Text('Metric')),
              DataColumn(label: Text('Value')),
              DataColumn(label: Text('Severity')),
            ],
            rows: findings
                .map(
                  (finding) => DataRow(
                    cells: [
                      DataCell(Text('${finding['title'] ?? finding['description'] ?? 'Finding'}')),
                      DataCell(Text('${finding['metric_name'] ?? finding['metric'] ?? '-'}')),
                      DataCell(Text('${finding['metric_value'] ?? finding['value'] ?? '-'}')),
                      DataCell(Text('${finding['severity'] ?? '-'}')),
                    ],
                  ),
                )
                .toList(),
          ),
        ),
      ),
    );
  }
}
