import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:record/record.dart';
import 'package:just_audio/just_audio.dart';
import 'package:path_provider/path_provider.dart';

// 실제 오디오 처리를 담당하는 서비스 클래스
class AudioService {
  final _record = AudioRecorder();
  final _player = AudioPlayer();

  // 1. 녹음 시작
  Future<void> startRecording() async {
    if (await _record.hasPermission()) {
      final dir = await getTemporaryDirectory();
      final path = '${dir.path}/audio_record_${DateTime.now().millisecondsSinceEpoch}.wav';
      
      await _record.start(
        const RecordConfig(
          encoder: AudioEncoder.wav,
          sampleRate: 16000,
          numChannels: 1,
        ), 
        path: path
      );
    }
  }

  // 2. 녹음 중지 및 파일 경로 반환
  Future<String?> stopRecording() async {
    return await _record.stop();
  }

  // 3. 오디오 재생
  Future<void> playUrl(String url) async {
    try {
      await _player.setUrl(url);
      await _player.play();
    } catch (e) {
      // 재생 실패 처리
    }
  }

  void dispose() {
    _record.dispose();
    _player.dispose();
  }
}

// 의존성 주입을 위한 프로바이더
final audioServiceProvider = Provider((ref) {
  final service = AudioService();
  ref.onDispose(() => service.dispose());
  return service;
});
