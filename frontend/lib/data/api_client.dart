import 'package:dio/dio.dart';
import 'models/api_models.dart';

class ApiClient {
  final Dio _dio;
  
  // 기본 백엔드 주소 (로컬 개발 환경)
  static const String baseUrl = 'http://localhost:8000/api/v1';

  ApiClient() : _dio = Dio(BaseOptions(
    baseUrl: baseUrl,
    connectTimeout: const Duration(seconds: 5),
    receiveTimeout: const Duration(seconds: 15),
  ));

  // 1. STT: 음성 파일을 텍스트로 변환
  Future<STTResponse> transcribe(String filePath) async {
    final formData = FormData.fromMap({
      'file': await MultipartFile.fromFile(filePath, filename: 'audio.wav'),
    });

    final response = await _dio.post('/stt/transcribe', data: formData);
    return STTResponse.fromJson(response.data);
  }

  // 2. Agent: 텍스트 입력에 대한 처리 요청
  Future<AgentResponse> processAgent(String text, {String? sessionId}) async {
    final response = await _dio.post('/agent/process', data: {
      'text': text,
      'session_id': sessionId,
    });
    return AgentResponse.fromJson(response.data);
  }

  // 3. TTS: 텍스트를 음성으로 합성 요청 (task_id 반환)
  Future<String> requestTTS(String text) async {
    final response = await _dio.post('/tts/synthesize', data: {
      'text': text,
    });
    return response.data['task_id'];
  }

  // 4. TTS Stream URL 생성
  String getTTSStreamUrl(String taskId) => '$baseUrl/tts/stream/$taskId';
}
