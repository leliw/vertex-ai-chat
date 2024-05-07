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
    currentAnswer = '';
    currentTypeIndex = 0;

    constructor(private chatService: ChatService) {
        // Get the initial messages from the server
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
        // Send message to the server and process the response synchronously
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
        // Send message to the server and process the response asynchronously
        if (this.newMessage.trim().length > 0) {
            const message = { author: "user", content: this.newMessage }
            this.messages.push(message);
            this.newMessage = '';
            this.waitingForResponse = true;
            this.currentAnswer = '';
            this.currentTypeIndex = 0;
            this.messages.push({ author: "ai", content: "" });
            this.chatService.send_async(message).subscribe({
                next: (chunk) => {
                    this.currentAnswer += chunk;
                    if (this.currentTypeIndex==0)
                        this.typeAnswer();
                },
                complete: () => {
                    this.waitingForResponse = false;
                }
            });
        }
    }
    typeAnswer() {
        // Simulate typing effect
        if (this.currentTypeIndex < this.currentAnswer.length) {
            this.messages[this.messages.length-1].content += this.currentAnswer[this.currentTypeIndex];
            this.currentTypeIndex++;
            setTimeout(() => this.typeAnswer(), 15);
        }
    }

    ngAfterViewChecked(): void {
        // Scroll to the bottom of the chat container
        this.container.nativeElement.scrollTop = this.container.nativeElement.scrollHeight;
    }
}