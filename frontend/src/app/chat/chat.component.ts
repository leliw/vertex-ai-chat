import { AfterViewChecked, Component, ElementRef, OnDestroy, OnInit, ViewChild, ViewEncapsulation } from '@angular/core';
import { ChatService, Message } from '../chat.service';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MarkdownPipe } from '../shared/markdown.pipe';


@Component({
    selector: 'app-chat',
    standalone: true,
    imports: [CommonModule, FormsModule, MatIconModule, MatTooltipModule, MarkdownPipe],
    templateUrl: './chat.component.html',
    styleUrl: './chat.component.css',
    encapsulation: ViewEncapsulation.None,
})
export class ChatComponent implements OnInit, OnDestroy, AfterViewChecked {

    @ViewChild('container') container!: ElementRef;

    messages: Message[] = []
    newMessage = '';
    waitingForResponse = false;
    connected = false;

    constructor(private chatService: ChatService) {
        this.chatService.get().subscribe(messages => this.messages = messages);
    }

    ngOnInit(): void {
        this.chatService.connect();
        this.chatService.connected().subscribe(connected => this.connected = connected);
    }

    ngOnDestroy(): void {
        this.chatService.disconect();
    }

    sendMessage() {
        if (this.newMessage.trim().length > 0) {
            const message = { author: "user", "content": this.newMessage }
            this.messages.push(message);
            this.newMessage = '';
            this.waitingForResponse = true;
            this.chatService.send(message).subscribe(response => {
                this.messages.push(response);
                this.waitingForResponse = false;
            });
        }
    }

    sendMessageAsync() {
        if (this.newMessage.trim().length > 0) {
            const message = { author: "user", content: this.newMessage }
            this.messages.push(message);
            this.newMessage = '';
            this.waitingForResponse = true;
            let response = { author: "ai", content: "" }
            this.messages.push(response);
            this.chatService.send_async(message).subscribe({
                next: (chunk) => {
                    response.content += chunk;
                },
                complete: () => {
                    this.waitingForResponse = false;
                }
            });
        }
    }

    ngAfterViewChecked(): void {
        this.container.nativeElement.scrollTop = this.container.nativeElement.scrollHeight;
    }
}