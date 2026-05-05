class STTResponse {
  final String text;
  final String language;
  final double confidence;

  STTResponse({
    required this.text,
    required this.language,
    required this.confidence,
  });

  factory STTResponse.fromJson(Map<String, dynamic> json) {
    return STTResponse(
      text: json['text'] ?? '',
      language: json['language'] ?? 'ko',
      confidence: (json['confidence'] ?? 0.0).toDouble(),
    );
  }
}

class AgentAction {
  final String type;
  final String action;
  final Map<String, dynamic> params;

  AgentAction({
    required this.type,
    required this.action,
    required this.params,
  });

  factory AgentAction.fromJson(Map<String, dynamic> json) {
    return AgentAction(
      type: json['type'] ?? '',
      action: json['action'] ?? '',
      params: json['params'] ?? {},
    );
  }
}

class AgentResponse {
  final String text;
  final List<AgentAction> actions;
  final String feedback;
  final String? sessionId;

  AgentResponse({
    required this.text,
    required this.actions,
    required this.feedback,
    this.sessionId,
  });

  factory AgentResponse.fromJson(Map<String, dynamic> json) {
    return AgentResponse(
      text: json['text'] ?? '',
      actions: (json['actions'] as List? ?? [])
          .map((a) => AgentAction.fromJson(a))
          .toList(),
      feedback: json['feedback'] ?? '',
      sessionId: json['session_id'],
    );
  }
}
