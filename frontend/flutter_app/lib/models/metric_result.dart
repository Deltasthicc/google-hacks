class MetricResult {
  const MetricResult({
    required this.name,
    required this.value,
    this.threshold,
    this.status = 'unknown',
  });

  final String name;
  final double value;
  final double? threshold;
  final String status;
}
