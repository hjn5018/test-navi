import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../providers/chat_provider.dart';
import '../../presentation/screens/settings_screen.dart';

class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final messages = ref.watch(chatProvider);
    final notifier = ref.read(chatProvider.notifier);
    final isRecording = ref.watch(chatProvider.notifier).isRecording;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Test-Navi Assistant', semanticsLabel: '테스트 내비 어시스턴트'),
        centerTitle: true,
        actions: [
          IconButton(
            icon: const Icon(Icons.settings, size: 28),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => const SettingsScreen()),
              );
            },
            tooltip: '설정',
          ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: messages.length,
              itemBuilder: (context, index) {
                final msg = messages[index];
                return _ChatBubble(
                  message: msg.text,
                  isUser: msg.isUser,
                );
              },
            ),
          ),
          _RecordingControl(
            isRecording: isRecording,
            onTap: () => notifier.toggleRecording(),
          ),
        ],
      ),
    );
  }
}

class _ChatBubble extends StatelessWidget {
  final String message;
  final bool isUser;

  const _ChatBubble({required this.message, required this.isUser});

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Semantics(
        label: isUser ? '나의 메시지' : '어시스턴트 응답',
        child: Container(
          margin: const EdgeInsets.symmetric(vertical: 8),
          padding: const EdgeInsets.all(20),
          constraints: BoxConstraints(
            maxWidth: MediaQuery.of(context).size.width * 0.8,
          ),
          decoration: BoxDecoration(
            color: isUser ? Colors.blue.shade700 : Colors.grey.shade800,
            borderRadius: BorderRadius.circular(24).copyWith(
              bottomRight: isUser ? const Radius.circular(0) : const Radius.circular(24),
              bottomLeft: isUser ? const Radius.circular(24) : const Radius.circular(0),
            ),
          ),
          child: Text(
            message,
            style: const TextStyle(
              color: Colors.white, 
              fontSize: 20,
              fontWeight: FontWeight.w500
            ),
          ),
        ),
      ),
    );
  }
}

class _RecordingControl extends StatelessWidget {
  final bool isRecording;
  final VoidCallback onTap;

  const _RecordingControl({required this.isRecording, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(32, 16, 32, 48),
      decoration: BoxDecoration(
        color: Colors.black.withAlpha(13), // 0.05 * 255
        borderRadius: const BorderRadius.vertical(top: Radius.circular(32)),
      ),
      child: Column(
        children: [
          Text(
            isRecording ? '듣고 있습니다... (중지하려면 터치)' : '마이크를 터치해 명령하세요',
            style: TextStyle(
              color: isRecording ? Colors.redAccent : Colors.grey.shade400,
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 24),
          GestureDetector(
            onTap: onTap,
            child: Semantics(
              button: true,
              label: isRecording ? '녹음 중지' : '녹음 시작',
              child: Container(
                width: 100,
                height: 100,
                decoration: BoxDecoration(
                  color: isRecording ? Colors.red : Colors.blue,
                  shape: BoxShape.circle,
                  boxShadow: [
                    BoxShadow(
                      color: (isRecording ? Colors.red : Colors.blue).withAlpha(102), // 0.4 * 255
                      spreadRadius: 8,
                      blurRadius: 20,
                    ),
                  ],
                ),
                child: Icon(
                  isRecording ? Icons.stop_rounded : Icons.mic_rounded,
                  color: Colors.white,
                  size: 56,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
