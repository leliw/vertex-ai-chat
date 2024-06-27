import { Component, EventEmitter, Input, Output, ViewChild } from '@angular/core';
import { MatButton, MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTooltipModule } from '@angular/material/tooltip';
import { SpeechSynthesisService } from '../speech-synthesis.service';

@Component({
    selector: 'app-speech-recognition-button',
    standalone: true,
    imports: [MatButtonModule, MatIconModule, MatTooltipModule, MatProgressSpinnerModule],
    templateUrl: './speech-recognition-button.component.html',
    styleUrl: './speech-recognition-button.component.css'
})
export class SpeechRecognitionButtonComponent {
    /**
     * Timeout in milliseconds after which the recognition will stop
     */
    @Input() timeout: number = 3000;
    /**
     * Emits transcript of the speech
     */
    @Output() transcriptEvent = new EventEmitter<string>();
    /**
     * Emits when the recognition times out (user ends speaking)
     */
    @Output() timeoutEvent = new EventEmitter<void>();

    @ViewChild("button") button!: MatButton;

    isHearing: boolean = false;
    timeoutId!: any;
    transcript: string = '';
    transcriptEmmited: string = '';
    recognition: any;
    endTime: number | undefined;
    progresPercent: number = 0;


    constructor(public speechSynthesisService: SpeechSynthesisService) {
        const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
        this.recognition = new SpeechRecognition();
        this.recognition.lang = navigator.language || 'en-US';
        this.recognition.continuous = true;
        this.recognition.interimResults = true;
        this.recognition.maxAlternatives = 1;

        // I use setInterval to emit transcriptEvent
        // because SpeechRecognition API isn't Angular component
        // and its events don't trigger Angular change detection
        setInterval(() => {
            if (this.endTime) {
                const period = this.endTime - Date.now();
                this.progresPercent = 100 - (period * 100 / this.timeout);
            } else {
                this.progresPercent = 0;
            }
            if (this.transcript.length > 0 && this.transcriptEmmited != this.transcript) {
                this.transcriptEmmited = this.transcript;
                this.transcriptEvent.emit(this.transcript);
            }
            if (this.transcript.length > 0 && !this.isHearing) {
                this.timeoutEvent.emit();
                this.endTime = undefined;
                this.transcript = '';
                this.transcriptEmmited = '';
            }
        }, 50);
    }

    startRecognition() {
        this.transcript = ''
        this.button._elementRef.nativeElement.blur();

        this.recognition.onresult = (event: any) => {
            let transcript = "";
            for (const sent of event.results)
                transcript += sent[0].transcript;
            this.transcript = transcript;
            if (this.transcript != this.transcriptEmmited) {
                clearTimeout(this.timeoutId);
                this.timeoutId = setTimeout(() => this.recognition.abort(), this.timeout); // 3 seconds
                this.endTime = Date.now() + this.timeout;
            }
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
