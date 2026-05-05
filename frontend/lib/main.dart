import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'presentation/screens/home_screen.dart';

void main() {
  runApp(
    // Riverpod 상태 관리를 위한 루트 위젯
    const ProviderScope(
      child: TestNaviApp(),
    ),
  );
}

class TestNaviApp extends StatelessWidget {
  const TestNaviApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Test-Navi Assistant',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.blueAccent,
          brightness: Brightness.dark,
        ),
        useMaterial3: true,
        // 시각 장애인을 위한 기본 텍스트 테마 (크고 뚜렷하게)
        textTheme: const TextTheme(
          bodyLarge: TextStyle(fontSize: 24, height: 1.5),
          bodyMedium: TextStyle(fontSize: 20, height: 1.5),
          titleLarge: TextStyle(fontSize: 32, fontWeight: FontWeight.bold),
        ),
      ),
      home: const HomeScreen(),
      debugShowCheckedModeBanner: false,
    );
  }
}
