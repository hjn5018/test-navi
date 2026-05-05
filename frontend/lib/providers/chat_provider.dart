import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/api_client.dart';
import 'audio_provider.dart';

class ChatMessage {
  final String text;
  final bool isUser;
  final DateTime timestamp;

  ChatMessage({required this.text, required this.isUser, required this.timestamp});
}

// API 클라이언트 프로바이더
final apiClientProvider = Provider((ref) => ApiClient());

class ChatNotifier extends StateNotifier<List<ChatMessage>> {
  final Ref _ref;
  bool _isRecording = false;

  ChatNotifier(this._ref) : super([
    ChatMessage(text: "안녕하세요! 무엇을 도와드릴까요?", isUser: false, timestamp: DateTime.now()),
  ]);

  bool get isRecording => _isRecording;

  void toggleRecording() async {
    final audioService = _ref.read(audioServiceProvider);
    final apiClient = _ref.read(apiClientProvider);

    if (!_isRecording) {
      // 1. 녹음 시작
      await audioService.startRecording();
      _isRecording = true;
      state = [...state]; // UI 갱신을 위해 상태 재설정
    } else {
      // 2. 녹음 중지
      _isRecording = false;
      final path = await audioService.stopRecording();
      
      if (path != null) {
        try {
          // 3. STT: 음성을 텍스트로
          final sttResult = await apiClient.transcribe(path);
          _addMessage(sttResult.text, true);

          // 4. Agent: 명령 처리
          final agentResult = await apiClient.processAgent(sttResult.text);
          _addMessage(agentResult.feedback, false);

          // 5. TTS: 응답 음성 재생
          if (agentResult.feedback.isNotEmpty) {
            final taskId = await apiClient.requestTTS(agentResult.feedback);
            final streamUrl = apiClient.getTTSStreamUrl(taskId);
            await audioService.playUrl(streamUrl);
          }
        } catch (e) {
          _addMessage("죄송합니다. 오류가 발생했습니다: $e", false);
        }
      }
    }
    state = [...state];
  }

  void _addMessage(String text, bool isUser) {
    state = [
      ...state,
      ChatMessage(text: text, isUser: isUser, timestamp: DateTime.now()),
    ];
  }
}

final chatProvider = StateNotifierProvider<ChatNotifier, List<ChatMessage>>((ref) {
  return ChatNotifier(ref);
});

// UI 처리를 위한 상태 프로바이더들
final processingProvider = StateProvider<bool>((ref) => false);
final recordingProvider = StateProvider<bool>((ref) => false);
