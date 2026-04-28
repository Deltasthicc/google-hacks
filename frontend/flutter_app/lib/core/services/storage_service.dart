import 'dart:typed_data';

import 'package:file_picker/file_picker.dart';

class PickedUpload {
  const PickedUpload({
    required this.name,
    required this.bytes,
    required this.size,
  });

  final String name;
  final Uint8List bytes;
  final int size;
}

class StorageService {
  Future<PickedUpload?> pickFile({
    required List<String> allowedExtensions,
  }) async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: allowedExtensions,
      withData: true,
    );
    final file = result?.files.single;
    final bytes = file?.bytes;
    if (file == null || bytes == null) {
      return null;
    }
    return PickedUpload(name: file.name, bytes: bytes, size: file.size);
  }
}
