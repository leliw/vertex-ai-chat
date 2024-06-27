import { Component, ElementRef, EventEmitter, Output, ViewEncapsulation } from '@angular/core';
import { ChatService } from '../chat.service';
import { MatChipsModule } from '@angular/material/chips';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { CommonModule } from '@angular/common';
import { MarkdownPipe } from '../../shared/markdown.pipe';

@Component({
    selector: 'app-chat-view',
    standalone: true,
    encapsulation: ViewEncapsulation.None,
    imports: [CommonModule, MatChipsModule, MatButtonModule, MatIconModule,
        MarkdownPipe
    ],
    templateUrl: './chat-view.component.html',
    styleUrl: './chat-view.component.css'
})
export class ChatViewComponent {
    @Output() editMessageEvent = new EventEmitter<number>();
    @Output() stopTypingEvent = new EventEmitter<void>();
    @Output() cancelGeneratingEvent = new EventEmitter<void>();

    actionButtons?: number = undefined;
    currentAnswer = '';
    currentTypeIndex = 0;

    constructor(public chatService: ChatService, private rootElement: ElementRef) { }

    scrollBottom(): void {
        setTimeout(() => this.rootElement.nativeElement.scrollTop = this.rootElement.nativeElement.scrollHeight, 100);
    }

    startTyping() {
        this.currentAnswer = '';
        this.currentTypeIndex = 0;
        this.typeAnswer();
        this.chatService.isTyping = true;
    }

    addAnswerChunk(chunk: string) {
        this.currentAnswer += chunk;
    }

    stopTyping() {
        // Stop typing
        this.currentTypeIndex = this.currentAnswer.length;
        this.chatService.chat.history[this.chatService.chat.history.length - 1].content = this.currentAnswer;
        this.chatService.waitingForResponse = false;
        this.chatService.isTyping = false;
        this.stopTypingEvent.emit();
    }

    private typeAnswer() {
        // Simulate typing effect
        if (this.currentTypeIndex < this.currentAnswer.length) {
            this.chatService.chat.history[this.chatService.chat.history.length - 1].content += this.currentAnswer[this.currentTypeIndex];
            this.currentTypeIndex++;
            this.scrollBottom();
            setTimeout(() => this.typeAnswer(), 10);
        } else if (this.chatService.waitingForResponse) {
            setTimeout(() => this.typeAnswer(), 10);
        } else {
            this.stopTypingEvent.emit();
            this.chatService.isTyping = false;
        }
    }

    cancelGenerating() {
        // Cancel the current request
        this.stopTyping();
        this.cancelGeneratingEvent.emit();
    }
}
