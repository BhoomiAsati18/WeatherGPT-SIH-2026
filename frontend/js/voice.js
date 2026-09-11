/**
 * WeatherGPT - Voice Interaction Engine (Web Speech API)
 * Speech-to-Text (STT) and Text-to-Speech (TTS)
 */

class VoiceEngine {
  constructor() {
    this.recognition = null;
    this.isRecording = false;
    this.synth = window.speechSynthesis;
    this.initRecognition();
  }

  initRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      this.recognition = new SpeechRecognition();
      this.recognition.continuous = false;
      this.recognition.interimResults = false;
      this.recognition.lang = 'hi-IN'; // default Hindi/Hinglish
    } else {
      console.warn("Speech recognition not supported in this browser.");
    }
  }

  setLanguage(langCode) {
    if (!this.recognition) return;
    if (langCode === 'hindi') {
      this.recognition.lang = 'hi-IN';
    } else if (langCode === 'english') {
      this.recognition.lang = 'en-IN';
    } else {
      this.recognition.lang = 'hi-IN'; // Hinglish uses hi-IN recognizer
    }
  }

  toggleRecording(btnElement, onResultCallback) {
    if (!this.recognition) {
      alert("Browser Voice Recognition is not supported on this device. Please type your query.");
      return;
    }

    if (this.isRecording) {
      this.recognition.stop();
      this.isRecording = false;
      btnElement.classList.remove('recording');
      return;
    }

    try {
      this.isRecording = true;
      btnElement.classList.add('recording');

      this.recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        this.isRecording = false;
        btnElement.classList.remove('recording');
        if (onResultCallback) onResultCallback(transcript);
      };

      this.recognition.onerror = (event) => {
        console.error("Speech recognition error:", event.error);
        this.isRecording = false;
        btnElement.classList.remove('recording');
      };

      this.recognition.onend = () => {
        this.isRecording = false;
        btnElement.classList.remove('recording');
      };

      this.recognition.start();
    } catch (e) {
      console.error("Failed to start voice recognition:", e);
      this.isRecording = false;
      btnElement.classList.remove('recording');
    }
  }

  speakText(text, lang) {
    if (!this.synth) return;
    this.synth.cancel(); // Stop any ongoing speech

    // Clean markdown symbols from text before speaking
    const cleanText = text.replace(/[*_#`~🚨⚠️💡]/g, '');

    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;

    // Pick best voice
    const voices = this.synth.getVoices();
    if (lang === 'hindi' || lang === 'hinglish') {
      const hiVoice = voices.find(v => v.lang.includes('hi') || v.name.includes('Hindi'));
      if (hiVoice) utterance.voice = hiVoice;
      utterance.lang = 'hi-IN';
    } else {
      const enVoice = voices.find(v => v.lang.includes('en-IN') || v.lang.includes('en'));
      if (enVoice) utterance.voice = enVoice;
      utterance.lang = 'en-IN';
    }

    this.synth.speak(utterance);
  }
}

window.voiceEngine = new VoiceEngine();
