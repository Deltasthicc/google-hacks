import 'package:intl/intl.dart';

String formatDateTime(DateTime? value) {
  if (value == null) {
    return 'Not recorded';
  }
  return DateFormat('dd MMM yyyy, HH:mm').format(value.toLocal());
}

List<String> parseCsvWords(String value) {
  return value
      .split(',')
      .map((item) => item.trim())
      .where((item) => item.isNotEmpty)
      .toList();
}

String titleCase(String value) {
  if (value.isEmpty) {
    return value;
  }
  return value
      .split(RegExp(r'[_\s-]+'))
      .where((part) => part.isNotEmpty)
      .map((part) => '${part[0].toUpperCase()}${part.substring(1).toLowerCase()}')
      .join(' ');
}
