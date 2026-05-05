import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

// 설정 상태를 관리하는 간단한 프로바이더
final backendUrlProvider = StateProvider<String>((ref) => 'http://localhost:8000/api/v1');

class SettingsScreen extends ConsumerWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final backendUrl = ref.watch(backendUrlProvider);
    final controller = TextEditingController(text: backendUrl);

    return Scaffold(
      appBar: AppBar(
        title: const Text('설정'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const Text(
            '서버 설정',
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 16),
          TextField(
            controller: controller,
            decoration: const InputDecoration(
              labelText: '백엔드 API 주소',
              border: OutlineInputBorder(),
              helperText: '예: http://localhost:8000/api/v1',
            ),
            onSubmitted: (value) {
              ref.read(backendUrlProvider.notifier).state = value;
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('서버 주소가 저장되었습니다.')),
              );
            },
          ),
          const SizedBox(height: 32),
          const Text(
            '앱 정보',
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
          ),
          const ListTile(
            title: Text('버전'),
            subtitle: Text('1.0.0 (MVP)'),
          ),
          const ListTile(
            title: Text('개발팀'),
            subtitle: Text('Test-Navi Project Team'),
          ),
        ],
      ),
    );
  }
}
