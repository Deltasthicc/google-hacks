import 'package:flutter/material.dart';

class RecommendationList extends StatelessWidget {
  const RecommendationList({super.key, required this.items});

  final List<String> items;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Recommendations', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 8),
            if (items.isEmpty)
              const Text('No recommendations returned yet.')
            else
              for (final item in items)
                ListTile(
                  contentPadding: EdgeInsets.zero,
                  leading: const Icon(Icons.check_circle_outline),
                  title: Text(item),
                ),
          ],
        ),
      ),
    );
  }
}
