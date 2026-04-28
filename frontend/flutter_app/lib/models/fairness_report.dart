class ReportRecord {
  const ReportRecord({
    required this.reportId,
    required this.projectId,
    required this.auditId,
    required this.userId,
    required this.status,
    required this.mode,
    required this.createdAt,
    required this.report,
  });

  factory ReportRecord.fromJson(Map<String, dynamic> json) {
    return ReportRecord(
      reportId: json['report_id'] as String? ?? '',
      projectId: json['project_id'] as String? ?? '',
      auditId: json['audit_id'] as String? ?? '',
      userId: json['user_id'] as String? ?? '',
      status: json['status'] as String? ?? 'generated',
      mode: json['mode'] as String? ?? 'executive',
      createdAt: DateTime.tryParse(json['created_at'] as String? ?? ''),
      report: FairnessReport.fromJson(
        Map<String, dynamic>.from(json['report'] as Map? ?? {}),
      ),
    );
  }

  final String reportId;
  final String projectId;
  final String auditId;
  final String userId;
  final String status;
  final String mode;
  final DateTime? createdAt;
  final FairnessReport report;
}

class FairnessReport {
  const FairnessReport({
    required this.title,
    required this.summary,
    required this.riskLevel,
    required this.findings,
    required this.recommendations,
    required this.raw,
  });

  factory FairnessReport.fromJson(Map<String, dynamic> json) {
    final placeholderFindings = json['findings'] as List?;
    final headlineFindings = json['headline_findings'] as List?;
    final recommendations = json['recommendations'] as List?;

    return FairnessReport(
      title: json['title'] as String? ?? 'NyayaLens Fairness Report',
      summary: json['summary'] as String? ??
          json['plain_english_verdict'] as String? ??
          'Report generated.',
      riskLevel: json['risk_level'] as String? ?? 'pending',
      findings: (headlineFindings ?? placeholderFindings ?? [])
          .map((item) => Map<String, dynamic>.from(item as Map? ?? {}))
          .toList(),
      recommendations: (recommendations ?? [])
          .map((item) {
            if (item is String) {
              return item;
            }
            final map = Map<String, dynamic>.from(item as Map? ?? {});
            return map['action'] as String? ?? map['rationale'] as String? ?? '$map';
          })
          .where((item) => item.isNotEmpty)
          .toList(),
      raw: json,
    );
  }

  final String title;
  final String summary;
  final String riskLevel;
  final List<Map<String, dynamic>> findings;
  final List<String> recommendations;
  final Map<String, dynamic> raw;
}
