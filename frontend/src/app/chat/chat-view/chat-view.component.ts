import { Component, ElementRef, EventEmitter, Output } from '@angular/core';
import { ChatService } from '../chat.service';
import { MatChipsModule } from '@angular/material/chips';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { CommonModule } from '@angular/common';
import { MarkdownPipe } from '../../shared/markdown.pipe';

@Component({
    selector: 'app-chat-view',
    standalone: true,
    imports: [CommonModule, MatChipsModule, MatButtonModule, MatIconModule,
        MarkdownPipe
    ],
    templateUrl: './chat-view.component.html',
    styleUrl: './chat-view.component.css'
})
export class ChatViewComponent {
    @Output() editMessageEvent = new EventEmitter<number>();

    actionButtons?: number = undefined;

    constructor(public chatService: ChatService, private rootElement: ElementRef) { }

    scrollBottom(): void {
        // Scroll to the bottom of the chat container
        console.log(this.rootElement);
        setTimeout(() => this.rootElement.nativeElement.scrollTop = this.rootElement.nativeElement.scrollHeight, 100);
    }
}
