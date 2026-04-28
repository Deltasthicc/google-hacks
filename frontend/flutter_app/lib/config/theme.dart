import 'package:flutter/material.dart';

class AppTheme {
  static const Color ink = Color(0xFF17211D);
  static const Color leaf = Color(0xFF2F6F4E);
  static const Color aqua = Color(0xFF127C89);
  static const Color gold = Color(0xFFE0A22F);
  static const Color danger = Color(0xFFC64242);
  static const Color paper = Color(0xFFF7F4EE);
  static const Color surface = Color(0xFFFFFFFF);
  static const Color border = Color(0xFFD9DED8);

  static ThemeData light() {
    final scheme = ColorScheme.fromSeed(
      seedColor: leaf,
      brightness: Brightness.light,
      primary: leaf,
      secondary: aqua,
      tertiary: gold,
      error: danger,
      surface: surface,
    );

    return ThemeData(
      useMaterial3: true,
      colorScheme: scheme,
      scaffoldBackgroundColor: paper,
      fontFamily: 'Roboto',
      appBarTheme: const AppBarTheme(
        backgroundColor: paper,
        foregroundColor: ink,
        elevation: 0,
        centerTitle: false,
      ),
      cardTheme: CardThemeData(
        color: surface,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
          side: const BorderSide(color: border),
        ),
        margin: EdgeInsets.zero,
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: surface,
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: const BorderSide(color: border),
        ),
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
          padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 14),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        ),
      ),
    );
  }
}
