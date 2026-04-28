import 'package:flutter/material.dart';

class UploadDropzone extends StatelessWidget {
  const UploadDropzone({
    super.key,
    required this.icon,
    required this.label,
    required this.onPressed,
  });

  final IconData icon;
  final String label;
  final VoidCallback onPressed;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      borderRadius: BorderRadius.circular(8),
      onTap: onPressed,
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.all(22),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(8),
          border: Border.all(
            color: Theme.of(context).colorScheme.primary,
            style: BorderStyle.solid,
          ),
          color: Theme.of(context).colorScheme.primary.withAlpha(15),
        ),
        child: Row(
          children: [
            Icon(icon, size: 30),
            const SizedBox(width: 14),
            Expanded(
              child: Text(label, style: Theme.of(context).textTheme.titleMedium),
            ),
            const Icon(Icons.chevron_right),
          ],
        ),
      ),
    );
  }
}
