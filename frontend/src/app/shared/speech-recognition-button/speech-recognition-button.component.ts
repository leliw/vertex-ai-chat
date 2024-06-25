import { Component, EventEmitter, Output } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';

@Component({
    selector: 'app-speech-recognition-button',
    standalone: true,
    imports: [MatButtonModule, MatIconModule, MatTooltipModule],
    templateUrl: './speech-recognition-button.component.html',
    styleUrl: './speech-recognition-button.component.css'
})
export class SpeechRecognitionButtonComponent {
    @Output() transcriptEvent = new EventEmitter<string>();
    @Output() timeoutEvent = new EventEmitter<void>();

    isHearing: boolean = false;
    timeoutId!: any;
    transcript: string = '';
    transcriptEmmited: string = '';
    recognition: any;

    constructor() {
        const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
        this.recognition = new SpeechRecognition();
        this.recognition.lang = 'pl-PL';
        this.recognition.continuous = true;
        this.recognition.interimResults = true;
        this.recognition.maxAlternatives = 1;

        // I use setInterval to emit transcriptEvent
        // because SpeechRecognition API isn't Angular component
        // and its events don't trigger Angular change detection
        setInterval(() => {
            if (this.transcript.length > 0 && this.transcriptEmmited != this.transcript) {
                this.transcriptEmmited = this.transcript;
                this.transcriptEvent.emit(this.transcript);
            }
            if (this.transcript.length > 0 && !this.isHearing) {
                this.timeoutEvent.emit();
                this.transcript = '';
                this.transcriptEmmited = '';
            }
        }, 100);
    }

    startRecognition() {
        this.transcript = ''
        this.recognition.onresult = (event: any) => {
            clearTimeout(this.timeoutId);
            let transcript = "";
            for (const sent of event.results)
                transcript += sent[0].transcript;
            this.transcript = transcript;
            this.timeoutId = setTimeout(() => this.recognition.abort(), 3000); // 3 seconds
        };

        this.recognition.onerror = (event: any) => {
            this.isHearing = false;
            clearTimeout(this.timeoutId);
        };

        this.recognition.onend = () => {
            this.isHearing = false;
            clearTimeout(this.timeoutId);
        }

        this.recognition.start();
        this.isHearing = true;
    }

    stopRecognition() {
        this.recognition.abort()
    }
}
