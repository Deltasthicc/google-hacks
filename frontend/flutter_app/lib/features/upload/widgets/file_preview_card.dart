import 'package:flutter/material.dart';

import '../../../core/services/storage_service.dart';

class FilePreviewCard extends StatelessWidget {
  const FilePreviewCard({
    super.key,
    required this.title,
    required this.file,
    required this.uploadedLabel,
    required this.onPick,
    required this.onUpload,
  });

  final String title;
  final PickedUpload? file;
  final String? uploadedLabel;
  final VoidCallback onPick;
  final VoidCallback onUpload;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title, style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 12),
            ListTile(
              contentPadding: EdgeInsets.zero,
              leading: const Icon(Icons.insert_drive_file_outlined),
              title: Text(file?.name ?? 'No file selected'),
              subtitle: Text(
                uploadedLabel ??
                    (file == null ? 'Waiting for selection' : '${file!.size} bytes'),
              ),
            ),
            const SizedBox(height: 10),
            Wrap(
              spacing: 12,
              runSpacing: 12,
              children: [
                OutlinedButton.icon(
                  onPressed: onPick,
                  icon: const Icon(Icons.attach_file),
                  label: const Text('Choose'),
                ),
                FilledButton.icon(
                  onPressed: file == null ? null : onUpload,
                  icon: const Icon(Icons.cloud_upload_outlined),
                  label: const Text('Upload'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
