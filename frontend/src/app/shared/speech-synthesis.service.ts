import { Injectable } from '@angular/core';


@Injectable({
    providedIn: 'root'
})
export class SpeechSynthesisService {

    lang: string = navigator.language || 'en-US';
    synth: any;
    speachQueue: string[] = [];
    begginningOfSpeach = '';
    isSpeaking = false;

    constructor() {
        this.synth = (<any>window).speechSynthesis;
    }

    /**
     * Speaks the given text
     * @param text Text to be spoken
     */
    speech(text: string) {
        this.speachQueue.push(text);
        if (!this.isSpeaking) {
            this.isSpeaking = true;
            this.speakNext();
        }
    }

    stopSpeaking() {
        this.speachQueue = [];
        this.isSpeaking = false;
        this.synth.cancel();
    }

    /**
     * Speaks the given text delivered in chunks.
     * It will split the text by pauses and speak
     * this parts one by one.
     * @param chunk Chunk of text to be spoken
     */
    addChunk(chunk: string) {
        const parts = this.splitBySpeechPause(chunk);
        if (parts[0]) {
            this.speech(this.begginningOfSpeach + parts[0]);
            this.begginningOfSpeach = parts[1];

        } else {
            this.begginningOfSpeach += parts[1];
        }
    }

    /**
     * Ends the current speech - speaks the rest of the text
     */
    endChunks() {
        if (this.begginningOfSpeach) {
            this.speech(this.begginningOfSpeach);
            this.begginningOfSpeach = '';
        }
    }

    /**
     * Split the text by pauses
     * @param text chunk of text
     * @returns list of two strings: first is the part of the text that should be spoken now, the second is the rest of the text
     */
    private splitBySpeechPause(text: string): string[] {
        const delimiters = [",", ".", "\n"];
        if (delimiters.some(delimiter => text.endsWith(delimiter))) {
            return [text, ''];
        }
        let lastDelimiterIndex = -1;
        for (let d of delimiters) {
            const delimiterIndex = text.lastIndexOf(d);
            if (delimiterIndex > lastDelimiterIndex)
                lastDelimiterIndex = delimiterIndex;
        }
        if (lastDelimiterIndex !== -1) {
            return [text.substring(0, lastDelimiterIndex + 1), text.substring(lastDelimiterIndex + 1)];
        }
        return ['', text];
    }

    /**
     * Speaks the next text from the queue
     */
    private speakNext() {
        if (this.speachQueue.length > 0) {
            const msg = new SpeechSynthesisUtterance(this.speachQueue.shift());
            msg.lang = this.lang;
            msg.onend = () => this.speakNext();
            this.synth.speak(msg);
        } else {
            this.isSpeaking = false;
        }
    }
}
